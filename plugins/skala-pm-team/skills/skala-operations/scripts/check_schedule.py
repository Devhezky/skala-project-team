#!/usr/bin/env python3
"""
check_schedule.py — deterministic schedule checks for Indonesian work sites.

Rules (IDs are cited by the QA Reviewer):
  SCH-01  Date is a national holiday            → warn (block for meetings)
  SCH-02  Date is cuti bersama                  → warn
  SCH-03  Sunday                                → warn
  SCH-04  Friday prayers 11:30–13:00 local time → block for meetings/calls with a time
  SCH-05  Outside 08:00–17:00 local time        → warn for meetings/calls
  SCH-06  Due date before start date            → block
  SCH-07  Timezone missing for a timed item     → block (ask: WIB, WITA or WIT?)
  SCH-08  Holiday data missing for that year    → warn (cannot verify holidays)

Input JSON: {"items": [{"id": "T-01", "kind": "task"|"meeting"|"call",
                         "date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"?,
                         "time": "HH:MM"?, "end_time": "HH:MM"?, "tz": "WIB"|"WITA"|"WIT"?}]}

Usage:  python3 check_schedule.py items.json        (or "-" for stdin)
        python3 check_schedule.py --demo
Output: JSON with findings per item and an overall verdict (ok / warnings / blocked).
"""

import json
import os
import sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
TZ_OFFSET = {"WIB": 7, "WITA": 8, "WIT": 9}
FRIDAY_PRAYER = ("11:30", "13:00")
OFFICE = ("08:00", "17:00")


def load_holidays():
    with open(os.path.join(HERE, "id_holidays.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    years = {d[:4] for d in data["national"]}
    return data["national"], data["cuti_bersama"], years


def _t(s):
    return datetime.strptime(s, "%H:%M").time()


def overlaps(a1, a2, b1, b2):
    return _t(a1) < _t(b2) and _t(b1) < _t(a2)


def check_item(item, national, cuti, years):
    f = []
    kind = item.get("kind", "task")
    timed = kind in ("meeting", "call") or bool(item.get("time"))
    try:
        d0 = date.fromisoformat(item["date"])
    except (KeyError, ValueError):
        return [{"rule": "SCH-00", "level": "block", "message": "date missing or not YYYY-MM-DD"}]
    d1 = d0
    if item.get("end_date"):
        try:
            d1 = date.fromisoformat(item["end_date"])
        except ValueError:
            f.append({"rule": "SCH-00", "level": "block", "message": "end_date not YYYY-MM-DD"})
        if d1 < d0:
            f.append({"rule": "SCH-06", "level": "block", "message": "end/due date is before start date"})
            d1 = d0

    day = d0
    while day <= d1 and (d1 - d0).days <= 366:
        iso = day.isoformat()
        if iso[:4] not in years:
            f.append({"rule": "SCH-08", "level": "warn", "message": "no holiday data for " + iso[:4] + "; holidays not checked"})
            years = years | {iso[:4]}
        if iso in national:
            f.append({"rule": "SCH-01", "level": "block" if timed else "warn", "date": iso,
                      "message": "national holiday: " + national[iso]})
        elif iso in cuti:
            f.append({"rule": "SCH-02", "level": "warn", "date": iso, "message": "cuti bersama: " + cuti[iso]})
        if day.weekday() == 6:
            f.append({"rule": "SCH-03", "level": "warn", "date": iso, "message": "Sunday"})
        day += timedelta(days=1)

    if timed:
        tz = (item.get("tz") or "").upper()
        if tz not in TZ_OFFSET:
            f.append({"rule": "SCH-07", "level": "block", "message": "timezone missing: ask WIB, WITA or WIT"})
        start = item.get("time")
        end = item.get("end_time")
        if start:
            if not end:
                end = (datetime.strptime(start, "%H:%M") + timedelta(hours=1)).strftime("%H:%M")
            if d0.weekday() == 4 and overlaps(start, end, *FRIDAY_PRAYER):
                f.append({"rule": "SCH-04", "level": "block",
                          "message": "overlaps Friday prayers (11:30–13:00 {}). Suggest 09:00–11:00 or 13:30–16:00".format(tz or "local")})
            if _t(start) < _t(OFFICE[0]) or _t(end) > _t(OFFICE[1]):
                f.append({"rule": "SCH-05", "level": "warn", "message": "outside office hours 08:00–17:00 " + (tz or "local")})
            if tz in TZ_OFFSET:
                base = datetime.combine(d0, _t(start)) - timedelta(hours=TZ_OFFSET[tz])
                item["same_time_in"] = {z: (base + timedelta(hours=o)).strftime("%H:%M") for z, o in TZ_OFFSET.items()}
    return f


def run(data):
    national, cuti, years = load_holidays()
    results, levels = [], set()
    for item in data.get("items", []):
        findings = check_item(item, national, cuti, years)
        levels |= {x["level"] for x in findings}
        results.append({"id": item.get("id"), "kind": item.get("kind", "task"), "findings": findings,
                        "same_time_in": item.get("same_time_in")})
    verdict = "blocked" if "block" in levels else ("warnings" if "warn" in levels else "ok")
    return {"verdict": verdict, "items": results}


DEMO = {"items": [
    {"id": "M-01", "kind": "meeting", "date": "2026-11-06", "time": "12:00", "tz": "WITA"},
    {"id": "T-01", "kind": "task", "date": "2026-12-23", "end_date": "2026-12-28"},
    {"id": "M-02", "kind": "call", "date": "2026-11-09", "time": "10:00"},
]}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--demo":
        data = DEMO
    elif sys.argv[1] == "-":
        data = json.load(sys.stdin)
    else:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
    print(json.dumps(run(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
