#!/usr/bin/env python3
"""
kurva_s.py - Hitung bobot pekerjaan, progress total, dan deviasi Kurva-S.

Pemakaian:
    python3 kurva_s.py --demo
    python3 kurva_s.py data.json

Format data.json:
{
  "project": "Renovasi Rumah Bpk. Andi",
  "contract_value": 250000000,
  "items": [
    {"name": "Pekerjaan persiapan", "value": 25000000, "progress": 100},
    {"name": "Pekerjaan pondasi",   "value": 75000000, "progress": 90}
  ],
  "planned_cumulative": 40.0
}
"""

import json
import sys

# Ambang deviasi (persen)
THRESHOLDS = [
    (2.0, "AHEAD", "Progress lebih cepat dari rencana"),
    (-2.0, "ON TRACK", "Sesuai rencana"),
    (-5.0, "PERHATIAN", "Cek item penyebab, siapkan tambahan tenaga"),
    (-10.0, "TERLAMBAT", "Susun recovery plan konkret"),
    (float("-inf"), "KRITIS", "Eskalasi ke owner, evaluasi target tanggal"),
]


def rp(value):
    """Format rupiah: Rp1.250.000"""
    return "Rp{:,.0f}".format(value).replace(",", ".")


def pct(value, decimals=1):
    """Format persen dengan koma desimal: 45,0%"""
    return ("{:." + str(decimals) + "f}%").format(value).replace(".", ",")


def status_for(deviation):
    for limit, label, advice in THRESHOLDS:
        if deviation >= limit:
            return label, advice
    return "KRITIS", "Eskalasi ke owner"


def compute(data):
    items = data.get("items", [])
    if not items:
        raise ValueError("Daftar 'items' kosong.")

    total_value = sum(float(i.get("value", 0)) for i in items)
    if total_value <= 0:
        raise ValueError("Total nilai item harus lebih besar dari 0.")

    rows = []
    progress_total = 0.0
    for item in items:
        value = float(item.get("value", 0))
        progress = float(item.get("progress", 0))
        weight = value / total_value * 100
        contribution = weight * progress / 100
        progress_total += contribution
        rows.append(
            {
                "name": item.get("name", "(tanpa nama)"),
                "value": value,
                "progress": progress,
                "weight": weight,
                "contribution": contribution,
            }
        )

    contract_value = data.get("contract_value")
    earned_value = None
    if contract_value:
        earned_value = progress_total / 100 * float(contract_value)

    planned = data.get("planned_cumulative")
    deviation = None
    status = None
    advice = None
    if planned is not None:
        deviation = progress_total - float(planned)
        status, advice = status_for(deviation)

    return {
        "rows": rows,
        "total_value": total_value,
        "progress_total": progress_total,
        "earned_value": earned_value,
        "contract_value": contract_value,
        "planned": planned,
        "deviation": deviation,
        "status": status,
        "advice": advice,
    }


def render(data, result):
    out = []
    title = data.get("project", "(tanpa nama proyek)")
    out.append("")
    out.append("PROGRESS PROYEK — " + title)
    out.append("=" * 78)
    out.append(
        "{:<34} {:>15} {:>8} {:>9} {:>10}".format(
            "Item pekerjaan", "Nilai", "Bobot", "Progress", "Kontribusi"
        )
    )
    out.append("-" * 78)
    for row in result["rows"]:
        name = row["name"][:34]
        out.append(
            "{:<34} {:>15} {:>8} {:>9} {:>10}".format(
                name,
                rp(row["value"]),
                pct(row["weight"]),
                "{:.0f}%".format(row["progress"]),
                pct(row["contribution"]),
            )
        )
    out.append("-" * 78)
    out.append(
        "{:<34} {:>15} {:>8} {:>9} {:>10}".format(
            "TOTAL",
            rp(result["total_value"]),
            pct(sum(r["weight"] for r in result["rows"])),
            "—",
            pct(result["progress_total"]),
        )
    )
    out.append("")

    # Pemeriksaan bobot
    weight_sum = sum(r["weight"] for r in result["rows"])
    if abs(weight_sum - 100.0) > 0.05:
        out.append(
            "PERINGATAN: total bobot {:.2f}% (seharusnya 100,0%). "
            "Periksa item yang hilang atau nilai yang salah.".format(weight_sum).replace(".", ",")
        )

    if result["contract_value"]:
        out.append(
            "Nilai kontrak      : {}".format(rp(float(result["contract_value"])))
        )
        out.append(
            "Nilai progress     : {}".format(rp(result["earned_value"]))
        )

    out.append("")
    out.append("PROGRESS TOTAL     : {}".format(pct(result["progress_total"])))

    if result["planned"] is not None:
        out.append("RENCANA KUMULATIF  : {}".format(pct(float(result["planned"]))))
        sign = "+" if result["deviation"] >= 0 else "−"
        out.append(
            "DEVIASI            : {}{}".format(sign, pct(abs(result["deviation"])))
        )
        out.append("STATUS             : {}".format(result["status"]))
        out.append("TINDAKAN           : {}".format(result["advice"]))
        out.append("")

        # Item yang tertinggal jauh dari rencana itemnya
        lagging = [
            r for r in result["rows"] if r["progress"] < 100 and r["weight"] >= 10
        ]
        if lagging:
            out.append("Item berbobot besar yang belum selesai:")
            for r in sorted(lagging, key=lambda x: -x["weight"]):
                out.append(
                    "  - {} (bobot {}) masih {:.0f}%".format(
                        r["name"], pct(r["weight"]), r["progress"]
                    )
                )
            out.append("")
    else:
        out.append(
            "RENCANA KUMULATIF  : [kosong] — deviasi belum bisa dihitung. "
            "Isi 'planned_cumulative' untuk membandingkan dengan Kurva-S rencana."
        )
        out.append("")

    out.append(
        "Catatan: progress fisik berdasarkan laporan pelaksana lapangan, "
        "bukan hasil opname bersama klien."
    )
    out.append("")
    return "\n".join(out)


DEMO = {
    "project": "Renovasi Rumah Bpk. Andi — 2026",
    "contract_value": 250000000,
    "planned_cumulative": 40.0,
    "items": [
        {"name": "Pekerjaan persiapan", "value": 25000000, "progress": 100},
        {"name": "Pekerjaan pondasi", "value": 75000000, "progress": 90},
        {"name": "Pekerjaan dinding", "value": 100000000, "progress": 20},
        {"name": "Pekerjaan finishing", "value": 50000000, "progress": 0},
    ],
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]
    if arg in ("--demo", "-d"):
        data = DEMO
    else:
        with open(arg, "r", encoding="utf-8") as f:
            data = json.load(f)

    try:
        result = compute(data)
    except ValueError as e:
        print("ERROR: {}".format(e))
        sys.exit(1)

    print(render(data, result))


if __name__ == "__main__":
    main()
