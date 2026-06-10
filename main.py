from flask import Flask, render_template, redirect, url_for, flash, request, session
from datetime import datetime, timedelta
from supabase import create_client
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.jinja_env.globals.update(enumerate=enumerate)


# ─── HELPER: hitung harga per pesanan ───
def hitung_harga(paket, berat):
    if paket == 1:
        return 9000 * berat   # Kilat
    elif paket == 3:
        return 6000 * berat   # Santuy
    else:
        return 7000 * berat   # fallback

# ─── HELPER: nomor minggu ISO dari string tanggal "dd-mm-yyyy" ───
def get_week(tgl_str):
    return datetime.strptime(tgl_str, "%Y-%m-%d").isocalendar()[1]

# ─── HELPER: nama hari singkat dari string tanggal ───
def get_hari(tgl_str):
    HARI = {0:'Sen', 1:'Sel', 2:'Rab', 3:'Kam', 4:'Jum', 5:'Sab', 6:'Min'}
    return HARI[datetime.strptime(tgl_str, "%Y-%m-%d").weekday()]


@app.route('/')
def home():
    return render_template('pages/login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    result = (
        supabase
        .table("users")
        .select("*")
        .eq("username", username)
        .eq("password", password)
        .execute()
    )

    user = result.data

    if len(user) > 0:
        session['username'] = user[0]['username']
        session['role'] = user[0]['role']
        return redirect(url_for('dashboard'))

    flash("Username atau password salah")
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    role = session['role']

    semua_laundry = (
        supabase
        .table("laundry")
        .select("*")
        .execute()
    ).data

    rows = (
        supabase
        .table("laundry")
        .select("*")
        .eq("tahap", "Proses")
        .execute()
    ).data


    selesai = (
    supabase.table("laundry")
    .select("*")
    .eq("tahap", "Selesai")
    .execute()
    ).data

    rows_pembelian = (
        supabase
        .table("pembelian")
        .select("*")
        .execute()
    ).data
    # ── Waktu ──
    hari_ini = datetime.now().date()
    minggu_ini = hari_ini.isocalendar()[1]
    tanggal = hari_ini.strftime("%Y-%m-%d")
    jam_sekarang = datetime.now().strftime("%H:%M")

    # ════════════════════════════════════════════
    # DATA KARYAWAN
    # ════════════════════════════════════════════
    jumlah_hari_ini = 0
    jumlah_masuk_hari_ini = 0
    jumlah_proses = 0
    jumlah_belum_diambil = 0

    data_laundry = []
    for row in rows:
        estimasi = datetime.strptime(row["tanggal_selesai"], "%Y-%m-%d").date()
        sisa_hari = (estimasi - hari_ini).days

        if estimasi == hari_ini:
            jumlah_masuk_hari_ini += 1

        jumlah_proses += 1

        if sisa_hari == 0:
            status_tenggat = "Hari Ini"
            jumlah_hari_ini += 1
        elif sisa_hari == 1:
            status_tenggat = "Besok"
        elif sisa_hari == 2:
            status_tenggat = "2 Hari Lagi"
        elif sisa_hari == 3:
            status_tenggat = "3 Hari Lagi"
        elif sisa_hari < 0:
            status_tenggat = "Terlambat"
        else:
            status_tenggat = f"{sisa_hari} Hari Lagi"

        data_laundry.append({
            "id": row["id"],
            "nama": row["nama_pelanggan"],
            "gender": row["jenis_kelamin"],
            "wa": row["no_wa"],
            "paket": row["paket_laundry"],
            "berat": row["berat"],
            "tanggal_masuk": row["tanggal_masuk"],
            "tanggal_selesai": row["tanggal_selesai"],
            "antar_jemput": row["antar_jemput"],
            "catatan": row["catatan"],
            "status": row["tahap"],
            "sisa_hari": sisa_hari,
            "status_tenggat": status_tenggat,
        })

    data_selesai = []
    for row in selesai:
        estimasi = datetime.strptime(row["tanggal_selesai"], "%Y-%m-%d").date()
        sisa_hari = (estimasi - hari_ini).days

        if row["tahap"] == "Sudah Diambil":
            status_tenggat = "Sudah Diambil"
        elif sisa_hari < 0:
            status_tenggat = "Belum Diambil"
            jumlah_belum_diambil += 1
        else:
            status_tenggat = "Selesai"

        telat_woy = sisa_hari * -1

        data_selesai.append({
            "id": row["id"],
            "nama": row["nama_pelanggan"],
            "gender": row["jenis_kelamin"],
            "wa": row["no_wa"],
            "paket": row["paket_laundry"],
            "berat": row["berat"],
            "tanggal_masuk": row["tanggal_masuk"],
            "tanggal_selesai": row["tanggal_selesai"],
            "antar_jemput": row["antar_jemput"],
            "catatan": row["catatan"],
            "status": row["tahap"],
            "sisa_hari": sisa_hari,
            "status_tenggat": status_tenggat,
            "telat_woy": telat_woy
        })

    data_pembelian = []
    for row in rows_pembelian:
        data_pembelian.append({
            "tanggal": row["tanggal_beli"],
            "nama_barang": row["nama_barang"],
            "kuantitas": row["kuantitas"],
            "harga_satuan": row["harga_satuan"],
            "total": row["total"],
            "supplier": row["supplier"],
            "pencatat": row["pencatat"],
        })

    # ════════════════════════════════════════════
    # DATA ADMIN — dihitung dari semua_laundry
    # ════════════════════════════════════════════

    # ── Gender ──
    jml_perempuan = 0
    jml_lakilaki = 0
    for row in semua_laundry:
        g = row["jenis_kelamin"]
        if g in ('P', 'Perempuan'):
            jml_perempuan += 1
        elif g in ('L', 'Laki-laki'):
            jml_lakilaki += 1
    total_pelanggan = jml_perempuan + jml_lakilaki
    pct_perempuan = round(jml_perempuan / total_pelanggan * 100) if total_pelanggan else 0
    pct_lakilaki  = round(jml_lakilaki  / total_pelanggan * 100) if total_pelanggan else 0

    # ── Paket terlaris minggu ini (Kilat=1, Santuy=3) ──
    jml_kilat_minggu  = 0
    jml_santuy_minggu = 0
    for row in semua_laundry:
        try:
            w = get_week(row["tanggal_masuk"])
        except:
            continue
        if w == minggu_ini:
            if row["paket_laundry"] == 1:
                jml_kilat_minggu += 1
            elif row["paket_laundry"] == 3:
                jml_santuy_minggu += 1

    # ── Pendapatan per hari minggu ini ──
    HARI_LABELS = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
    pendapatan_per_hari = defaultdict(float)
    pesanan_per_hari    = defaultdict(int)

    for row in semua_laundry:
        try:
            w = get_week(row["tanggal_masuk"])
        except:
            continue
        if w == minggu_ini:
            hari = get_hari(row["tanggal_masuk"])
            harga = hitung_harga(row["paket_laundry"], row["berat"])
            pendapatan_per_hari[hari] += harga
            pesanan_per_hari[hari]    += 1

    chart_pendapatan_labels = HARI_LABELS
    chart_pendapatan_data   = [int(pendapatan_per_hari.get(h, 0)) for h in HARI_LABELS]
    chart_pesanan_data      = [pesanan_per_hari.get(h, 0) for h in HARI_LABELS]

    # ── Total pendapatan & pengeluaran minggu ini ──
    total_pendapatan_minggu = sum(chart_pendapatan_data)

    pengeluaran_per_hari = defaultdict(int)
    total_pengeluaran_minggu = 0
    for row in rows_pembelian:
        try:
            w = get_week(row["tanggal_beli"])
        except:
            continue
        if w == minggu_ini:
            total_pengeluaran_minggu += row["total"]
            hari = get_hari(row["tanggal_beli"])
            pengeluaran_per_hari[hari] += row["total"]

    laba_bersih_minggu = total_pendapatan_minggu - total_pengeluaran_minggu

    # ── Pertumbuhan pelanggan per minggu (6 minggu terakhir) ──
    minggu_counts = defaultdict(int)
    for row in semua_laundry:
        try:
            w = get_week(row["tanggal_masuk"])
        except:
            continue
        minggu_counts[w] += 1

    # Ambil 6 minggu terakhir secara kumulatif
    sorted_weeks = sorted(minggu_counts.keys())[-6:]
    growth_labels = [f"Minggu {w}" for w in sorted_weeks]
    growth_data   = []
    kumulatif = 0
    for w in sorted_weeks:
        kumulatif += minggu_counts[w]
        growth_data.append(kumulatif)

    # ── Daftar pelanggan unik dengan total order dan total bayar ──
    pelanggan_dict = {}
    for row in semua_laundry:
        nama = row["nama_pelanggan"]
        wa   = row["no_wa"]
        gender = row["jenis_kelamin"]
        harga  = hitung_harga(row["paket_laundry"], row["berat"])
        tgl    = row["tanggal_masuk"]
        key    = wa  # pakai WA sebagai unique key

        if key not in pelanggan_dict:
            pelanggan_dict[key] = {
                "nama": nama,
                "gender": gender,
                "wa": wa,
                "total_order": 0,
                "total_bayar": 0,
                "terakhir_order": tgl,
            }
        pelanggan_dict[key]["total_order"] += 1
        pelanggan_dict[key]["total_bayar"] += harga
        # simpan tanggal terbaru
        tgl_dt = datetime.strptime(tgl, "%Y-%m-%d")
        existing_dt = datetime.strptime(pelanggan_dict[key]["terakhir_order"], "%Y-%m-%d")
        if tgl_dt > existing_dt:
            pelanggan_dict[key]["terakhir_order"] = tgl

    daftar_pelanggan = sorted(pelanggan_dict.values(), key=lambda x: x["total_order"], reverse=True)

    return render_template(
        'index.html',
        # karyawan
        data_laundry=data_laundry,
        data_selesai=data_selesai,
        data_pembelian=data_pembelian,
        jumlah_hari_ini=jumlah_hari_ini,
        jumlah_masuk_hari_ini=jumlah_masuk_hari_ini,
        jumlah_proses=jumlah_proses,
        jumlah_belum_diambil=jumlah_belum_diambil,
        # info umum
        username=username,
        role=role,
        tanggal=tanggal,
        jam_sekarang=jam_sekarang,
        # admin — gender
        jml_perempuan=jml_perempuan,
        jml_lakilaki=jml_lakilaki,
        total_pelanggan=total_pelanggan,
        pct_perempuan=pct_perempuan,
        pct_lakilaki=pct_lakilaki,
        # admin — paket
        jml_kilat_minggu=jml_kilat_minggu,
        jml_santuy_minggu=jml_santuy_minggu,
        # admin — chart data (dikirim sebagai JSON-ready list)
        chart_pendapatan_labels=chart_pendapatan_labels,
        chart_pendapatan_data=chart_pendapatan_data,
        chart_pesanan_data=chart_pesanan_data,
        # admin — keuangan minggu ini
        total_pendapatan_minggu=total_pendapatan_minggu,
        total_pengeluaran_minggu=total_pengeluaran_minggu,
        laba_bersih_minggu=laba_bersih_minggu,
        # admin — pertumbuhan pelanggan
        growth_labels=growth_labels,
        growth_data=growth_data,
        # admin — daftar pelanggan
        daftar_pelanggan=daftar_pelanggan,
    )


# ── LOGIKA INPUT LAUNDRY ──
@app.route('/dashboard1', methods=['POST'])
def dashboard1():
    nama_pelanggan = request.form['nama_pelanggan'].title()
    gender = request.form['jenis_kelamin']
    jenis_kelamin = "Laki-laki" if gender == "L" else "Perempuan"
    wa = request.form['no_wa']
    paket_laundry = int(request.form['paket_laundry'])
    berat = float(request.form['berat'])
    tanggal_masuk = datetime.now()
    tanggal_selesai = tanggal_masuk + timedelta(days=paket_laundry)
    antar_jemput = request.form['antar_jemput']
    catatan = request.form['catatan']

    supabase.table("laundry").insert({
        "nama_pelanggan": nama_pelanggan,
        "jenis_kelamin": jenis_kelamin,
        "no_wa": wa,
        "paket_laundry": paket_laundry,
        "berat": berat,
        "tanggal_masuk": tanggal_masuk.strftime("%Y-%m-%d"),
        "tanggal_selesai": tanggal_selesai.strftime("%Y-%m-%d"),
        "antar_jemput": antar_jemput,
        "catatan": catatan,
        "tahap": "Proses"
    }).execute()
    return redirect(url_for('dashboard'))


# ── LOGIKA PEMBELIAN ──
@app.route('/pembelian', methods=['POST'])
def pembelian():
    username = session['username']

    tanggal_beli = datetime.now()
    nama_barang = request.form['nama_barang'].title()
    kuantitas = int(request.form['kuantitas'])
    harga_satuan = int(request.form['harga_satuan'])

    total = kuantitas * harga_satuan

    supplier = request.form['supplier'].title()
    pencatat = username.title()

    supabase.table("pembelian").insert({
        "tanggal_beli": tanggal_beli.strftime("%Y-%m-%d"),
        "nama_barang": nama_barang,
        "kuantitas": kuantitas,
        "harga_satuan": harga_satuan,
        "total": total,
        "supplier": supplier,
        "pencatat": pencatat
    }).execute()

    return redirect(url_for('dashboard', tab='pembelian'))

# ── LOGIKA TAHAP SELESAI ──
@app.route('/selesai/<int:id>')
def tahap(id):

    supabase.table("laundry").update({
        "tahap": "Selesai"
    }).eq("id", id).execute()

    return redirect(url_for('dashboard'))


# ── LOGIKA SUDAH DIAMBIL ──
@app.route('/sudah_diambil/<int:id>')
def sudah_diambil(id):

    supabase.table("laundry").update({
        "tahap": "Sudah Diambil"
    }).eq("id", id).execute()

    return redirect(url_for('dashboard'))

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
