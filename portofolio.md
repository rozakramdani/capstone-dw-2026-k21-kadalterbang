## Nama Tim dan Avatar

Nama Tim: **Kadal Terbang**

Filosofi kadal terbang (genus *Draco*) mengajarkan tentang pentingnya beradaptasi dan kemampuan memaksimalkan keterbatasan. Celah keberhasilan tercipta bukan dari apa yang kita miliki, melainkan dari cara kita mengolah apa yang ada. Lahir tanpa sayap sejati tak lantas membuatnya terikat selamanya membatasi langkah untuk tetap melayang tinggi.

Avatar Tim: 🦎✈️

| Komponen | Penanggung Jawab | Alasan Pembagian |
| :--- | :--- | :--- |
| **Ekstraksi dan lineage** | Rozak Ramdani (124450100) | Bertanggung jawab membangun skrip unduh data mentah, memastikan validasi SHA256 awal, serta mencatat asal-usul data (*lineage*) agar proses dapat direproduksi. |
| **Profil dan pembersihan** | Danil Nur Fadillah (124450103) | Bertanggung jawab penanganan awal (*screening*) data mentah, mengidentifikasi *missing values*, mendeteksi duplikat, serta menangani *outliers* dan patahan seri. |
| **Transformasi dan panel** | Muhammad Daffa Arrafi (124450120) | Bertanggung jawab merestrukturisasi (*reshape*) data ke format panel Gold (Provinsi × Periode × Indikator) dan menyelaraskan variabel. |
| **Integrasi, penyimpanan, dan skala** | Ahmad Bimo Akbar Arkana Putra (124450113) & Andra Ilham Bintang (124450060) | Mengelola penyimpanan SQL (Silver & Gold), membandingkan efisiensi pemrosesan (Pandas vs DuckDB/Dask), serta menjaga skalabilitas komputasi *pipeline*. |
| **Validasi dan dokumentasi** | Layina Ropiqo (124450016) | Bertanggung jawab membuat skema validasi otomatis (`src.common.skema`), mengelola *data dictionary*, serta memastikan kriteria *Definition of Done* (DoD) terpenuhi. |

| Tugas Sampingan | Penanggung Jawab | Alasan Pembagian |
| :--- | :--- | :--- |
| **Koordinator** | Rozak Ramdani (124450100) | Mengoordinasikan alur komunikasi tim, jadwal *standup*, serta memantau progres *sprint* agar selaras dengan alur *pipeline* dari tahap awal *Ekstraksi*. |
| **Penjaga Data & Evaluasi** | Danil Nur Fadillah (124450103) | Berhubungan erat dengan tugas utamanya (*Profil dan Pembersihan*), sehingga ideal dalam mengawasi integritas data mentah/uji serta validitas penanganan *outliers*. |
| **Integrator** | Muhammad Daffa Arrafi (124450120) | Berada di posisi *Transformasi dan Panel*, memudahkan penggabungan kode dari pembersihan ke format panel Gold sebelum di-merge ke *main branch*. |
| **Analis Utama** | Ahmad Bimo Akbar Arkana Putra (124450113) & Andra Ilham Bintang (124450060) | Memegang *Integrasi, Penyimpanan, dan Skala*, sangat tepat memimpin interpretasi temuan, perbandingan efisiensi pemrosesan (Pandas vs DuckDB), dan penulisan laporan akhir. |
| **Reproduksi & Demo** | Layina Ropiqo (124450016) | Berhubungan erat dengan tugas utamanya (*Validasi dan Dokumentasi*), memastikan *pipeline* dapat dijalankan ulang dari nol (*reproducible*) sesuai kriteria DoD dan menyiapkan materi *Demo Sprint*. |

### Standup Mingguan dan Kanal Komunikasi

**Hari/jam standup:** Sabtu (19.30 – 20.30 WIB) & Minggu (16.00 – 17.30 WIB)  
**Kanal:** WhatsApp Group (Koordinasi Harian) & Google Meet (Rapat & Kerja Bersama)

| Hari & Waktu | Fokus Utama | Agenda Rapat |
| :--- | :--- | :--- |
| **Sabtu**<br>(19.30 – 20.30 WIB) | **Sync & Evaluasi Progres** | - Evaluasi status tugas per komponen (Ekstraksi, Pembersihan, Transformasi, Integrasi, Validasi).<br>- Pembahasan kendala teknis pada kode dan repositori GitHub.<br>- Penyusunan rencana *Pull Request* (PR) dan *merge* ke *main branch*. |
| **Minggu**<br>(16.00 – 17.30 WIB) | **Kerja Bersama & Persiapan Sprint** | - Sesi pengerjaan dan integrasi *pipeline* bersama serta penyelesaian *merge conflict*.<br>- Penyamaan persepsi untuk pengisian *Log Sprint* dan persiapan materi *Demo Sprint*.<br>- Pembagian fokus dan target capaian untuk minggu berikutnya. |

## Jika ada anggota yang menghilang

* **Sprint 1 (Tidak Muncul):**
  * Koordinator tim akan menghubungi anggota yang bersangkutan melalui WhatsApp/telepon untuk mengonfirmasi kendala yang dihadapi.
  * Tim membantu penyesuaian kendala teknis/logistik jika ada, serta mengingatkan pengisian Log Sprint dan kontribusi kode.
  * Jika tetap tidak ada respons hingga akhir Sprint 1, Koordinator mencatat status non-aktif anggota tersebut dan melaporkannya ke Dosen Pembimbing sebagai peringatan awal.

* **Sprint 2 (Masih Tidak Muncul):**
  * Koordinator melaporkan secara resmi kepada Dosen Pembimbing untuk pemanggilan dan penanganan sesuai aturan platform (penandaan anggota pasif/merah 2 sprint berturut-turut).
  * Komponen utama yang diampu anggota yang menghilang akan dicatat di laporan tim (*reports/tim.md*) dengan keterangan: *"Komponen X tidak dapat disajikan secara maksimal karena penanggung jawab pasif/tidak aktif"*.
  * Anggota tim lain berfokus menyelesaikan komponen masing-masing dan menjaga integrasi *pipeline* utama tetap dapat berjalan (*reproducible*).
