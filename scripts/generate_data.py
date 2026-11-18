"""Generate synthetic Alberta energy operations data for the AISQL hands-on lab.

Structured tables are clean. The three *_RAW tables hold facts (facility,
severity, downtime, cost, penalties, topic) only inside free text, written with
inconsistent aliases and formats. The hidden ground truth is used to compute
expected answers in eval_questions.csv so both agents can be scored.

Usage: python scripts/generate_data.py
"""

import csv
import random
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

random.seed(1125)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "workshop_guide" / "data"
ZIP_NAME = "alberta_energy_data.zip"

# (id, name, code, operator, type, lat, lon, max_capacity_bpd, aer_licence, aliases)
FACILITIES = [
    ("F001", "Scotford Upgrader", "SCTF", "Shell Canada", "upgrader", 53.68, -113.12, 350000, "AER-F-10442",
     ["Scotford Upgrader", "Scotford", "SCTF", "Shell Scotford", "the Fort Saskatchewan upgrader"]),
    ("F002", "Horizon Oil Sands", "HRZN", "Canadian Natural Resources", "extraction", 57.34, -111.80, 250000, "AER-F-20871",
     ["Horizon Oil Sands", "Horizon", "HRZN", "CNRL Horizon", "the Horizon mine"]),
    ("F003", "Kearl Lake Operations", "KRLK", "Imperial Oil", "extraction", 57.38, -111.45, 220000, "AER-F-31256",
     ["Kearl Lake Operations", "Kearl", "KRLK", "Imperial Kearl", "the Kearl site"]),
    ("F004", "Christina Lake SAGD", "CHLK", "Cenovus Energy", "sagd", 54.82, -110.20, 180000, "AER-F-40913",
     ["Christina Lake SAGD", "Christina Lake", "CHLK", "Cenovus CL", "the Christina SAGD plant"]),
    ("F005", "Keystone Terminal Calgary", "KYST", "TC Energy", "pipeline_terminal", 51.08, -114.07, 590000, "AER-F-50377",
     ["Keystone Terminal Calgary", "Keystone Terminal", "KYST", "TC Calgary terminal", "the Calgary terminal"]),
]
FACILITY_WEIGHTS = [26, 24, 20, 18, 12]

# (id, name, operator, product_type, max_throughput_bpd, diameter_inches, year_commissioned)
PIPELINES = [
    ("P001", "Keystone XL", "TC Energy", "crude_oil", 350000, 48, 2001),
    ("P002", "Trans Mountain Expansion", "Trans Mountain Corp", "dilbit", 350000, 24, 2006),
    ("P003", "Enbridge Line 3", "Enbridge", "crude_oil", 1200000, 48, 1995),
    ("P004", "NOVA Gas Transmission", "TC Energy", "natural_gas", 350000, 42, 2003),
    ("P005", "Alliance Pipeline", "Pembina Pipeline", "natural_gas", 1200000, 30, 1999),
    ("P006", "Pembina Peace", "Pembina Pipeline", "dilbit", 830000, 36, 1995),
    ("P007", "TC Mainline", "TC Energy", "crude_oil", 590000, 36, 2015),
    ("P008", "Express Pipeline", "Enbridge", "synthetic_crude", 830000, 24, 2017),
    ("P009", "Milk River Pipeline", "Pembina Pipeline", "synthetic_crude", 830000, 24, 2019),
    ("P010", "Aurora Pipeline", "Canadian Natural Resources", "dilbit", 830000, 42, 1993),
    ("P011", "Cold Lake Pipeline", "Imperial Oil", "dilbit", 350000, 30, 2018),
    ("P012", "Athabasca Pipeline", "Enbridge", "dilbit", 830000, 30, 1992),
    ("P013", "Waupisoo Pipeline", "Enbridge", "crude_oil", 350000, 42, 2016),
    ("P014", "Polaris Pipeline", "Pembina Pipeline", "ngls", 1200000, 24, 1999),
    ("P015", "Horizon Connector", "Canadian Natural Resources", "ngls", 200000, 42, 2011),
    ("P016", "Christina Lateral", "Cenovus Energy", "ngls", 590000, 30, 1993),
    ("P017", "Surmont Pipeline", "Cenovus Energy", "dilbit", 590000, 36, 2024),
    ("P018", "Brintnell Pipeline", "Pembina Pipeline", "dilbit", 500000, 42, 1993),
    ("P019", "Kearl Connector", "Imperial Oil", "ngls", 1200000, 30, 2016),
    ("P020", "Hardisty Terminal Line", "Enbridge", "crude_oil", 200000, 30, 2008),
]
DESTINATIONS = ["Hardisty", "Edmonton", "Sarnia", "Burnaby", "Superior", "Patoka", "Cushing", "Regina", "Montreal", "Lévis"]

START = datetime(2026, 1, 1)
END = datetime(2026, 9, 30)


def rand_date():
    return START + timedelta(seconds=random.randint(0, int((END - START).total_seconds())))


def write_csv(name, rows):
    path = DATA_DIR / name
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


# ---------------------------------------------------------------- structured
def build_structured():
    facilities = [
        {"facility_id": f[0], "facility_name": f[1], "facility_code": f[2], "operator": f[3], "facility_type": f[4],
         "latitude": f[5], "longitude": f[6], "max_capacity_bpd": f[7], "aer_licence": f[8]}
        for f in FACILITIES
    ]
    pipelines = [
        {"pipeline_id": p[0], "pipeline_name": p[1], "operator": p[2], "product_type": p[3],
         "max_throughput_bpd": p[4], "diameter_inches": p[5], "year_commissioned": p[6]}
        for p in PIPELINES
    ]
    shipments = []
    for i in range(400):
        p = random.choice(PIPELINES)
        f = random.choices(FACILITIES, weights=FACILITY_WEIGHTS)[0]
        nominated = random.randint(20, 160) * 500
        shortfall_pct = max(0.0, random.gauss(0.05 if f[0] in ("F002", "F003") else 0.02, 0.04))
        shipments.append({
            "shipment_id": f"SHP{i + 1:04d}",
            "pipeline_id": p[0],
            "facility_id": f[0],
            "destination": random.choice(DESTINATIONS),
            "batch_start_ts": rand_date().strftime("%Y-%m-%d %H:%M:%S"),
            "nominated_barrels": nominated,
            "delivered_barrels": int(round(nominated * (1 - shortfall_pct))),
            "api_gravity": round(random.uniform(19, 39), 1),
        })
    return facilities, pipelines, shipments


# ------------------------------------------------------------- incident text
CATEGORIES = {
    "equipment_failure": [
        "{equip} {eq_id} went down with a {fault} during {op}.",
        "{equip} {eq_id} tripped offline — {fault}.",
        "Breakdown on {equip} {eq_id} ({fault}) while running {op}.",
    ],
    "weather": [
        "{weather} forced a stop on outdoor operations.",
        "Ops curtailed due to {weather}; field crews pulled back per cold-weather protocol.",
        "{weather} rolled through and site work paused.",
    ],
    "safety_injury": [
        "Field operator {injury} while {op}. First aid on scene.",
        "Worker {injury} during {op}; Alberta OHS notified.",
        "Injury reported — a contractor {injury} while {op}.",
    ],
    "environmental": [
        "{spill} observed near the {area} after {op}. Containment deployed.",
        "Release: {spill} reported by the ground patrol; AER notified per Directive 071.",
        "{spill} released to the lease surface during {op}; vac truck called in.",
    ],
    "h2s_release": [
        "H2S alarm at the {area} — readings peaked at {ppm} ppm. Area evacuated.",
        "Sour gas detection in the {area} ({ppm} ppm). Crews mustered and SCBA deployed.",
        "Personal H2S monitor alarmed at {ppm} ppm near the {area}; ESD activated.",
    ],
    "pipeline_integrity": [
        "Inline inspection on the {pipeline} flagged a wall-loss anomaly; line pressure reduced.",
        "Pressure drop on the {pipeline} lateral triggered a controlled shutdown for dig verification.",
        "Cathodic protection survey found a coating defect on the {pipeline}; segment isolated.",
    ],
}
CATEGORY_WEIGHTS = [28, 16, 14, 14, 12, 16]

EQUIPMENT = [("steam generator", "OTSG-{n:02d}"), ("compressor", "K-{n:03d}"), ("produced water pump", "P-{n:03d}"),
             ("haul truck", "HT-{n:03d}"), ("coker drum", "CD-{n:02d}")]
FAULTS = ["seal failure", "bearing overheat", "PLC/controller error", "vibration trip", "boiler tube leak", "damaged power cable"]
OPS = ["a well pad turnaround", "night shift rounds", "tank farm transfers", "a pigging run", "coker startup", "truck loading"]
WEATHER = ["An extreme cold snap (-42°C)", "A spring blizzard", "Wildfire smoke and an evacuation alert", "Freezing rain",
           "A chinook wind event gusting 90 km/h", "Heavy overland flooding"]
INJURIES = ["twisted an ankle", "took a hand laceration", "slipped on ice on the pipe rack stairs",
            "fell from a tank ladder", "suffered a steam burn to the forearm"]
SPILLS = ["A produced water spill (~4 m³)", "Dilbit (~2 m³)", "A glycol leak (~300L)", "A bitumen froth spill (~6 m³)", "Diesel (~500L)"]
AREAS = ["tank farm", "well pad", "central processing facility", "compressor station", "tailings pond"]

SEVERITY_CUES = {
    "low": ["minor", "low impact", "Sev: Low", "no real impact to production", "low severity"],
    "medium": ["moderate impact", "Sev: Medium", "medium severity", "noticeable curtailment"],
    "high": ["serious", "Sev: High", "high severity", "significant production loss", "major curtailment"],
    "critical": ["CRITICAL", "Sev: Critical", "critical severity", "full facility shut-in", "emergency response plan activated"],
}
SEVERITY_DIST = {
    "equipment_failure": [35, 40, 20, 5],
    "weather": [15, 35, 35, 15],
    "safety_injury": [20, 40, 30, 10],
    "environmental": [20, 35, 30, 15],
    "h2s_release": [25, 35, 25, 15],
    "pipeline_integrity": [20, 40, 25, 15],
}
DOWNTIME_RANGE = {"low": (0.5, 2), "medium": (2, 6), "high": (6, 14), "critical": (14, 36)}
COST_RANGE = {"low": (2000, 15000), "medium": (15000, 60000), "high": (60000, 250000), "critical": (250000, 900000)}
REPORTERS = ["Shift Supervisor", "Operations Superintendent", "Control Room Operator", "Field Operator", "HSE Coordinator",
             "Integrity Engineer", "Maintenance Lead"]


def fmt_hours(h):
    style = random.randint(0, 4)
    if style == 0:
        return f"{h:g} hours"
    if style == 1:
        return f"~{h:g} hrs"
    if style == 2:
        return f"approx. {int(round(h * 60))} minutes"
    if style == 3:
        return f"{h:g}h"
    return f"about {h:g} hours"


def fmt_cost(c):
    style = random.randint(0, 3)
    if style == 0:
        return f"${c:,.0f}"
    if style == 1:
        return f"{c / 1000:g}k CAD"
    if style == 2:
        return f"CAD {c:,.0f}"
    return f"roughly ${c / 1000:g}K"


def build_incidents():
    rows, truth = [], []
    for i in range(300):
        cat = random.choices(list(CATEGORIES), weights=CATEGORY_WEIGHTS)[0]
        sev = random.choices(["low", "medium", "high", "critical"], weights=SEVERITY_DIST[cat])[0]
        fac = random.choices(FACILITIES, weights=FACILITY_WEIGHTS)[0]
        downtime = round(random.uniform(*DOWNTIME_RANGE[sev]) * 2) / 2
        cost = round(random.uniform(*COST_RANGE[sev]), -2)
        ts = rand_date()
        equip, eq_fmt = random.choice(EQUIPMENT)
        body = random.choice(CATEGORIES[cat]).format(
            equip=equip, eq_id=eq_fmt.format(n=random.randint(1, 40)), fault=random.choice(FAULTS),
            op=random.choice(OPS), weather=random.choice(WEATHER), injury=random.choice(INJURIES),
            spill=random.choice(SPILLS), area=random.choice(AREAS), ppm=random.randint(12, 140),
            pipeline=random.choice(PIPELINES)[1],
        )
        alias = random.choice(fac[9])
        sev_txt = random.choice(SEVERITY_CUES[sev])
        hrs_txt, cost_txt = fmt_hours(downtime), fmt_cost(cost)
        layout = random.randint(0, 3)
        if layout == 0:
            text = f"[{alias}] {body} Lost {hrs_txt} of production. Est. cost {cost_txt}. Assessed as {sev_txt}."
        elif layout == 1:
            text = (f"Hi team, quick report from {alias}: {body} We were down for {hrs_txt}. "
                    f"Repair/cleanup estimate is {cost_txt}. I'd call it {sev_txt}. Will follow up.")
        elif layout == 2:
            text = f"LOCATION: {alias} | {sev_txt.upper()} | {body} DOWNTIME {hrs_txt}. COST {cost_txt}."
        else:
            text = (f"{body} This happened at {alias} around {ts.strftime('%H:%M')}. "
                    f"Impact: {sev_txt}, {hrs_txt} of downtime, estimated {cost_txt} in costs.")
        rid = f"INC-{i + 1:04d}"
        rows.append({
            "report_id": rid,
            "submitted_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "submitted_by": random.choice(REPORTERS),
            "report_text": text,
        })
        truth.append({"report_id": rid, "facility": fac[1], "category": cat, "severity": sev,
                      "downtime_hours": downtime, "cost_cad": cost, "month": ts.month})
    return rows, truth


# ---------------------------------------------------------- inspection text
FOCUS_AREAS = ["sulphur recovery unit", "well integrity", "tailings pond", "flare stack", "tank farm",
               "pipeline right-of-way", "produced water disposal", "emissions monitoring (CEMS)"]
OUTCOMES = ["compliant", "penalty", "suspension", "corrective_action"]


def build_inspections():
    rows, truth = [], []
    for i in range(120):
        fac = random.choices(FACILITIES, weights=FACILITY_WEIGHTS)[0]
        focus = random.choice(FOCUS_AREAS)
        outcome = random.choices(OUTCOMES, weights=[55, 25, 10, 10])[0]
        penalty = round(random.uniform(1500, 60000), -2) if outcome == "penalty" else 0
        ts = rand_date()
        alias = random.choice(fac[9])
        intro = random.choice([
            f"AER field inspection of the {focus} at {alias}.",
            f"Targeted inspection — {focus} program at {alias}.",
            f"Routine compliance review at {alias}, scope: {focus}.",
        ])
        if outcome == "compliant":
            end = random.choice(["Records and field conditions satisfactory. Compliant, no further action.",
                                 "No deficiencies found; inspection closed as compliant."])
        elif outcome == "penalty":
            end = random.choice([f"Repeat non-compliance with Directive 060 found. Administrative penalty of {fmt_cost(penalty)} issued to the licensee.",
                                 f"Late incident reporting under Directive 071; licensee fined {fmt_cost(penalty)}."])
        elif outcome == "suspension":
            end = random.choice(["High-risk non-compliance identified. Operations at the affected unit suspended pending remediation.",
                                 "Immediate safety concern found. Suspension order issued until repairs are verified."])
        else:
            end = random.choice(["Low-risk deficiencies noted; corrective action plan required within 30 days.",
                                 "Minor non-compliance — licensee to submit a corrective action plan."])
        rid = f"AER-{i + 1:04d}"
        rows.append({"inspection_id": rid, "aer_licence": fac[8], "inspected_at": ts.strftime("%Y-%m-%d"),
                     "inspector_notes": f"{intro} {end}"})
        truth.append({"inspection_id": rid, "facility": fac[1], "focus_area": focus, "outcome": outcome, "penalty_cad": penalty})
    return rows, truth


# --------------------------------------------------------------- email text
EMAIL_TOPICS = {
    "delay": (["Our batch out of {t} has been held for {d} days past the nomination date.", "Apportionment at {t} pushed our barrels again and we missed the cycle."],
              ["Notre lot au départ de {t} est retenu depuis {d} jours après la date de nomination.", "Encore un retard à {t}, notre nomination a été reportée."]),
    "quality": (["The last batch from {t} came in off-spec — BS&W well over tariff limits.", "Sulphur content on our receipt from {t} is higher than the quality certificate."],
                ["Le dernier lot reçu de {t} est hors spécification, trop d'eau et de sédiments.", "La teneur en soufre du lot de {t} dépasse le certificat de qualité."]),
    "billing": (["We were charged tariff at {t} for barrels that were never delivered.", "The invoice from {t} has duplicate storage and tankage fees."],
                ["Des frais de tarif nous ont été facturés à {t} pour des barils jamais livrés.", "La facture de {t} contient des frais de stockage en double."]),
    "documentation": (["Still waiting on batch tickets from {t} — what is missing?", "Need the custody transfer confirmation for our shipment at {t}."],
                      ["Nous attendons toujours les billets de lot de {t} : que manque-t-il?", "Pouvez-vous confirmer le transfert de propriété de notre lot à {t}?"]),
    "compliment": (["Thanks to the team at {t} for getting our batch out ahead of schedule.", "Great work at {t} this week — smooth scheduling and quick tickets."],
                   ["Merci à l'équipe de {t} pour le service rapide.", "Excellent travail à {t} cette semaine."]),
}
TOPIC_WEIGHTS = [35, 15, 20, 18, 12]
CUSTOMERS = ["Irving Oil", "Valero Lévis", "Suncor Montréal Refinery", "Imperial Sarnia", "Shell Sarnia",
             "Parkland Burnaby", "Federated Co-op Regina", "Phillips 66 Trading", "Marathon Petroleum", "BP Products North America"]


def build_emails():
    rows, truth = [], []
    for i in range(150):
        topic = random.choices(list(EMAIL_TOPICS), weights=TOPIC_WEIGHTS)[0]
        fac = random.choices(FACILITIES, weights=FACILITY_WEIGHTS)[0]
        french = random.random() < 0.2
        urgent = topic in ("delay", "quality", "documentation") and random.random() < 0.45
        en, fr = EMAIL_TOPICS[topic]
        body = random.choice(fr if french else en).format(t=random.choice(fac[9]), d=random.randint(2, 9))
        if urgent:
            body += " Ce dossier est URGENT." if french else " This is URGENT — we need an answer today."
        elif topic != "compliment":
            body += " Merci de nous revenir." if french else " Please advise when you can."
        ts = rand_date()
        eid = f"EML-{i + 1:04d}"
        rows.append({"email_id": eid, "received_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                     "from_company": random.choice(CUSTOMERS),
                     "subject": random.choice(["Suivi", "Lot", "Question", "Urgent"] if french else ["Re: batch", "Shipment status", "Question", "Urgent", "Follow-up"]),
                     "body": body})
        truth.append({"email_id": eid, "topic": topic, "facility": fac[1], "language": "fr" if french else "en", "urgent": urgent})
    return rows, truth


# ---------------------------------------------------------------- eval set
def build_eval(inc, insp, eml, shipments):
    def n(x):
        return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.1f}"

    horizon = [r for r in inc if r["facility"] == "Horizon Oil Sands"]
    inc42 = next(r for r in inc if r["report_id"] == "INC-0042")
    equip_hrs = sum(r["downtime_hours"] for r in inc if r["category"] == "equipment_failure")
    hi_by_fac = {}
    for r in inc:
        if r["severity"] in ("high", "critical"):
            hi_by_fac[r["facility"]] = hi_by_fac.get(r["facility"], 0) + 1
    top_hi = max(hi_by_fac, key=hi_by_fac.get)
    env_cost = sum(r["cost_cad"] for r in inc if r["category"] == "environmental")
    weather = [r["downtime_hours"] for r in inc if r["category"] == "weather"]
    pen = [r for r in insp if r["outcome"] == "penalty"]
    urgent_delay = sum(1 for e in eml if e["topic"] == "delay" and e["urgent"])
    french = sum(1 for e in eml if e["language"] == "fr")
    q3_crit = sum(1 for r in inc if r["severity"] == "critical" and r["month"] in (7, 8, 9))
    op_of = {p[0]: p[2] for p in PIPELINES}
    op_ship = {}
    for s in shipments:
        op_ship[op_of[s["pipeline_id"]]] = op_ship.get(op_of[s["pipeline_id"]], 0) + 1
    top_op = max(op_ship, key=op_ship.get)
    kearl = [s for s in shipments if s["facility_id"] == "F003"]
    kearl_short = sum(s["nominated_barrels"] - s["delivered_barrels"] for s in kearl) / len(kearl)

    qs = [
        ("structured", "Which pipeline operator had the most shipments this year?", f"{top_op} ({op_ship[top_op]} shipments)"),
        ("structured", "What is the average delivery shortfall in barrels for shipments from Kearl Lake Operations (nominated minus delivered barrels)?", f"{kearl_short:,.0f} barrels"),
        ("lookup", "Which facility was incident INC-0042 at, and what was its severity?", f"{inc42['facility']}, {inc42['severity']} severity"),
        ("aggregate_text", "How many incidents were reported at Horizon Oil Sands?", f"{len(horizon)} incidents"),
        ("aggregate_text", "What is the total downtime in hours caused by equipment failures across all facilities?", f"{n(equip_hrs)} hours"),
        ("aggregate_text", "Which facility had the most high or critical severity incidents?", f"{top_hi} ({hi_by_fac[top_hi]} incidents)"),
        ("aggregate_text", "What is the total estimated cost of environmental incidents?", f"${n(env_cost)} CAD"),
        ("aggregate_text", "What is the average downtime in hours for weather-related incidents?", f"{sum(weather) / len(weather):.1f} hours"),
        ("aggregate_text", "How many critical severity incidents happened in Q3 (July to September)?", f"{q3_crit} incidents"),
        ("aggregate_text", "How many AER inspections resulted in a penalty, and what was the total penalty amount?", f"{len(pen)} penalties totalling ${n(sum(p['penalty_cad'] for p in pen))} CAD"),
        ("aggregate_text", "How many urgent shipper emails were about shipment delays?", f"{urgent_delay} emails"),
        ("aggregate_text", "How many shipper emails were written in French?", f"{french} emails"),
    ]
    return [{"question_id": f"Q{i + 1:02d}", "question_type": t, "question": q, "expected_answer": a} for i, (t, q, a) in enumerate(qs)]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for old in DATA_DIR.glob("*"):
        old.unlink()
    facilities, pipelines, shipments = build_structured()
    incidents, inc_truth = build_incidents()
    inspections, insp_truth = build_inspections()
    emails, eml_truth = build_emails()
    evals = build_eval(inc_truth, insp_truth, eml_truth, shipments)

    files = [
        write_csv("facilities.csv", facilities),
        write_csv("pipelines.csv", pipelines),
        write_csv("pipeline_shipments.csv", shipments),
        write_csv("incident_reports_raw.csv", incidents),
        write_csv("aer_inspections_raw.csv", inspections),
        write_csv("shipper_emails_raw.csv", emails),
        write_csv("eval_questions.csv", evals),
    ]
    with zipfile.ZipFile(DATA_DIR / ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.name)
    for f in files:
        with f.open(encoding="utf-8") as fh:
            print(f"{f.name}: {sum(1 for _ in fh) - 1} rows")
    for e in evals:
        print(f"{e['question_id']} [{e['question_type']}] {e['question']} -> {e['expected_answer']}")


if __name__ == "__main__":
    main()
