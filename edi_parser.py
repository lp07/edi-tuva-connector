#!/usr/bin/env python3
"""
edi_parser.py  --  source-faithful EDI X12 parser for the edi-tuva-connector.

Reads a raw 837P (professional claim) file and a raw 835 (remittance) file and
emits two JSON files at NATIVE grain:

    claims_837.json   list of claim objects, each with a nested service_lines[]
    remit_835.json    list of claim-payment objects, each with claim_level
                      adjustments[] and a nested service_lines[] that itself
                      carries line_adjustments[] and remark_codes[]

Both are keyed on the claim id (837 CLM01 == 835 CLP01) so dbt owns the join,
the grain shaping to one row per line, and the adjustments/denials/reversals
logic.

Design rules (deliberate):
  - No type coercion. Every value is the raw string from the segment, money and
    quantities included. Staging casts. This keeps the parser faithful and
    avoids float rounding on dollar amounts.
  - Delimiters are read from the ISA segment, not hardcoded.
  - Diagnosis codes stay claim-level (ordered list). Service lines keep their
    SV1-07 pointers as-is. Pointer-to-code resolution is a mapping step and
    belongs in dbt, not here.

Stdlib only. Python 3.10+.
"""

import argparse
import json
import sys


# ----------------------------------------------------------------------------- 
# Tokenizer
# ----------------------------------------------------------------------------- 

def read_delimiters(raw: str):
    """Derive element, component, repetition separators and segment terminator
    from the ISA segment. ISA is the one fixed-length (106 char) segment, so the
    component separator is at index 104 and the segment terminator at index 105.
    The element separator is always the 4th character of the interchange."""
    raw = raw.lstrip("\ufeff").lstrip()
    if raw[:3] != "ISA":
        raise ValueError(
            "File does not begin with ISA. This parser expects a raw X12 "
            "interchange. Got first 3 chars: %r" % raw[:3]
        )
    if len(raw) < 106:
        raise ValueError("Interchange shorter than a valid ISA segment (106 chars).")
    element_sep = raw[3]
    component_sep = raw[104]
    segment_term = raw[105]
    repetition_sep = raw[82]  # ISA11 in 005010; captured but not relied upon
    return raw, element_sep, component_sep, segment_term, repetition_sep


def tokenize(raw: str, element_sep: str, segment_term: str):
    """Split the interchange into a list of segments, each a list of element
    strings. Whitespace and newlines around a segment terminator are stripped."""
    segments = []
    for seg in raw.split(segment_term):
        seg = seg.strip()
        if not seg:
            continue
        segments.append(seg.split(element_sep))
    return segments


def el(elements, i):
    """Safe element accessor. Returns '' for missing trailing elements."""
    return elements[i] if i < len(elements) else ""


def split_composite(value, component_sep):
    return value.split(component_sep) if value else []


def parse_proc_composite(value, component_sep):
    """SV101 (837) and SVC01 (835) share structure:
    qualifier : procedure : mod1 : mod2 : mod3 : mod4"""
    parts = split_composite(value, component_sep)
    qualifier = parts[0] if len(parts) > 0 else ""
    procedure = parts[1] if len(parts) > 1 else ""
    modifiers = [m for m in parts[2:] if m != ""]
    return {"qualifier": qualifier, "procedure_code": procedure, "modifiers": modifiers}


def parse_cas(elements, component_sep):
    """CAS: group code in CAS01, then up to 6 triplets of
    (reason_code, amount, quantity) starting at CAS02."""
    group = el(elements, 1)
    out = []
    i = 2
    while i < len(elements):
        reason = el(elements, i)
        if reason == "":
            break
        out.append({
            "group_code": group,
            "reason_code": reason,
            "amount": el(elements, i + 1),
            "quantity": el(elements, i + 2),
        })
        i += 3
    return out


# ----------------------------------------------------------------------------- 
# 837P
# ----------------------------------------------------------------------------- 

def parse_837(segments, component_sep):
    claims = []
    st_control = ""
    billing = {}
    subscriber = {}
    payer = {}
    claim = None
    line = None

    def reset_provider_scope():
        nonlocal billing, subscriber, payer
        billing, subscriber, payer = {}, {}, {}

    for s in segments:
        seg_id = s[0]

        if seg_id == "ST":
            if el(s, 1) and el(s, 1) != "837":
                sys.stderr.write(
                    "warning: ST01=%r, expected 837 in the 837 input file\n" % el(s, 1)
                )
            st_control = el(s, 2)
            reset_provider_scope()
            claim = None
            line = None

        elif seg_id == "HL":
            level = el(s, 3)
            if level == "20":          # 2000A billing provider
                reset_provider_scope()
            elif level == "22":        # 2000B subscriber
                subscriber, payer = {}, {}
            claim = None
            line = None

        elif seg_id == "SBR":
            subscriber["payer_responsibility"] = el(s, 1)
            subscriber["group_number"] = el(s, 3)
            subscriber["claim_filing_indicator"] = el(s, 9)

        elif seg_id == "NM1":
            qual = el(s, 1)
            if qual == "85":           # billing provider
                billing["name"] = el(s, 3)
                if el(s, 8) == "XX":
                    billing["npi"] = el(s, 9)
            elif qual == "IL":         # subscriber / insured
                subscriber["last_name"] = el(s, 3)
                subscriber["first_name"] = el(s, 4)
                subscriber["id_qualifier"] = el(s, 8)
                subscriber["member_id"] = el(s, 9)
            elif qual == "PR":         # payer
                payer["name"] = el(s, 3)
                payer["id"] = el(s, 9)
            elif qual == "82":         # rendering provider (claim 2310B or line 2420A)
                npi = el(s, 9) if el(s, 8) == "XX" else ""
                if line is not None:
                    line["rendering_provider_npi"] = npi
                elif claim is not None:
                    claim["rendering_provider_npi"] = npi
            elif qual == "QC" and claim is not None:  # patient (when != subscriber)
                claim["patient_last_name"] = el(s, 3)
                claim["patient_first_name"] = el(s, 4)

        elif seg_id == "DMG":
            # subscriber demographics (no separate patient loop in subscriber=patient case)
            subscriber["dob"] = el(s, 2)
            subscriber["gender"] = el(s, 3)

        elif seg_id == "CLM":
            clm05 = split_composite(el(s, 5), component_sep)
            claim = {
                "st_control_number": st_control,
                "claim_id": el(s, 1),                       # CLM01, join key
                "total_charge": el(s, 2),                   # CLM02
                "place_of_service": clm05[0] if len(clm05) > 0 else "",
                "facility_code_qualifier": clm05[1] if len(clm05) > 1 else "",
                "claim_frequency_code": clm05[2] if len(clm05) > 2 else "",
                "billing_provider": dict(billing),
                "subscriber": dict(subscriber),
                "payer": dict(payer),
                "diagnoses": [],
                "rendering_provider_npi": "",
                "service_lines": [],
            }
            claims.append(claim)
            line = None

        elif seg_id == "HI" and claim is not None:
            for idx in range(1, len(s)):
                comp = split_composite(s[idx], component_sep)
                if not comp or comp[0] == "":
                    continue
                claim["diagnoses"].append({
                    "sequence": str(len(claim["diagnoses"]) + 1),
                    "qualifier": comp[0],
                    "code": comp[1] if len(comp) > 1 else "",
                })

        elif seg_id == "LX" and claim is not None:
            line = {
                "line_sequence": str(len(claim["service_lines"]) + 1),  # position in claim
                "line_number": el(s, 1),                                 # LX01 (source)
                "procedure_code": "",
                "modifiers": [],
                "line_charge": "",
                "unit_type": "",
                "units": "",
                "diagnosis_pointers": [],
                "service_date": "",
                "rendering_provider_npi": "",
                "line_control_number": "",
            }
            claim["service_lines"].append(line)

        elif seg_id == "SV1" and line is not None:
            proc = parse_proc_composite(el(s, 1), component_sep)
            line["procedure_code"] = proc["procedure_code"]
            line["modifiers"] = proc["modifiers"]
            line["line_charge"] = el(s, 2)              # SV102
            line["unit_type"] = el(s, 3)                # SV103
            line["units"] = el(s, 4)                    # SV104
            line["diagnosis_pointers"] = [
                p for p in split_composite(el(s, 7), component_sep) if p != ""
            ]

        elif seg_id == "DTP":
            if el(s, 1) == "472":                       # date of service
                if line is not None:
                    line["service_date"] = el(s, 3)
                elif claim is not None:
                    claim.setdefault("service_date", el(s, 3))

        elif seg_id == "REF":
            if el(s, 1) == "6R" and line is not None:   # line item control number
                line["line_control_number"] = el(s, 2)

        elif seg_id == "SE":
            claim = None
            line = None

    return claims


# ----------------------------------------------------------------------------- 
# 835
# ----------------------------------------------------------------------------- 

def parse_835(segments, component_sep):
    payments = []
    st_control = ""
    bpr = {}
    trace = ""
    payer_name = ""
    payee_name = ""
    claim = None
    line = None

    for s in segments:
        seg_id = s[0]

        if seg_id == "ST":
            if el(s, 1) and el(s, 1) != "835":
                sys.stderr.write(
                    "warning: ST01=%r, expected 835 in the 835 input file\n" % el(s, 1)
                )
            st_control = el(s, 2)
            bpr, trace = {}, ""
            payer_name, payee_name = "", ""
            claim, line = None, None

        elif seg_id == "BPR":
            bpr = {
                "transaction_handling": el(s, 1),
                "total_paid": el(s, 2),                 # BPR02
                "credit_debit": el(s, 3),
                "payment_method": el(s, 4),
            }

        elif seg_id == "TRN":
            trace = el(s, 2)                            # check / EFT trace number

        elif seg_id == "N1":
            if el(s, 1) == "PR":
                payer_name = el(s, 2)
            elif el(s, 1) == "PE":
                payee_name = el(s, 2)

        elif seg_id == "CLP":
            claim = {
                "st_control_number": st_control,
                "trace_number": trace,
                "payer_name": payer_name,
                "payee_name": payee_name,
                "payment_total": bpr.get("total_paid", ""),
                "claim_id": el(s, 1),                   # CLP01, join key
                "claim_status_code": el(s, 2),          # CLP02 (4=denied, 22=reversal)
                "claim_charge": el(s, 3),               # CLP03
                "claim_paid": el(s, 4),                 # CLP04
                "patient_responsibility": el(s, 5),     # CLP05
                "claim_filing_indicator": el(s, 6),     # CLP06
                "payer_claim_control_number": el(s, 7), # CLP07
                "claim_level_adjustments": [],
                "service_lines": [],
            }
            payments.append(claim)
            line = None

        elif seg_id == "CAS":
            adjustments = parse_cas(s, component_sep)
            if line is not None:
                line["line_adjustments"].extend(adjustments)
            elif claim is not None:
                claim["claim_level_adjustments"].extend(adjustments)

        elif seg_id == "NM1" and claim is not None:
            qual = el(s, 1)
            if qual == "QC":
                claim["patient_last_name"] = el(s, 3)
                claim["patient_first_name"] = el(s, 4)
            elif qual == "82":
                claim["rendering_provider_npi"] = el(s, 9) if el(s, 8) == "XX" else ""

        elif seg_id == "SVC" and claim is not None:
            proc = parse_proc_composite(el(s, 1), component_sep)
            line = {
                "line_sequence": str(len(claim["service_lines"]) + 1),  # position in claim
                "procedure_code": proc["procedure_code"],
                "modifiers": proc["modifiers"],
                "line_charge": el(s, 2),                # SVC02
                "line_paid": el(s, 3),                  # SVC03
                "units_paid": el(s, 5),                 # SVC05
                "service_date": "",
                "line_control_number": "",
                "line_adjustments": [],
                "remark_codes": [],
            }
            claim["service_lines"].append(line)

        elif seg_id == "DTM":
            if el(s, 1) == "472" and line is not None:
                line["service_date"] = el(s, 2)

        elif seg_id == "REF":
            if el(s, 1) == "6R" and line is not None:
                line["line_control_number"] = el(s, 2)

        elif seg_id == "LQ" and line is not None:
            if el(s, 1) == "HE":                        # RARC remark code
                line["remark_codes"].append(el(s, 2))

        elif seg_id == "PLB":
            sys.stderr.write(
                "note: PLB (provider-level adjustment) segment present; not "
                "captured by this parser. Flag if your data uses it.\n"
            )

        elif seg_id == "SE":
            claim = None
            line = None

    return payments


# ----------------------------------------------------------------------------- 
# CLI
# ----------------------------------------------------------------------------- 

def parse_file(path, which):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    raw, esep, csep, term, _rep = read_delimiters(raw)
    segments = tokenize(raw, esep, term)
    if which == "837":
        return parse_837(segments, csep)
    return parse_835(segments, csep)


def main():
    ap = argparse.ArgumentParser(description="Source-faithful 837P/835 EDI parser.")
    ap.add_argument("--in-837", default="sample_data/claims_837.txt")
    ap.add_argument("--in-835", default="sample_data/remittance_835.txt")
    ap.add_argument("--out-dir", default="sample_data/parsed")
    args = ap.parse_args()

    import os
    os.makedirs(args.out_dir, exist_ok=True)

    claims = parse_file(args.in_837, "837")
    out_837 = os.path.join(args.out_dir, "claims_837.json")
    with open(out_837, "w", encoding="utf-8") as f:
        json.dump(claims, f, indent=2)
    total_lines_837 = sum(len(c["service_lines"]) for c in claims)
    sys.stderr.write(
        "837: %d claims, %d service lines -> %s\n" % (len(claims), total_lines_837, out_837)
    )

    remits = parse_file(args.in_835, "835")
    out_835 = os.path.join(args.out_dir, "remit_835.json")
    with open(out_835, "w", encoding="utf-8") as f:
        json.dump(remits, f, indent=2)
    total_lines_835 = sum(len(c["service_lines"]) for c in remits)
    sys.stderr.write(
        "835: %d claim payments, %d service lines -> %s\n"
        % (len(remits), total_lines_835, out_835)
    )


if __name__ == "__main__":
    main()
