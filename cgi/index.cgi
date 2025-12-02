#!/usr/bin/env python3

import os
import http.cookies
from config import EXHIBITORS_REQUIRED, SESSIONS_REQUIRED
from common import render_template, print_html

def main():
    cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE", ""))
    has_email = "attendee_email" in cookie
    user_email = cookie["attendee_email"].value if has_email else ""
    
    print_html(render_template("index.html", has_email=has_email, user_email=user_email,
                               exhibitors_required=EXHIBITORS_REQUIRED, sessions_required=SESSIONS_REQUIRED))

if __name__ == "__main__":
    main()
