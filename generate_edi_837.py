import json
from pathlib import Path

OUT = Path(__file__).parent / "sample_data"
claims = json.loads((OUT / "claims.json").read_text())

def seg(*p): return "*".join(str(x) for x in p) + "~"

def build(claims, sender="RIVERBENDMED", receiver="CLEARINGHOUSE"):
    ctrl = "000000001"
    L = [
        seg("ISA","00"," "*10,"00"," "*10,"ZZ",sender.ljust(15),"ZZ",receiver.ljust(15),"260101","1200","^","00501",ctrl,"0","P",":"),
        seg("GS","HC",sender,receiver,"20260101","1200","1","X","005010X222A1"),
        seg("ST","837","0001","005010X222A1"),
        seg("BHT","0019","00","0123","20260101","1200","CH"),
        seg("NM1","41","2","RIVERBEND MEDICAL GROUP","","","","","46",sender),
        seg("PER","IC","BILLING DEPT","TE","5555550100"),
        seg("NM1","40","2","CLEARINGHOUSE","","","","","46",receiver),
        seg("HL","1","","20","1"),
        seg("NM1","85","2","RIVERBEND MEDICAL GROUP","","","","","XX","1234567890"),
        seg("N3","100 RIVERBEND WAY"),
        seg("N4","AUSTIN","TX","78701"),
    ]
    hl = 2
    for c in claims:
        L += [
            seg("HL",hl,"1","22","0"),
            seg("SBR","P","18","","","","","","","CI"),
            seg("NM1","IL","1",c["last"],c["first"],"","","","MI",c["member_id"]),
            seg("DMG","D8",c["dob"],c["sex"]),
            seg("NM1","PR","2",c["payer_name"],"","","","","PI",c["payer_id"]),
            seg("CLM",c["claim_id"],f'{c["total"]:.2f}',"","",f'{c["pos"]}:B:1',"Y","A","Y","I"),
            seg("DTP","472","RD8",f'{c["dos"]}-{c["dos"]}'),
        ]
        hi = ["HI", f'ABK:{c["dx"][0]}'] + [f"ABF:{d}" for d in c["dx"][1:]]
        L.append("*".join(hi) + "~")
        L.append(seg("NM1","82","1","PROVIDER","RENDERING","","","","XX",c["rendering_npi"]))
        for i, ln in enumerate(c["lines"], 1):
            sv = f'HC:{ln["proc"]}' + (f':{ln["mod"]}' if ln["mod"] else "")
            L += [seg("LX",i), seg("SV1",sv,f'{ln["charge"]:.2f}',"UN","1","","",i), seg("DTP","472","D8",c["dos"])]
        hl += 1
    L += [seg("SE",len(L)-2,"0001"), seg("GE","1","1"), seg("IEA","1",ctrl)]
    return "\n".join(L)

(OUT/"claims_837.txt").write_text(build(claims))
print(f"Wrote {OUT/'claims_837.txt'}")