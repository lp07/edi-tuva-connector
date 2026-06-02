import json
from pathlib import Path

OUT = Path(__file__).parent / "sample_data"
claims = json.loads((OUT / "claims.json").read_text())

def seg(*p): return "*".join(str(x) for x in p) + "~"

def adjudicate(c, idx):
    mode = ["paid","underpaid","denied","patient_resp","paid"][idx % 5]
    out = []
    for ln in c["lines"]:
        b = ln["charge"]
        if mode == "denied":
            allowed, paid, co, pr, status = 0.0, 0.0, b, 0.0, "4"
        elif mode == "underpaid":
            allowed = round(b*0.55,2); paid = allowed; co = round(b-allowed,2); pr = 0.0; status = "1"
        elif mode == "patient_resp":
            allowed = round(b*0.80,2); pr = 20.0; paid = round(allowed-pr,2); co = round(b-allowed,2); status = "1"
        else:
            allowed = round(b*0.70,2); paid = allowed; co = round(b-allowed,2); pr = 0.0; status = "1"
        out.append({"proc":ln["proc"],"mod":ln["mod"],"billed":b,"allowed":allowed,"paid":paid,"co":co,"pr":pr})
    return status, out

def build(claims, payer_name="BCBS TEXAS", payer_id="987654321", check="CHK20260115001"):
    ctrl = "000000001"
    body, total = [], 0.0
    for idx, c in enumerate(claims):
        status, lines = adjudicate(c, idx)
        cb = sum(l["billed"] for l in lines)
        cp = sum(l["paid"] for l in lines)
        cpr = sum(l["pr"] for l in lines)
        total += cp
        body.append(seg("CLP",c["claim_id"],status,f"{cb:.2f}",f"{cp:.2f}",f"{cpr:.2f}","CI",f'REF{c["claim_id"][-6:]}',"11"))
        body.append(seg("NM1","QC","1",c["last"],c["first"],"","","","MI",c["member_id"]))
        for l in lines:
            sv = f'HC:{l["proc"]}' + (f':{l["mod"]}' if l["mod"] else "")
            body.append(seg("SVC",sv,f'{l["billed"]:.2f}',f'{l["paid"]:.2f}',"","1"))
            body.append(seg("DTM","472",c["dos"]))
            if l["co"] > 0: body.append(seg("CAS","CO","45",f'{l["co"]:.2f}'))
            if l["pr"] > 0: body.append(seg("CAS","PR","3",f'{l["pr"]:.2f}'))
            body.append(seg("AMT","B6",f'{l["allowed"]:.2f}'))
    L = [
        seg("ISA","00"," "*10,"00"," "*10,"ZZ",payer_id.ljust(15),"ZZ","RIVERBENDMED".ljust(15),"260115","0900","^","00501",ctrl,"0","P",":"),
        seg("GS","HP",payer_id,"RIVERBENDMED","20260115","0900","1","X","005010X221A1"),
        seg("ST","835","0001","005010X221A1"),
        seg("BPR","I",f"{total:.2f}","C","ACH","CCP","01","111111111","DA","222222222","","","","","","20260115"),
        seg("TRN","1",check,payer_id),
        seg("DTM","405","20260115"),
        seg("N1","PR",payer_name),
        seg("N1","PE","RIVERBEND MEDICAL GROUP","XX","1234567890"),
        seg("LX","1"),
    ] + body
    L += [seg("SE",len(L)-2,"0001"), seg("GE","1","1"), seg("IEA","1",ctrl)]
    return "\n".join(L)

(OUT/"remittance_835.txt").write_text(build(claims))
print(f"Wrote {OUT/'remittance_835.txt'}")