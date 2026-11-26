
# Prite Itik FFmpeg

Mesin produksi video MP4 otomatis untuk channel YouTube Prite Itik.

## Fitur
- Membuat video vertikal 1080x1920.
- Format MP4 H.264.
- Gerakan kamera otomatis pada gambar.
- Menambahkan audio narasi atau musik.
- Durasi video 10 sampai 90 detik.
- Menggunakan FFmpeg.

## Server
Aplikasi berjalan pada port 7860.

## API
- GET / : Memeriksa status server.
- POST /render : Membuat video MP4 dari gambar dan audio.

## Teknologi
- Python
- Flask
- FFmpeg
- Gunicorn
- 
