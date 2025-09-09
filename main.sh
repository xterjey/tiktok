#!/bin/bash

set -e

# Update dan upgrade sistem
sudo apt update && sudo apt upgrade -y

# Install ffmpeg (wajib untuk merge video+audio)
sudo apt install -y ffmpeg

# Install pip jika belum ada
if ! command -v pip &> /dev/null; then
    sudo apt install -y python3-pip
fi

# Install / upgrade yt-dlp
pip install --upgrade yt-dlp

echo "Selesai instalasi!"

# Periksa yt-dlp
if ! command -v yt-dlp &> /dev/null; then
    echo "yt-dlp tidak ditemukan! Silakan install terlebih dahulu."
    exit 1
fi

# Input URL
echo -n "Masukkan URL video: "
read -r video_url

# Cek cookies
cookies_arg=""
if [[ -f "cookies.txt" ]]; then
    cookies_arg="--cookies cookies.txt"
fi

# Tampilkan semua format
yt-dlp -F "$video_url" $cookies_arg

# Pilih format video (wajib)
echo -n "Masukkan format video yang diinginkan: "
read -r video_format

if [[ -z "$video_format" ]]; then
    echo "Format video wajib diisi!"
    exit 1
fi

# Merge video + bestaudio
format_choice="$video_format+bestaudio"

# Nama output
echo -n "Masukkan nama file output (tekan enter untuk default output.mp4): "
read -r output_name
output_name=${output_name:-output.mp4}

# Download & merge (yt-dlp otomatis pakai ffmpeg)
yt-dlp -f "$format_choice" "$video_url" $cookies_arg -o "$output_name"

echo "✅ Download & merge selesai! File tersimpan sebagai $output_name"

# Jalankan script Python (jika ada)
if [[ -f "TiktokStreamKeyGenerator.py" ]]; then
    python3 TiktokStreamKeyGenerator.py
else
    echo "⚠️ TiktokStreamKeyGenerator.py tidak ditemukan, dilewati."
fi

# Jalankan ffmpeg.py dengan file hasil download
if [[ -f "ffmpeg.py" ]]; then
    python3 ffmpeg.py "$output_name" ----load-url
else
    echo "⚠️ ffmpeg.py tidak ditemukan, dilewati."
fi
