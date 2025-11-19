#!/usr/bin/env python3

import os, cgi, http.cookies
import hmac, hashlib
from config import QR_SECRET

from db import get_db
from common import render_template, print_html

def main():
    form = cgi.FieldStorage()
    code = form.getfirst("code", "").strip()
    sig = form.getfirst("sig", "").strip()
    cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE", ""))
    email = cookie["attendee_email"].value if "attendee_email" in cookie else None
    
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if not code:
        print_html(render_template("scan.html", message="Missing QR code parameter."))
        return

    if not email:
        if "email" in form:
            email = form.getfirst("email", "").strip().lower()
            print_html("", cookies={"attendee_email": email}, status="303 See Other", 
                       location=f"/cgi/scan.cgi?code={code}")
            return
        print_html(render_template("email_prompt.html", code=code))
        return
    
    if not valid_sig(code, sig):
        print_html(render_template("scan.html", message="Invalid or tampered QR code."))
        return

    cur.execute("SELECT id, name, type FROM places WHERE code=%s", (code,))
    place = cur.fetchone()

    if not place:
        print_html(render_template("scan.html", message="Invalid QR code."))
        return

    cur.execute("INSERT IGNORE INTO attendees (email) VALUES (%s)", (email,))
    conn.commit()
    cur.execute("SELECT id FROM attendees WHERE email=%s", (email,))
    attendee_id = cur.fetchone()["id"]

    cur.execute("INSERT IGNORE INTO scans (attendee_id, place_id) VALUES (%s, %s)", 
                (attendee_id, place["id"]))
    conn.commit()

    # INSERT IGNORE returns rowcount=0 when the record already exists, i.e., duplicate scan.
    duplicate_scan = (cur.rowcount == 0)

    cur.execute("SELECT SUM(p.type='exhibitor') exhibitors, SUM(p.type='session') sessions "
                "FROM scans s JOIN places p ON p.id=s.place_id WHERE s.attendee_id=%s", 
                (attendee_id,))
    p = cur.fetchone() or {"exhibitors": 0, "sessions": 0}
    q = (p["exhibitors"] >= 12 and p["sessions"] >= 3)

    print_html(render_template("scan.html", place=place, email=email, 
                               exhibitors=p["exhibitors"], sessions=p["sessions"], 
                               qualified=q, duplicate_scan=duplicate_scan))

    cur.close()
    conn.close()

def valid_sig(code, sig):
    expected = hmac.new(QR_SECRET.encode(), code.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)

if __name__=="__main__": main()
