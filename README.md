# ⚽ FPL Mini-League Data Extractor & Analytics Dashboard

Tools lengkap berbasis Python untuk mengekstrak, menganalisis, dan memvisualisasikan data **Fantasy Premier League (FPL) Mini-League**.

Tersedia dalam 2 mode:
1. **Interactive Web Dashboard (Streamlit + Plotly)**: Dashboard interaktif dengan grafik dan visualisasi modern.
2. **CLI Terminal Tool (Rich)**: Penarik data cepat langsung dari terminal dengan tabel berwarna & ekspor instan ke Excel/CSV.

---

## 🚀 Fitur Utama

- 🏆 **Klasemen Lengkap**: Rank, pergerakan rank (🔼/🔽), poin GW, total poin, overall rank, nilai tim, sisa bank.
- 👑 **Captaincy Breakdown**: Distribusi pilihan kapten & wakil kapten di seluruh manajer liga.
- 📊 **Effective Ownership (EO)**: Persentase kepemilikan dan penggunaan pemain (starter, bench, kapten, triple captain) di mini-league vs FPL Global.
- 📈 **Grafik Tren & Performa**: Visualisasi interaktif riwayat poin kumulatif, poin mingguan, dan rank dunia (GW1 s/d GW sekarang).
- 🃏 **Chip Tracker**: Pelacak status penggunaan Wildcard 1/2, Free Hit, Triple Captain, dan Bench Boost untuk setiap manajer.
- ⚔️ **Squad Comparison (H2H)**: Bandingkan susunan squad 2 manajer secara berdampingan untuk melihat pemain bersama (*common*) & pemain pembeda (*differentials*).
- 📥 **Ekspor Multi-Format**:
  - File Excel (`.xlsx`) multi-sheet terformat dan diberi warna tema Premier League.
  - File CSV untuk integrasi pengolahan data lanjutan.

---

## 📦 Instalasi & Persiapan

Buka terminal di folder project ini (`d:\Antigravity\FPL`), lalu pastikan dependencies terinstall:

```bash
pip install -r requirements.txt
```

---

## 🖥️ Cara Menjalankan

### 1. Menjalankan Web Dashboard Interaktif (Rekomendasi)

Jalankan perintah berikut di terminal:

```bash
streamlit run app.py
```

Browser akan terbuka secara otomatis di `http://localhost:8501`.
- Masukkan **League ID** Anda pada menu samping (*Sidebar*).
- Pilih **Gameweek (GW)** yang ingin dilihat.
- Klik **Tarik / Refresh Data**.

---

### 2. Menjalankan via CLI (Terminal)

Untuk menarik data cepat dan langsung mengekspornya ke Excel:

```bash
# Mode Interaktif (akan meminta input League ID di terminal)
python fpl_cli.py

# Atau dengan parameter langsung:
python fpl_cli.py --league 314 --gw 25 --export excel

# Opsi parameter:
# --league / -l : League ID FPL (contoh: 314)
# --gw / -g     : Gameweek tertentu (default: GW aktif saat ini)
# --export / -e : Format ekspor: excel, csv, atau both (default: excel)
# --limit       : Batasi jumlah manajer teratas (contoh: --limit 50)
```

---

## 🔍 Cara Mengetahui League ID Mini-League Anda

1. Buka dan login ke situs [fantasy.premierleague.com](https://fantasy.premierleague.com).
2. Klik menu **Leagues & Cups**, lalu klik nama Mini-League Anda.
3. Perhatikan URL di address bar browser Anda:
   ```
   https://fantasy.premierleague.com/leagues/123456/standings/c
                                             ^^^^^^
   ```
4. Angka tersebut (`123456`) adalah **League ID** Anda!
