#!/usr/bin/env python3
"""
buat_excel.py - Membuat workbook Excel setara fitur inti Skala Pro.

Dipakai untuk user yang belum punya akun Skala. Isinya bukan tabel mati:
semua bobot, kontribusi, total, progress, dan deviasi memakai formula asli,
jadi tetap hidup saat diisi.

Sheet yang dihasilkan:
    1. Proyek       Data master proyek
    2. RAB          Item pekerjaan + bobot otomatis + progress
    3. Pengeluaran  Pencatatan biaya, total otomatis, dropdown kategori
    4. Progress     Rekap progress total + tabel & grafik Kurva-S
    5. Tugas        Pembagian tugas dengan PIC tunggal
    6. Panduan      Cara pakai singkat

Contoh:
    python3 bin/buat_excel.py
    python3 bin/buat_excel.py --nama-proyek "Renovasi Rumah Bpk. Andi" --nilai-kontrak 250000000
    python3 bin/buat_excel.py --kosong --output /tmp/template.xlsx

Butuh openpyxl:  pip install openpyxl
"""

import argparse
import os
import sys
from datetime import date, datetime, timedelta

try:
    from openpyxl import Workbook
    from openpyxl.chart import LineChart, Reference
    from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    print("openpyxl belum terpasang. Jalankan:")
    print("  pip install openpyxl")
    sys.exit(1)

# --- Palet ---------------------------------------------------------------
HIJAU = "1F6F4A"
HIJAU_MUDA = "E8F3ED"
ABU = "F2F4F5"
KUNING = "FFF4D6"
MERAH_MUDA = "FBE3E1"

JUDUL = Font(bold=True, color="FFFFFF", size=11)
TEBAL = Font(bold=True)
KECIL = Font(size=9, color="5A6B63")

BORDER = Border(*[Side(style="thin", color="D5DDD8")] * 4)

RP = '"Rp"#,##0'
PERSEN = '0.0"%"'
TANGGAL = "DD/MM/YYYY"


def siapkan_sheet(ws, judul, lebar, baris_header=3):
    ws.sheet_view.showGridLines = False
    ws["A1"] = judul
    ws["A1"].font = Font(bold=True, size=14, color=HIJAU)
    ws.row_dimensions[1].height = 26
    for i, w in enumerate(lebar, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A{}".format(baris_header + 1)


def header(ws, baris, kolom):
    for i, teks in enumerate(kolom, start=1):
        c = ws.cell(row=baris, column=i, value=teks)
        c.font = JUDUL
        c.fill = PatternFill("solid", fgColor=HIJAU)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[baris].height = 30


# --- Data contoh ---------------------------------------------------------
CONTOH_RAB = [
    ("Pekerjaan persiapan", 25000000, 100),
    ("Pekerjaan pondasi", 75000000, 90),
    ("Pekerjaan dinding & partisi", 100000000, 20),
    ("Pekerjaan finishing", 50000000, 0),
]

CONTOH_PENGELUARAN = [
    (date(2026, 10, 18), "SJ-1021", "Toko Bangunan Sinar Jaya", "Penggunaan Bahan", "Semen", 20, "sak", 68000, "Transfer", "Lunas", "Pekerjaan dinding & partisi", ""),
    (date(2026, 10, 18), "SJ-1021", "Toko Bangunan Sinar Jaya", "Penggunaan Bahan", "Pasir", 1, "pick up", 850000, "Transfer", "Lunas", "Pekerjaan dinding & partisi", ""),
    (date(2026, 10, 18), "SJ-1021", "Toko Bangunan Sinar Jaya", "Transport", "Ongkir material", 1, "trip", 150000, "Transfer", "Lunas", "Pekerjaan dinding & partisi", "Sebaiknya digabung ke harga material"),
    (date(2026, 10, 19), "-", "Mandor Sukirman", "Gaji Karyawan", "Kasbon Sukirman", 5, "hari", 1000000, "Kasbon", "Lunas", "Pekerjaan dinding & partisi", ""),
]

CONTOH_TUGAS = [
    ("T-01", "Pasang rangka hollow plafon area ruang tamu & dapur", "Plafon", "Adi", date(2026, 10, 23), date(2026, 10, 25), "-", "Pekerjaan finishing", "Rangka level, jarak 60 cm, tidak bergetar", "Belum mulai"),
    ("T-02", "Pasang papan gypsum + compound", "Plafon", "Adi", date(2026, 10, 26), date(2026, 10, 28), "T-01", "Pekerjaan finishing", "Sambungan rapat, tidak ada retak rambut", "Belum mulai"),
    ("T-03", "Screed lantai area servis", "Lantai & Dinding", "Sukirman", date(2026, 10, 23), date(2026, 10, 25), "-", "Pekerjaan dinding & partisi", "Permukaan rata, kemiringan ke floor drain", "Belum mulai"),
    ("T-04", "Pasang keramik lantai 60x60", "Lantai & Dinding", "Sukirman", date(2026, 10, 27), date(2026, 10, 31), "T-03", "Pekerjaan finishing", "Nat konsisten, kopong < 5%", "Belum mulai"),
]

CONTOH_RENCANA = [
    ("Minggu 1", 6.0), ("Minggu 2", 12.0), ("Minggu 3", 22.0), ("Minggu 4", 22.0),
    ("Minggu 5", 15.0), ("Minggu 6", 11.0), ("Minggu 7", 7.0), ("Minggu 8", 4.0), ("Minggu 9", 1.0),
]


def buat(args):
    kosong = args.kosong
    nama = args.nama_proyek or ("(isi nama proyek)" if kosong else "Renovasi Rumah Bpk. Andi — 2026")
    nama = nama[:200]
    nilai = args.nilai_kontrak if args.nilai_kontrak else (0 if kosong else 250000000)

    wb = Workbook()

    # =========================================================== Sheet Proyek
    ws = wb.active
    ws.title = "Proyek"
    siapkan_sheet(ws, "DATA PROYEK", [30, 46, 34], baris_header=2)
    ws["A2"] = "Isi kolom B. Nilai di sini dipakai sheet lain."
    ws["A2"].font = KECIL

    baris_proyek = [
        ("Nama proyek", nama),
        ("Jenis", "Renovasi interior"),
        ("Klien", "Bpk. Andi Wijaya"),
        ("Lokasi", "Jl. Melati No. 12, Bandung"),
        ("Nilai kontrak (Rp)", nilai),
        ("Tanggal mulai", date(2026, 10, 23)),
        ("Tanggal selesai", date(2026, 12, 20)),
        ("Termin", "DP 30% · T1 25% · T2 25% · Retensi 20%"),
        ("Mandor", "Sukirman"),
        ("Admin", "(nama admin)"),
    ]
    for i, (label, value) in enumerate(baris_proyek, start=3):
        ws.cell(row=i, column=1, value=label).font = TEBAL
        c = ws.cell(row=i, column=2, value=value)
        if isinstance(value, str):
            c.data_type = "s"  # user text is never a formula (blocks =HYPERLINK/=cmd injection)
        c.border = BORDER
        c.alignment = Alignment(vertical="center")
        if label == "Nilai kontrak (Rp)":
            c.number_format = RP
        if isinstance(value, date):
            c.number_format = TANGGAL

    # Catatan
    ws["A15"] = "Catatan penting"
    ws["A15"].font = Font(bold=True, color=HIJAU)
    catatan = [
        "RAB adalah tulang punggung. Setiap pengeluaran dan progress harus menempel ke item RAB,",
        "kalau tidak, kolom biaya dan Kurva-S tidak bisa menunjukkan pekerjaan mana yang bocor.",
        "",
        "Urutan pengisian yang benar:",
        "1. Sheet Proyek   → data master",
        "2. Sheet RAB      → item pekerjaan + nilai (bobot terhitung otomatis)",
        "3. Sheet Progress → isi bobot rencana per minggu (harus total 100%)",
        "4. Sheet Tugas    → pembagian tugas harian",
        "5. Sheet Pengeluaran → isi setiap hari saat nota masuk",
    ]
    for i, teks in enumerate(catatan, start=16):
        ws.cell(row=i, column=1, value=teks).font = KECIL

    # ============================================================== Sheet RAB
    ws = wb.create_sheet("RAB")
    siapkan_sheet(ws, "RAB — ITEM PEKERJAAN & BOBOT", [6, 42, 18, 12, 12, 14, 40])
    header(ws, 3, ["No", "Item pekerjaan", "Nilai (Rp)", "Bobot (%)", "Progress (%)", "Kontribusi (%)", "Catatan"])

    data_rab = [] if kosong else CONTOH_RAB
    baris_awal = 4
    baris_total = baris_awal + max(len(data_rab), 12)
    for i in range(baris_awal, baris_total):
        idx = i - baris_awal
        ws.cell(row=i, column=1, value=idx + 1).alignment = Alignment(horizontal="center")
        if idx < len(data_rab):
            nama_item, nilai_item, progress_item = data_rab[idx]
            ws.cell(row=i, column=2, value=nama_item)
            ws.cell(row=i, column=3, value=nilai_item).number_format = RP
            ws.cell(row=i, column=5, value=progress_item).number_format = PERSEN
        else:
            ws.cell(row=i, column=3).number_format = RP
            ws.cell(row=i, column=5).number_format = PERSEN
        ws.cell(row=i, column=4, value="=IF($C${0}=0,0,C{1}/$C${0}*100)".format(baris_total, i)).number_format = PERSEN
        ws.cell(row=i, column=6, value="=IF(OR(D{0}=\"\",E{0}=\"\"),0,D{0}*E{0}/100)".format(i)).number_format = PERSEN
        for col in range(1, 8):
            ws.cell(row=i, column=col).border = BORDER
        ws.cell(row=i, column=5).fill = PatternFill("solid", fgColor=KUNING)

    # Baris total
    ws.cell(row=baris_total, column=2, value="TOTAL").font = TEBAL
    ws.cell(row=baris_total, column=3, value="=SUM(C{}:C{})".format(baris_awal, baris_total - 1)).number_format = RP
    ws.cell(row=baris_total, column=4, value="=SUM(D{}:D{})".format(baris_awal, baris_total - 1)).number_format = PERSEN
    ws.cell(row=baris_total, column=6, value="=SUM(F{}:F{})".format(baris_awal, baris_total - 1)).number_format = PERSEN
    for col in range(1, 8):
        c = ws.cell(row=baris_total, column=col)
        c.font = TEBAL
        c.fill = PatternFill("solid", fgColor=HIJAU_MUDA)
        c.border = BORDER

    ws.cell(row=baris_total + 2, column=2, value="Kolom kuning = isi manual. Kolom Bobot & Kontribusi berformula, jangan ditimpa.").font = KECIL
    ws.cell(row=baris_total + 3, column=2, value="Kalau total Bobot bukan 100,0%, ada item yang belum diisi nilainya.").font = KECIL

    # ====================================================== Sheet Pengeluaran
    ws = wb.create_sheet("Pengeluaran")
    siapkan_sheet(ws, "PENCATATAN PENGELUARAN", [12, 12, 26, 13, 30, 7, 9, 14, 15, 11, 12, 26, 24])
    header(ws, 3, ["Tanggal", "No. Nota", "Vendor / Toko", "Kategori", "Deskripsi item",
                   "Qty", "Satuan", "Harga satuan", "Total", "Metode", "Status", "Item RAB", "Catatan"])

    data_peng = [] if kosong else CONTOH_PENGELUARAN
    mulai = 4
    akhir = mulai + max(len(data_peng), 25)
    for i in range(mulai, akhir):
        idx = i - mulai
        if idx < len(data_peng):
            tgl, nota, vendor, kat, desc, qty, sat, harga, metode, status, item, cat = data_peng[idx]
            ws.cell(row=i, column=1, value=tgl).number_format = TANGGAL
            ws.cell(row=i, column=2, value=nota)
            ws.cell(row=i, column=3, value=vendor)
            ws.cell(row=i, column=4, value=kat)
            ws.cell(row=i, column=5, value=desc)
            ws.cell(row=i, column=6, value=qty)
            ws.cell(row=i, column=7, value=sat)
            ws.cell(row=i, column=8, value=harga).number_format = RP
            ws.cell(row=i, column=10, value=metode)
            ws.cell(row=i, column=11, value=status)
            ws.cell(row=i, column=12, value=item)
            ws.cell(row=i, column=13, value=cat)
        ws.cell(row=i, column=1).number_format = TANGGAL
        ws.cell(row=i, column=8).number_format = RP
        ws.cell(row=i, column=9, value="=IF(OR(F{0}=\"\",H{0}=\"\"),\"\",F{0}*H{0})".format(i)).number_format = RP
        for col in range(1, 14):
            ws.cell(row=i, column=col).border = BORDER

    # Total
    trow = akhir
    ws.cell(row=trow, column=3, value="TOTAL PENGELUARAN").font = TEBAL
    ws.cell(row=trow, column=9, value="=SUM(I{}:I{})".format(mulai, akhir - 1)).number_format = RP
    for col in range(1, 14):
        c = ws.cell(row=trow, column=col)
        c.font = TEBAL
        c.fill = PatternFill("solid", fgColor=HIJAU_MUDA)
        c.border = BORDER

    # Dropdown
    dv_kat = DataValidation(type="list", formula1='"Penggunaan Bahan,Gaji Karyawan,Sewa Alat,Transport,Subkon,Lain-lain"', allow_blank=True)
    dv_kat.error = "Pilih salah satu kategori standar."
    ws.add_data_validation(dv_kat)
    dv_kat.add("D{}:D{}".format(mulai, akhir - 1))

    dv_met = DataValidation(type="list", formula1='"Cash,Transfer,Kasbon,Tempo"', allow_blank=True)
    ws.add_data_validation(dv_met)
    dv_met.add("J{}:J{}".format(mulai, akhir - 1))

    dv_st = DataValidation(type="list", formula1='"Lunas,Belum bayar"', allow_blank=True)
    ws.add_data_validation(dv_st)
    dv_st.add("K{}:K{}".format(mulai, akhir - 1))

    # ========================================================= Sheet Progress
    ws = wb.create_sheet("Progress")
    siapkan_sheet(ws, "PROGRESS & KURVA-S", [22, 16, 16, 18, 18, 16, 22])

    ringkasan = [
        ("Total RAB", "=RAB!$C${}".format(baris_total), RP),
        ("Nilai kontrak", "=Proyek!$B$7", RP),
        ("Progress total (%)", "=RAB!$F${}".format(baris_total), PERSEN),
        ("Nilai progress (Rp)", "=IF(B5=0,0,B6/100*B5)", RP),
        ("Total pengeluaran", "=Pengeluaran!$I${}".format(trow), RP),
        ("Sisa anggaran", "=IF(B4=0,0,B4-B8)", RP),
    ]
    ws["A3"] = "RINGKASAN"
    ws["A3"].font = Font(bold=True, color=HIJAU)
    for i, (label, formula, fmt) in enumerate(ringkasan, start=4):
        ws.cell(row=i, column=1, value=label).font = TEBAL
        c = ws.cell(row=i, column=2, value=formula)
        c.number_format = fmt
        c.border = BORDER
        c.fill = PatternFill("solid", fgColor=ABU)

    # Tabel kurva S
    ws["A11"] = "KURVA-S — RENCANA VS AKTUAL"
    ws["A11"].font = Font(bold=True, color=HIJAU)
    header(ws, 12, ["Periode", "Bobot rencana (%)", "Kumulatif rencana (%)", "Kumulatif aktual (%)", "Deviasi (%)", "Status", ""])

    data_rencana = [("Minggu 1", 0)] * 9 if kosong else CONTOH_RENCANA
    r0 = 13
    for i in range(r0, r0 + 9):
        idx = i - r0
        periode, bobot = data_rencana[idx] if idx < len(data_rencana) else ("Minggu {}".format(idx + 1), 0)
        ws.cell(row=i, column=1, value=periode)
        c = ws.cell(row=i, column=2, value=bobot)
        c.number_format = PERSEN
        c.fill = PatternFill("solid", fgColor=KUNING)
        if idx == 0:
            ws.cell(row=i, column=3, value="=B{}".format(i)).number_format = PERSEN
        else:
            ws.cell(row=i, column=3, value="=C{}+B{}".format(i - 1, i)).number_format = PERSEN
        # Kolom aktual: diisi manual hasil hitung progress
        ws.cell(row=i, column=4).number_format = PERSEN
        ws.cell(row=i, column=4).fill = PatternFill("solid", fgColor=KUNING)
        ws.cell(row=i, column=5, value='=IF(D{0}="","",D{0}-C{0})'.format(i)).number_format = PERSEN
        ws.cell(row=i, column=6, value='=IF(E{0}="","",IF(E{0}>=2,"Ahead",IF(E{0}>=-2,"On track",IF(E{0}>=-5,"Perhatian",IF(E{0}>=-10,"Terlambat","Kritis")))))'.format(i))
        for col in range(1, 7):
            ws.cell(row=i, column=col).border = BORDER

    # Total bobot rencana harus 100
    ws.cell(row=r0 + 9, column=1, value="TOTAL").font = TEBAL
    ws.cell(row=r0 + 9, column=2, value="=SUM(B{}:B{})".format(r0, r0 + 8)).number_format = PERSEN
    ws.cell(row=r0 + 9, column=2).font = TEBAL
    ws.cell(row=r0 + 9, column=2).fill = PatternFill("solid", fgColor=HIJAU_MUDA)
    ws.cell(row=r0 + 10, column=1, value="Total bobot rencana harus 100,0%. Kalau belum, sesuaikan pembagian per minggu.").font = KECIL

    # Conditional formatting deviasi
    rentang = "E{}:E{}".format(r0, r0 + 8)
    ws.conditional_formatting.add(
        rentang, CellIsRule(operator="lessThan", formula=["-5"], fill=PatternFill("solid", fgColor=MERAH_MUDA))
    )

    # Grafik kurva S
    chart = LineChart()
    chart.title = "Kurva-S — Rencana vs Aktual"
    chart.y_axis.title = "Kumulatif (%)"
    chart.x_axis.title = "Periode"
    chart.height = 8
    chart.width = 16
    data_ref = Reference(ws, min_col=3, max_col=4, min_row=12, max_row=r0 + 8)
    cats = Reference(ws, min_col=1, min_row=r0, max_row=r0 + 8)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "H11")

    # ============================================================ Sheet Tugas
    ws = wb.create_sheet("Tugas")
    siapkan_sheet(ws, "PEMBAGIAN TUGAS", [8, 42, 16, 14, 12, 12, 12, 26, 34, 13])
    header(ws, 3, ["ID", "Tugas", "Divisi", "PIC", "Mulai", "Selesai", "Dep.", "Item RAB", "Kriteria selesai", "Status"])

    data_tugas = [] if kosong else CONTOH_TUGAS
    t0 = 4
    t1 = t0 + max(len(data_tugas), 20)
    for i in range(t0, t1):
        idx = i - t0
        if idx < len(data_tugas):
            tid, tugas, divisi, pic, mulai_t, selesai_t, dep, item, kriteria, status = data_tugas[idx]
            ws.cell(row=i, column=1, value=tid)
            ws.cell(row=i, column=2, value=tugas)
            ws.cell(row=i, column=3, value=divisi)
            ws.cell(row=i, column=4, value=pic)
            ws.cell(row=i, column=5, value=mulai_t).number_format = TANGGAL
            ws.cell(row=i, column=6, value=selesai_t).number_format = TANGGAL
            ws.cell(row=i, column=7, value=dep)
            ws.cell(row=i, column=8, value=item)
            ws.cell(row=i, column=9, value=kriteria)
            ws.cell(row=i, column=10, value=status)
        ws.cell(row=i, column=5).number_format = TANGGAL
        ws.cell(row=i, column=6).number_format = TANGGAL
        for col in range(1, 11):
            ws.cell(row=i, column=col).border = BORDER

    dv_div = DataValidation(
        type="list",
        formula1='"Persiapan,Struktur,Dinding & Partisi,Plafon,Lantai & Dinding,Instalasi Listrik,Plumbing,Finishing,Furniture,Subkon,Serah Terima"',
        allow_blank=True,
    )
    ws.add_data_validation(dv_div)
    dv_div.add("C{}:C{}".format(t0, t1 - 1))

    dv_st2 = DataValidation(type="list", formula1='"Belum mulai,Jalan,Selesai,Tertahan"', allow_blank=True)
    ws.add_data_validation(dv_st2)
    dv_st2.add("J{}:J{}".format(t0, t1 - 1))

    # =========================================================== Sheet Panduan
    ws = wb.create_sheet("Panduan")
    siapkan_sheet(ws, "CARA PAKAI WORKBOOK INI", [4, 96])
    panduan = [
        ("Ini apa?", "Workbook ini adalah versi Excel dari empat fitur inti Skala Pro: catat pengeluaran, update progress dengan Kurva-S, bagi tugas, dan kelola proyek baru. Semua kolom penting memakai formula asli, jadi tetap hidup saat diisi."),
        ("Sheet Proyek", "Isi data master. Nilai kontrak di sel B7 dipakai untuk menghitung nilai progress di sheet Progress."),
        ("Sheet RAB", "Isi item pekerjaan dan nilainya di kolom C. Bobot dihitung otomatis dari total. Isi progress tiap item di kolom kuning. Total bobot harus 100,0%."),
        ("Sheet Progress", "Isi bobot rencana per minggu di kolom kuning. Kolom kumulatif rencana berformula. Kolom kumulatif aktual kamu isi dari hasil hitung progress fisik minggu itu. Deviasi dan status muncul otomatis. Grafik Kurva-S ada di kanan."),
        ("Sheet Pengeluaran", "Catat setiap nota. Kolom Total otomatis dari Qty x Harga satuan. Kategori, Metode, dan Status sudah berupa dropdown. Isi kolom Item RAB supaya biaya bisa ditelusuri."),
        ("Sheet Tugas", "Satu tugas satu PIC. Isi kriteria selesai dengan bukti objektif, bukan kata 'rapi'. Kolom Dep. diisi ID tugas prasyarat, misal T-01."),
        ("Cara hitung progress total", "Jumlahkan (bobot x progress) untuk semua item. Contoh: persiapan 10% x 100% = 10; pondasi 30% x 90% = 27; dinding 40% x 20% = 8; finishing 20% x 0% = 0. Total 45,0%. Bukan rata-rata persentase."),
        ("Kalau nanti pindah ke Skala", "Workbook ini jadi bahan impor. Item RAB, pengeluaran, dan tugas bisa disalin langsung. Bobot tidak perlu dihitung ulang."),
        ("Yang perlu diwaspadai", "Progress fisik di sini berdasarkan laporan lapangan, bukan opname bersama klien. Sebut hal ini di laporan ke klien supaya tidak jadi sengketa."),
    ]
    baris = 3
    for judul, isi in panduan:
        ws.cell(row=baris, column=1, value=judul).font = Font(bold=True, color=HIJAU)
        c = ws.cell(row=baris, column=2, value=isi)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[baris].height = 46
        baris += 1

    # --- Simpan
    output = args.output
    if not output:
        aman = "".join(ch if ch.isalnum() or ch in " -_" else "" for ch in nama).strip().replace(" ", "-")[:50]
        output = os.path.join(
            os.path.dirname(BASE_DIR),
            "output",
            "Skala-{}-{}.xlsx".format(aman or "Proyek", datetime.now().strftime("%Y%m%d")),
        )
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    wb.save(output)
    return output, baris_total, trow


def main():
    parser = argparse.ArgumentParser(
        description="Membuat workbook Excel setara fitur inti Skala Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Contoh:\n"
        "  python3 bin/buat_excel.py\n"
        "  python3 bin/buat_excel.py --nama-proyek \"Renovasi Dapur Bu Rina\" --nilai-kontrak 85000000\n"
        "  python3 bin/buat_excel.py --kosong --output template.xlsx\n",
    )
    parser.add_argument("--nama-proyek", help="Nama proyek")
    parser.add_argument("--nilai-kontrak", type=float, help="Nilai kontrak dalam rupiah, tanpa titik")
    parser.add_argument("--output", help="Path file .xlsx hasil")
    parser.add_argument("--kosong", action="store_true", help="Buat template kosong tanpa data contoh")
    args = parser.parse_args()

    path, baris_total, trow = buat(args)
    print("Workbook dibuat:")
    print("  " + path)
    print("")
    print("Isi: 6 sheet — Proyek, RAB, Pengeluaran, Progress (dengan grafik Kurva-S), Tugas, Panduan")
    print("Baris total RAB   : {}".format(baris_total))
    print("Baris total biaya : {}".format(trow))
    print("")
    if args.kosong:
        print("Template kosong. Mulai isi dari sheet Proyek, lalu RAB.")
    else:
        print("Berisi data contoh supaya kelihatan cara kerjanya. Hapus isinya sebelum dipakai.")


if __name__ == "__main__":
    main()
