# Konverter Video ke Frame

Taruh semua video yang ingin diproses di folder `video/`, lalu jalankan satu perintah di terminal. Hasil gambar masuk ke `output/`, dengan satu subfolder untuk tiap video.

## Menjalankan di Windows

1. Pasang Python 3 dan FFmpeg. Pastikan perintah `py -3 --version` dan `ffmpeg -version` bisa dijalankan di PowerShell. FFmpeg harus ada di `PATH`.
2. Salin semua video ke folder `video/` di project ini.
3. Buka PowerShell atau Windows Terminal, lalu jalankan:

   ```powershell
   cd D:\GitHub\ffmpeg-converter
   py -3 convert.py
   ```

Perintah itu mengekstrak **semua frame** menjadi JPG. Hasilnya akan seperti ini:

```text
output/
├── nama-video-1/
│   ├── frame_000001.jpg
│   ├── frame_000002.jpg
│   └── ...
└── nama-video-2/
    ├── frame_000001.jpg
    └── ...
```

Kalau FFmpeg belum masuk `PATH`, jalankan dengan path lengkap ke executable-nya:

```powershell
py -3 convert.py --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe"
```

## Pilihan tambahan

- Ambil satu frame per detik: `py -3 convert.py --interval 1`
- Ambil satu frame setiap setengah detik: `py -3 convert.py --interval 0.5`
- Simpan sebagai PNG: `py -3 convert.py --format png`
- Pilih kualitas JPG (1 paling baik, 31 file lebih kecil): `py -3 convert.py --quality 2`
- Jalankan `py -3 convert.py --help` untuk daftar opsi.

Kalau dijalankan lagi, gambar frame lama di folder video tersebut akan diganti. File lain di folder output tetap dibiarkan. Ekstraksi semua frame dapat menghasilkan ribuan gambar dan memakai banyak ruang disk.
