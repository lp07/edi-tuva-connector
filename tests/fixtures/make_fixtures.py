#!/usr/bin/env python3
"""Build small conformant 837P and 835 fixtures to exercise the parser.

Two claims:
  CLAIM-A  clean paid, 2 lines, modifiers, 2 diagnoses with line pointers
  CLAIM-B  one line paid with a line-level CO-45 adjustment, one line denied
           (claim status will still be 1; denial shown via PR/CO adjustments and
           a remark code) to exercise adjustment + remark capture
"""

ES = "*"   # element separator
CS = ":"   # component separator
ST = "~"   # segment terminator


def build_isa():
    # 16 ISA elements at fixed widths; component sep is ISA16, terminator follows.
    fields = [
        "ISA",
        "00", " " * 10,        # ISA01, ISA02
        "00", " " * 10,        # ISA03, ISA04
        "ZZ", "SENDER".ljust(15),   # ISA05, ISA06
        "ZZ", "RECEIVER".ljust(15), # ISA07, ISA08
        "250601", "1200",      # ISA09, ISA10
        "^",                   # ISA11 repetition separator (005010)
        "00501", "000000001",  # ISA12, ISA13
        "0", "P",              # ISA14, ISA15
        CS,                    # ISA16 component element separator
    ]
    isa = ES.join(fields) + ST
    assert len(isa) == 106, "ISA must be 106 chars, got %d" % len(isa)
    assert isa[3] == ES and isa[104] == CS and isa[105] == ST
    return isa


def seg(*elements):
    return ES.join(elements) + ST


def build_837():
    out = [build_isa()]
    out.append(seg("GS", "HC", "SENDER", "RECEIVER", "20250601", "1200", "1", "X", "005010X222A1"))
    out.append(seg("ST", "837", "0001", "005010X222A1"))
    out.append(seg("BHT", "0019", "00", "REF123", "20250601", "1200", "CH"))
    # 2000A billing provider
    out.append(seg("HL", "1", "", "20", "1"))
    out.append(seg("NM1", "85", "2", "Riverbend Medical Group", "", "", "", "", "XX", "1234567893"))
    out.append(seg("N3", "100 River Rd"))
    out.append(seg("N4", "Austin", "TX", "78701"))
    # 2000B subscriber
    out.append(seg("HL", "2", "1", "22", "0"))
    out.append(seg("SBR", "P", "18", "GRP001", "", "", "", "", "", "CI"))
    out.append(seg("NM1", "IL", "1", "Doe", "Jane", "", "", "", "MI", "MEM00001"))
    out.append(seg("DMG", "D8", "19850214", "F"))
    out.append(seg("NM1", "PR", "2", "Acme Health Plan", "", "", "", "", "PI", "PAYER01"))

    # ---- CLAIM A ----
    out.append(seg("CLM", "CLAIM-A", "225", "", "", "11:B:1", "Y", "A", "Y", "Y"))
    out.append(seg("HI", "ABK:E119", "ABF:I10"))
    out.append(seg("NM1", "82", "1", "Smith", "John", "", "", "", "XX", "1987654321"))
    out.append(seg("LX", "1"))
    out.append(seg("SV1", "HC:99213:25", "125", "UN", "1", "", "", "1:2"))
    out.append(seg("DTP", "472", "D8", "20250515"))
    out.append(seg("REF", "6R", "A-LINE-1"))
    out.append(seg("LX", "2"))
    out.append(seg("SV1", "HC:93000", "100", "UN", "1", "", "", "1"))
    out.append(seg("DTP", "472", "D8", "20250515"))
    out.append(seg("REF", "6R", "A-LINE-2"))

    # ---- CLAIM B ----
    out.append(seg("CLM", "CLAIM-B", "300", "", "", "11:B:1", "Y", "A", "Y", "Y"))
    out.append(seg("HI", "ABK:M5450"))
    out.append(seg("LX", "1"))
    out.append(seg("SV1", "HC:97110:GP", "150", "UN", "2", "", "", "1"))
    out.append(seg("DTP", "472", "D8", "20250520"))
    out.append(seg("REF", "6R", "B-LINE-1"))
    out.append(seg("LX", "2"))
    out.append(seg("SV1", "HC:97140", "150", "UN", "1", "", "", "1"))
    out.append(seg("DTP", "472", "D8", "20250520"))
    out.append(seg("REF", "6R", "B-LINE-2"))

    out.append(seg("SE", "30", "0001"))
    out.append(seg("GE", "1", "1"))
    out.append(seg("IEA", "1", "000000001"))
    return "\n".join(out) + "\n"


def build_835():
    out = [build_isa()]
    out.append(seg("GS", "HP", "SENDER", "RECEIVER", "20250601", "1200", "1", "X", "005010X221A1"))
    out.append(seg("ST", "835", "0001"))
    out.append(seg("BPR", "I", "330", "C", "ACH", "CCP", "01", "999999999", "DA", "123", "", "", "", "", "", "", "", "20250601"))
    out.append(seg("TRN", "1", "CHK-555000", "1999999999"))
    out.append(seg("N1", "PR", "Acme Health Plan"))
    out.append(seg("N1", "PE", "Riverbend Medical Group", "XX", "1234567893"))
    out.append(seg("LX", "1"))

    # ---- CLAIM A: paid in full, 2 lines ----
    out.append(seg("CLP", "CLAIM-A", "1", "225", "225", "0", "CI", "PAYER-A-001"))
    out.append(seg("NM1", "QC", "1", "Doe", "Jane", "", "", "", "MI", "MEM00001"))
    out.append(seg("SVC", "HC:99213:25", "125", "125", "", "1"))
    out.append(seg("DTM", "472", "20250515"))
    out.append(seg("REF", "6R", "A-LINE-1"))
    out.append(seg("SVC", "HC:93000", "100", "100", "", "1"))
    out.append(seg("DTM", "472", "20250515"))
    out.append(seg("REF", "6R", "A-LINE-2"))

    # ---- CLAIM B: line 1 contractual write-down (CO-45), line 2 denied (PR + remark) ----
    out.append(seg("CLP", "CLAIM-B", "1", "300", "105", "45", "CI", "PAYER-B-002"))
    out.append(seg("NM1", "QC", "1", "Doe", "Jane", "", "", "", "MI", "MEM00001"))
    out.append(seg("SVC", "HC:97110:GP", "150", "105", "", "2"))
    out.append(seg("DTM", "472", "20250520"))
    out.append(seg("CAS", "CO", "45", "45"))
    out.append(seg("REF", "6R", "B-LINE-1"))
    out.append(seg("SVC", "HC:97140", "150", "0", "", "1"))
    out.append(seg("DTM", "472", "20250520"))
    out.append(seg("CAS", "PR", "96", "150"))
    out.append(seg("LQ", "HE", "N130"))
    out.append(seg("REF", "6R", "B-LINE-2"))

    out.append(seg("SE", "28", "0001"))
    out.append(seg("GE", "1", "1"))
    out.append(seg("IEA", "1", "000000001"))
    return "\n".join(out) + "\n"


import os
os.makedirs("sample_data", exist_ok=True)
with open("sample_data/claims_837.txt", "w") as f:
    f.write(build_837())
with open("sample_data/remittance_835.txt", "w") as f:
    f.write(build_835())
print("wrote sample_data/claims_837.txt and sample_data/remittance_835.txt")
