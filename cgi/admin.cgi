#!/usr/bin/env python3

import cgi
import random
import pymysql.cursors
from db import get_db
from config import ADMIN_KEY, EXHIBITORS_REQUIRED, SESSIONS_REQUIRED
from common import render_template, print_html

def main():
    form=cgi.FieldStorage();
    key=form.getfirst("key","")

    if key != ADMIN_KEY: 
        print_html(render_template("admin.html", unauthorized=True))
        return
    
    conn=get_db(); 
    cur=conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT COUNT(*) c FROM attendees"); attendees=cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) c FROM scans"); scans=cur.fetchone()["c"]

    leaderboard_query = """
        SELECT a.email, a.name,
            SUM(p.type='exhibitor') AS exhibitors,
            SUM(p.type='session') AS sessions
        FROM attendees a
        LEFT JOIN scans s ON s.attendee_id = a.id
        LEFT JOIN places p ON p.id = s.place_id
        GROUP BY a.email, a.name
        ORDER BY sessions DESC, exhibitors DESC
    """
    cur.execute(leaderboard_query)
    
    leaderboard=cur.fetchall()

    # Find qualified winners (those who scanned all required items)
    qualified = [
        row for row in leaderboard
        if (row['exhibitors'] or 0) >= EXHIBITORS_REQUIRED and (row['sessions'] or 0) >= SESSIONS_REQUIRED
    ]
    
    # Randomly select up to 2 winners
    winners = random.sample(qualified, min(2, len(qualified))) if qualified else []

    print_html(render_template("admin.html", 
                               attendees=attendees, 
                               scans=scans, 
                               leaderboard=leaderboard,
                               winners=winners,
                               admin_key=key))

if __name__=="__main__": main()
