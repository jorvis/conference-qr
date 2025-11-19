#!/usr/bin/env python3

import os, cgi
from db import get_db
from config import ADMIN_KEY
from common import render_template, print_html

def main():
    form = cgi.FieldStorage()
    key = form.getfirst("key", "")
    email = form.getfirst("email", "").strip().lower()

    if key != ADMIN_KEY: 
        print_html(render_template("admin.html", unauthorized=True))
        return

    if form.getfirst("email"):
        email = form.getfirst("email").strip().lower()
    if not email:
        print_html(render_template("progress.html", no_email=True))
        return

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id FROM attendees WHERE email=%s", (email,)
    )

    row = cur.fetchone()
    
    if not row:
        print_html(render_template("progress.html", email=email, not_found=True))
        return

    aid = row["id"]
    cur.execute(
        "SELECT SUM(p.type='exhibitor') exhibitors, "
        "SUM(p.type='session') sessions FROM scans s "
        "JOIN places p ON s.place_id=p.id WHERE s.attendee_id=%s",
        (aid,)
    )
    p = cur.fetchone() or {"exhibitors": 0, "sessions": 0}

    q = p["exhibitors"] >= 12 and p["sessions"] >= 3
    cur.execute(
        "SELECT p.code, p.name, p.type, s.scanned_at FROM scans s "
        "JOIN places p ON s.place_id=p.id WHERE s.attendee_id=%s "
        "ORDER BY s.scanned_at DESC",
        (aid,)
    )
    scanned = cur.fetchall()

    print_html(render_template(
        "progress.html",
        email=email,
        exhibitors=p["exhibitors"],
        sessions=p["sessions"],
        qualified=q,
        scanned=scanned
    ))
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
