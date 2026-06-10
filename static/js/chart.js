/* ════════════════════════════════════════════
   LAUNDRYPRO — chart.js
   Data diambil dari data-attribute canvas (dikirim Flask via Jinja2)
   Membutuhkan: https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
   ════════════════════════════════════════════ */

let charts = {};

/* ── Gradient helpers ── */
function gradientBlue(ctx) {
  const g = ctx.createLinearGradient(0, 0, 0, 300);
  g.addColorStop(0, 'rgba(94,114,228,0.4)');
  g.addColorStop(1, 'rgba(94,114,228,0)');
  return g;
}

/* ── Helper: baca data-attribute dari canvas, parse JSON ── */
function readData(id, attr) {
  const el = document.getElementById(id);
  if (!el) return null;
  try { return JSON.parse(el.dataset[attr]); } catch { return null; }
}

/* ── Destroy & buat chart baru ── */
function createChart(id, config) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(canvas, config);
}

/* ── Axis style reusable ── */
const axisDefault = {
  y: {
    grid: { color: '#f0f2f5' },
    ticks: { color: '#8898aa', font: { size: 11 } }
  },
  x: {
    grid: { display: false },
    ticks: { color: '#8898aa', font: { size: 11 } }
  }
};

const axisRupiah = {
  y: {
    grid: { color: '#f0f2f5' },
    ticks: {
      color: '#8898aa', font: { size: 11 },
      callback: v => 'Rp ' + Number(v).toLocaleString('id-ID')
    }
  },
  x: {
    grid: { display: false },
    ticks: { color: '#8898aa', font: { size: 11 } }
  }
};


/* ════════════════════════════════════════════
   INIT ALL CHARTS
   ════════════════════════════════════════════ */
function initCharts() {

  /* ── 1. Chart Pesanan Minggu Ini (Karyawan Dashboard) ── */
  const labelsK  = readData('chartWeekK', 'labels') || ['Sen','Sel','Rab','Kam','Jum','Sab','Min'];
  const valuesK  = readData('chartWeekK', 'values') || [0,0,0,0,0,0,0];
  createChart('chartWeekK', {
    type: 'line',
    data: {
      labels: labelsK,
      datasets: [{
        label: 'Pesanan',
        data: valuesK,
        borderColor: '#5e72e4',
        backgroundColor: ctx => gradientBlue(ctx.chart.ctx),
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: '#5e72e4',
        tension: 0,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: axisDefault
    }
  });
  document.addEventListener('DOMContentLoaded', function() {
    initCharts();
});


  /* ── 2. Chart Pendapatan Overview (Admin) — hanya mingguan, 1 batang ── */
  const labelsP = readData('chartPenjualan', 'labels') || ['Sen','Sel','Rab','Kam','Jum','Sab','Min'];
  const valuesP = readData('chartPenjualan', 'values') || [0,0,0,0,0,0,0];
  createChart('chartPenjualan', {
    type: 'bar',
    data: {
      labels: labelsP,
      datasets: [{
        label: 'Pendapatan',
        data: valuesP,
        backgroundColor: 'rgba(94,114,228,0.75)',
        borderRadius: 6,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: axisRupiah
    }
  });


  /* ── 3. Chart Distribusi Pelanggan (donut) ── */
  const valPerempuan = readData('chartPelanggan', 'perempuan') || 0;
  const valLakilaki  = readData('chartPelanggan', 'lakilaki')  || 0;

  
    document.getElementById("detailBodyJadwal").innerHTML = `
      <div>  
      <p>woi</p>
      </div>
      `;
  createChart('chartPelanggan', {
    type: 'doughnut',
    data: {
      labels: ['Perempuan', 'Laki-laki'],
      datasets: [{
        data: [valPerempuan, valLakilaki],
        backgroundColor: ['#fb6340', '#11cdef'],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: { legend: { display: false } }
    }
  });


  /* ── 4. Chart Total Pesanan per Hari (Admin) — BAR, mingguan ── */
  const labelsPO = readData('chartTotalOrders', 'labels') || ['Sen','Sel','Rab','Kam','Jum','Sab','Min'];
  const valuesPO = readData('chartTotalOrders', 'values') || [0,0,0,0,0,0,0];
  createChart('chartTotalOrders', {
    type: 'bar',
    data: {
      labels: labelsPO,
      datasets: [{
        label: 'Pesanan',
        data: valuesPO,
        backgroundColor: 'rgba(251,99,64,0.75)',
        borderRadius: 5,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: axisDefault
    }
  });


  /* ── 5. Chart Pendapatan (Data Penjualan) — LINE lurus (tension:0) ── */
  const labelsP2 = readData('chartPenjualan2', 'labels') || ['Sen','Sel','Rab','Kam','Jum','Sab','Min'];
  const valuesP2 = readData('chartPenjualan2', 'values') || [0,0,0,0,0,0,0];
  createChart('chartPenjualan2', {
    type: 'line',
    data: {
      labels: labelsP2,
      datasets: [{
        label: 'Pendapatan',
        data: valuesP2,
        borderColor: '#5e72e4',
        backgroundColor: ctx => gradientBlue(ctx.chart.ctx),
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: '#5e72e4',
        tension: 0,        // 0 = garis lurus
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: axisRupiah
    }
  });


  /* ── 6. Chart Paket Terlaris (donut) — hanya Kilat & Santuy ── */
  const valKilat  = readData('chartPaket', 'kilat')  || 0;
  const valSantuy = readData('chartPaket', 'santuy') || 0;
  createChart('chartPaket', {
    type: 'doughnut',
    data: {
      labels: ['Kilat', 'Santuy'],
      datasets: [{
        data: [valKilat, valSantuy],
        backgroundColor: ['#5e72e4', '#2dce89'],
        borderWidth: 0,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { size: 11 }, color: '#8898aa' }
        }
      }
    }
  });


  /* ── 7. Chart Pertumbuhan Pelanggan — LINE ── */
  const labelsG = readData('chartGrowth', 'labels') || [];
  const valuesG = readData('chartGrowth', 'values') || [];
  createChart('chartGrowth', {
    type: 'line',
    data: {
      labels: labelsG,
      datasets: [{
        label: 'Total Pelanggan',
        data: valuesG,
        borderColor: '#5e72e4',
        backgroundColor: ctx => gradientBlue(ctx.chart.ctx),
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: '#5e72e4',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: axisDefault
    }
  });


  /* ── 8. Chart Segmentasi Gender — BAR ── */
  const gPerempuan = readData('chartGender', 'perempuan') || 0;
  const gLakilaki  = readData('chartGender', 'lakilaki')  || 0;
  createChart('chartGender', {
  type: 'bar',
  data: {
    labels: ['Perempuan', 'Laki-laki'],
    datasets: [{
      data: [gPerempuan, gLakilaki],
      backgroundColor: [
        'rgba(251,99,64,0.75)',
        'rgba(17,205,239,0.75)'
      ]
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 200   // <- ubah sesuai kebutuhan
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  }
  });
}
