#!/usr/bin/env bash
set -euo pipefail

# You must make these match what is in config.py
BASE_URL="http://localhost"
QR_SECRET="choose_a_very_long_random_secret"

# Set output directory
OUTDIR="${1:-qr_out}"
mkdir -p "$OUTDIR"

# List of codes to generate QR codes for
codes=(
    E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 
    E11 E12 E13 E14 E15 E16 E17 E18 E19 E20 
    E21 E22 E23 E24 S01 S02 S03
)

# Generate QR codes
for code in "${codes[@]}"; do
    sig=$(echo -n "$code" | openssl dgst -sha256 -hmac "$QR_SECRET" | cut -d" " -f2)
    url="${BASE_URL}/cgi/scan.cgi?code=${code}&sig=${sig}"
    output_file="${OUTDIR}/${code}.png"
    
    qrencode -o "$output_file" "$url"
    echo "Generated $output_file -> $url"
done
