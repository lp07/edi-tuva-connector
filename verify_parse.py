#!/usr/bin/env python3
"""verify_parse.py -- health check on parsed 837/835 JSON.

Reports field completeness, the line-level join key health, and a few
distributions, so silent empties and broken joins are visible. Run after the
parser. Paste the summary.
"""

import json
import sys
from collections import Counter

P837 = "sample_data/parsed/claims_837.json"
P835 = "sample_data/parsed/remit_835.json"


def load(path):
    with open(path) as f:
        return json.load(f)


def empties(rows, key):
    return sum(1 for r in rows if not r.get(key))


def nested_empties(claims, line_key):
    n = 0
    total = 0
    for c in claims:
        for ln in c.get("service_lines", []):
            total += 1
            v = ln.get(line_key)
            if v in (None, "", []):
                n += 1
    return n, total


def main():
    c837 = load(P837)
    c835 = load(P835)

    print("=" * 60)
    print("837  claims=%d  lines=%d" % (
        len(c837), sum(len(c.get("service_lines", [])) for c in c837)))
    print("-" * 60)
    print("claim-level empties:")
    for k in ["claim_id", "total_charge", "place_of_service"]:
        print("  %-26s %d" % (k, empties(c837, k)))
    print("  %-26s %d" % ("billing_provider.npi",
          sum(1 for c in c837 if not c.get("billing_provider", {}).get("npi"))))
    print("  %-26s %d" % ("subscriber.member_id",
          sum(1 for c in c837 if not c.get("subscriber", {}).get("member_id"))))
    print("  %-26s %d" % ("payer.id",
          sum(1 for c in c837 if not c.get("payer", {}).get("id"))))
    print("  %-26s %d" % ("diagnoses==0",
          sum(1 for c in c837 if not c.get("diagnoses"))))
    print("line-level empties (n_empty / n_lines):")
    for k in ["procedure_code", "line_charge", "units", "diagnosis_pointers",
              "service_date", "line_control_number"]:
        n, t = nested_empties(c837, k)
        print("  %-26s %d / %d" % (k, n, t))
    mods = sum(1 for c in c837 for ln in c["service_lines"] if ln.get("modifiers"))
    print("  lines with >=1 modifier   %d" % mods)

    print("=" * 60)
    print("835  payments=%d  lines=%d" % (
        len(c835), sum(len(c.get("service_lines", [])) for c in c835)))
    print("-" * 60)
    print("claim-level empties:")
    for k in ["claim_id", "claim_status_code", "claim_charge", "claim_paid"]:
        print("  %-26s %d" % (k, empties(c835, k)))
    claim_adj = sum(len(c.get("claim_level_adjustments", [])) for c in c835)
    print("  claim_level_adjustments    %d total" % claim_adj)
    print("line-level empties (n_empty / n_lines):")
    for k in ["procedure_code", "line_charge", "line_paid", "service_date",
              "line_control_number"]:
        n, t = nested_empties(c835, k)
        print("  %-26s %d / %d" % (k, n, t))
    line_adj = sum(len(ln.get("line_adjustments", []))
                   for c in c835 for ln in c["service_lines"])
    remarks = sum(len(ln.get("remark_codes", []))
                  for c in c835 for ln in c["service_lines"])
    print("  line_adjustments           %d total" % line_adj)
    print("  remark_codes               %d total" % remarks)

    print("=" * 60)
    print("JOIN HEALTH")
    print("-" * 60)
    ids837 = {c.get("claim_id") for c in c837}
    ids835 = {c.get("claim_id") for c in c835}
    print("claim_id  837=%d  835=%d  both=%d  837_only=%d  835_only=%d" % (
        len(ids837), len(ids835), len(ids837 & ids835),
        len(ids837 - ids835), len(ids835 - ids837)))
    lc837 = [ln.get("line_control_number") for c in c837 for ln in c["service_lines"]]
    lc835 = [ln.get("line_control_number") for c in c835 for ln in c["service_lines"]]
    set837 = {x for x in lc837 if x}
    set835 = {x for x in lc835 if x}
    print("line_control_number  837_nonempty=%d  835_nonempty=%d  match=%d" % (
        len(set837), len(set835), len(set837 & set835)))
    print("  (if match is 0 or low, lines must be joined by position within claim)")

    # per-claim line-count parity: precondition for positional alignment
    lines837 = {c.get("claim_id"): len(c.get("service_lines", [])) for c in c837}
    lines835 = {c.get("claim_id"): len(c.get("service_lines", [])) for c in c835}
    mismatched = [cid for cid in (ids837 & ids835)
                  if lines837.get(cid) != lines835.get(cid)]
    print("per-claim line-count parity: %d of %d matched claims have EQUAL line counts" % (
        len(ids837 & ids835) - len(mismatched), len(ids837 & ids835)))
    if mismatched:
        print("  MISMATCH (positional join unsafe for these): " + ", ".join(
            "%s 837=%d/835=%d" % (cid, lines837.get(cid), lines835.get(cid))
            for cid in mismatched[:10]))

    print("=" * 60)
    print("DISTRIBUTIONS (835)")
    print("-" * 60)
    print("claim_status_code:", dict(Counter(c.get("claim_status_code") for c in c835)))
    groups = Counter(a["group_code"] for c in c835
                     for ln in c["service_lines"] for a in ln.get("line_adjustments", []))
    groups.update(a["group_code"] for c in c835 for a in c.get("claim_level_adjustments", []))
    print("CAS group_code:", dict(groups))


if __name__ == "__main__":
    main()
