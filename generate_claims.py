import json, random
from pathlib import Path
from datetime import date, timedelta

OUT = Path(__file__).parent / "sample_data"
OUT.mkdir(exist_ok=True)

PAYERS = [("BCBS TEXAS","987654321"),("AETNA","60054"),("CIGNA","62308"),("HUMANA","61101")]
PROCEDURES = [("99213",150.0),("99214",200.0),("93000",100.0),("90837",250.0),("80053",45.0),("85025",35.0)]
DIAGNOSES = ["Z1100","E1190","I10","J069","M5450","K2110"]
MODIFIERS = ["25","59","","",""]
FIRST = ["JOHN","MARIA","DAVID","SARAH","JAMES","LINDA","ROBERT","EMMA"]
LAST = ["SMITH","JOHNSON","WILLIAMS","BROWN","JONES","GARCIA","MILLER","DAVIS"]

def make_claims(n=5):
    out = []
    for i in range(1, n+1):
        payer_name, payer_id = random.choice(PAYERS)
        nlines = random.randint(1,3)
        lines, total = [], 0.0
        for _ in range(nlines):
            proc, charge = random.choice(PROCEDURES)
            lines.append({"proc": proc, "charge": charge, "mod": random.choice(MODIFIERS)})
            total += charge
        dxn = random.randint(1,2)
        out.append({
            "claim_id": f"CLM{i:06d}",
            "last": random.choice(LAST), "first": random.choice(FIRST),
            "member_id": f"MBR{random.randint(10000000,99999999)}",
            "dob": "19850101", "sex": random.choice(["M","F"]),
            "payer_name": payer_name, "payer_id": payer_id, "pos": "11",
            "dos": (date(2026,1,1)+timedelta(days=random.randint(0,120))).strftime("%Y%m%d"),
            "dx": random.sample(DIAGNOSES, dxn),
            "rendering_npi": str(random.randint(1000000000,1999999999)),
            "lines": lines, "total": round(total,2),
        })
    return out

if __name__ == "__main__":
    random.seed(42)
    claims = make_claims(5)
    (OUT/"claims.json").write_text(json.dumps(claims, indent=2))
    print(f"Wrote {OUT/'claims.json'}")
    print(f"{len(claims)} claims, {sum(len(c['lines']) for c in claims)} lines")