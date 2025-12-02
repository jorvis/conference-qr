#!/usr/bin/env python3

import os, cgi
from db import get_db
from common import render_template, print_html

def main():
    form = cgi.FieldStorage()
    email = form.getfirst("email", "").strip().lower()

    if not email:
        print_html(render_template("progress.html", no_email=True))
        return

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, name FROM attendees WHERE email=%s", (email,)
    )

    row = cur.fetchone()
    
    if not row:
        print_html(render_template("progress.html", email=email, not_found=True))
        return

    aid = row["id"]
    attendee_name = row["name"]
    
    cur.execute(
        "SELECT SUM(p.type='exhibitor') exhibitors, "
        "SUM(p.type='session') sessions FROM scans s "
        "JOIN places p ON s.place_id=p.id WHERE s.attendee_id=%s",
        (aid,)
    )
    p = cur.fetchone() or {"exhibitors": 0, "sessions": 0}

    q = p["exhibitors"] >= 12 and p["sessions"] >= 3
    
    # Get all exhibitors with scan status
    cur.execute("""
        SELECT p.id, p.name, p.type, 
               IF(s.id IS NOT NULL, 1, 0) as scanned
        FROM places p
        LEFT JOIN scans s ON s.place_id = p.id AND s.attendee_id = %s
        WHERE p.type = 'exhibitor'
        ORDER BY p.name
    """, (aid,))
    exhibitor_list = cur.fetchall()

    # Get all sessions with scan status
    cur.execute("""
        SELECT p.id, p.name, p.type, 
               IF(s.id IS NOT NULL, 1, 0) as scanned
        FROM places p
        LEFT JOIN scans s ON s.place_id = p.id AND s.attendee_id = %s
        WHERE p.type = 'session'
        ORDER BY p.name
    """, (aid,))
    session_list = cur.fetchall()

    print_html(render_template(
        "progress.html",
        email=email,
        attendee_name=attendee_name,
        exhibitors=p["exhibitors"],
        sessions=p["sessions"],
        qualified=q,
        exhibitor_list=exhibitor_list,
        session_list=session_list
    ))
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
