# 🫧 Kilau Laundry

Aplikasi manajemen laundry berbasis web yang dibangun dengan **Flask** dan **Supabase**. Dirancang untuk memudahkan karyawan dan admin dalam mengelola pesanan, jadwal, status laundry, serta laporan keuangan.

---

## ✨ Fitur

### 👷 Karyawan
| Fitur | Deskripsi |
|---|---|
| **Dashboard Karyawan** | Ringkasan pesanan sedang diproses, tenggat hari ini, dan pesanan belum diambil |
| **Input Laundry** | Tambah pesanan baru dengan data pelanggan, paket, berat, dan layanan antar-jemput |
| **Jadwal Laundry** | Lihat daftar pesanan beserta estimasi selesai dan status tenggat |
| **Status Pesanan** | Update status pesanan dari *Proses* → *Selesai* → *Sudah Diambil* |
| **Data Pembelian** | Catat pembelian barang/supplies dari supplier |

### 🔑 Admin (Role: Admin)
| Fitur | Deskripsi |
|---|---|
| **Dashboard Admin** | Grafik pendapatan & pesanan mingguan, distribusi gender pelanggan, laba bersih |
| **Data Penjualan** | Rekap seluruh transaksi laundry beserta pendapatan per pesanan |
| **Data Pelanggan** | Daftar pelanggan unik, total order, total pembayaran, dan tanggal order terakhir |

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Font & Icon**: Plus Jakarta Sans, Font Awesome 6

---

## 📦 Paket Laundry

| Kode | Nama | Harga | Estimasi Selesai |
|---|---|---|---|
| `1` | Kilat | Rp 9.000 / kg | 1 hari |
| `3` | Santuy | Rp 6.000 / kg | 3 hari |

---

## 🗂️ Struktur Proyek

```
kilau-laundry/
├── main.py                        # Aplikasi Flask utama (routes & logika bisnis)
├── .env                           # Konfigurasi environment (tidak di-commit)
├── static/
│   ├── css/
│   │   ├── dashboard.css          # Stylesheet utama dashboard
│   │   └── login.css              # Stylesheet halaman login
│   ├── js/
│   │   ├── website.js             # Logika navigasi & interaksi UI
│   │   └── chart.js               # Konfigurasi grafik Chart.js
│   └── img/
│       └── logo-baru.png          # Logo Kilau Laundry
└── templates/
    ├── index.html                 # Layout utama (single-page wrapper)
    ├── pages/
    │   ├── login.html             # Halaman login
    │   ├── sidebar.html           # Sidebar navigasi
    │   ├── dashboard-karyawan.html
    │   ├── input-laundry.html
    │   ├── jadwal-laundry.html
    │   ├── status-pesanan.html
    │   └── pembelian.html
    ├── admin/
    │   ├── dashboard-admin.html
    │   ├── data-penjualan.html
    │   └── pelanggan.html
    └── modals/
        ├── modals.html
        ├── modals-jadwal.html
        └── modals-status.html
```

---

## 🚀 Cara Menjalankan

### 1. Clone & Masuk ke Direktori

```bash
git clone <url-repo>
cd kilau-laundry
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependensi

Gunakan `requirements.txt` agar versi library konsisten:

```bash
pip install -r requirements.txt
```

> Atau install manual (minimal):
> ```bash
> pip install flask supabase python-dotenv
> ```

### 4. Konfigurasi Environment

Buat file `.env` di root proyek:

```env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_flask_secret_key
```

### 5. Jalankan Aplikasi

```bash
python main.py
```

Buka browser dan akses: **http://localhost:5000**

---

## 🗄️ Struktur Database (Supabase)

### Tabel `users`
| Kolom | Tipe | Keterangan |
|---|---|---|
| `username` | text | Username login |
| `password` | text | Password login |
| `role` | text | `Karyawan` atau `Admin` |

### Tabel `laundry`
| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | int | Primary key |
| `nama_pelanggan` | text | Nama pelanggan |
| `jenis_kelamin` | text | `Laki-laki` / `Perempuan` |
| `no_wa` | text | Nomor WhatsApp |
| `paket_laundry` | int | `1` = Kilat, `3` = Santuy |
| `berat` | float | Berat cucian (kg) |
| `tanggal_masuk` | date | Tanggal terima |
| `tanggal_selesai` | date | Estimasi selesai |
| `antar_jemput` | text | Layanan antar-jemput |
| `catatan` | text | Catatan tambahan |
| `tahap` | text | `Proses` / `Selesai` / `Sudah Diambil` |

### Tabel `pembelian`
| Kolom | Tipe | Keterangan |
|---|---|---|
| `tanggal_beli` | date | Tanggal pembelian |
| `nama_barang` | text | Nama barang |
| `kuantitas` | int | Jumlah barang |
| `harga_satuan` | int | Harga per satuan |
| `total` | int | Total harga |
| `supplier` | text | Nama supplier |
| `pencatat` | text | Username pencatat |

---

## 🔐 Autentikasi & Role

- Login dilakukan via halaman `/` dengan verifikasi ke tabel `users` di Supabase.
- Session Flask menyimpan `username` dan `role` selama pengguna aktif.
- Halaman dan menu **Admin** hanya tampil jika `role == 'Admin'`.

---

## 📊 Fitur Analitik (Dashboard Admin)

- **Grafik Pendapatan Mingguan** — Pendapatan per hari dalam minggu berjalan
- **Grafik Jumlah Pesanan** — Jumlah pesanan per hari dalam minggu berjalan
- **Distribusi Gender** — Persentase pelanggan laki-laki vs perempuan
- **Paket Terlaris** — Jumlah paket Kilat vs Santuy minggu ini
- **Pertumbuhan Pelanggan** — Tren kumulatif pelanggan 6 minggu terakhir
- **Ringkasan Keuangan** — Total pendapatan, pengeluaran, dan laba bersih minggu ini

---

## 📝 Lisensi

Proyek ini dikembangkan untuk keperluan internal **Kilau Laundry**.
