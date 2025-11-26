#!/usr/bin/env python3
"""
Generate QR codes for conference exhibitors and sessions.
Reads configuration from config.py for consistency.
"""

import os
import sys
import hmac
import hashlib
import subprocess

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cgi'))
from config import BASE_URL, QR_SECRET

def generate_signature(code, secret):
    """Generate HMAC-SHA256 signature for a code."""
    return hmac.new(secret.encode(), code.encode(), hashlib.sha256).hexdigest()

def generate_qr_code(code, output_dir):
    """Generate a QR code for the given code."""
    sig = generate_signature(code, QR_SECRET)
    url = f"{BASE_URL}/cgi/scan.cgi?code={code}&sig={sig}"
    output_file = os.path.join(output_dir, f"{code}.png")
    
    try:
        subprocess.run(
            ['qrencode', '-o', output_file, url],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Generated {output_file} -> {url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating {output_file}: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: qrencode command not found. Please install it:", file=sys.stderr)
        print("  Ubuntu/Debian: sudo apt-get install qrencode", file=sys.stderr)
        print("  macOS: brew install qrencode", file=sys.stderr)
        sys.exit(1)

def main():
    # Set output directory
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "qr_out"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # List of codes to generate QR codes for
    codes = [
        'E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08', 'E09', 'E10',
        'E11', 'E12', 'E13', 'E14', 'E15', 'E16', 'E17', 'E18', 'E19', 'E20',
        'E21', 'E22', 'E23', 'E24', 'S01', 'S02', 'S03'
    ]
    
    print(f"Generating QR codes using:")
    print(f"  BASE_URL: {BASE_URL}")
    print(f"  Output directory: {output_dir}")
    print()
    
    # Generate QR codes
    success_count = 0
    for code in codes:
        if generate_qr_code(code, output_dir):
            success_count += 1
    
    print()
    print(f"Successfully generated {success_count}/{len(codes)} QR codes")

if __name__ == "__main__":
    main()
