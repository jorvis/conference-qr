#!/usr/bin/env python3
"""
Insert rows into the QR code scan log table for one user as if they
scanned all QR codes.  This is useful for testing purposes.
"""

import os
import sys
import pymysql.cursors

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cgi'))
from config import BASE_URL, QR_SECRET
from db import get_db



def main():
    if len(sys.argv) < 3:
        print("Usage: scan_all.py <email> <name>", file=sys.stderr)
        print("  email: The attendee's email address", file=sys.stderr)
        print("  name: The attendee's name", file=sys.stderr)
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    name = sys.argv[2].strip()
    
    try:
        conn = get_db()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        # Insert or get the attendee
        cur.execute("INSERT IGNORE INTO attendees (email, name) VALUES (%s, %s)", (email, name))
        conn.commit()
        
        cur.execute("SELECT id FROM attendees WHERE email=%s", (email,))
        attendee = cur.fetchone()
        
        if not attendee:
            print(f"Error: Failed to create or find attendee with email {email}", file=sys.stderr)
            sys.exit(1)
        
        attendee_id = attendee["id"]
        
        # Get all places
        cur.execute("SELECT id, code, name, type FROM places ORDER BY code")
        places = cur.fetchall()
        
        if not places:
            print("Error: No places found in database", file=sys.stderr)
            sys.exit(1)
        
        # Insert scans for all places
        inserted_count = 0
        for place in places:
            cur.execute("INSERT IGNORE INTO scans (attendee_id, place_id) VALUES (%s, %s)",
                       (attendee_id, place["id"]))
            if cur.rowcount > 0:
                inserted_count += 1
        
        conn.commit()
        
        print(f"Successfully inserted {inserted_count} scans for {email} ({name})")
        print(f"Total places in database: {len(places)}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
