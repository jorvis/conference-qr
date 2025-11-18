#!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader, select_autoescape
from config import CONFERENCE_NAME

env=Environment(loader=FileSystemLoader("/var/www/html/templates"),autoescape=select_autoescape(["html","xml"]))

def render_template(name,**ctx):
    ctx.setdefault("conference_name",CONFERENCE_NAME)
    return env.get_template(name).render(**ctx)

def print_html(content,cookies=None,status=None,location=None):
    h=["Content-Type: text/html; charset=utf-8"]

    if cookies:
        for k,v in cookies.items(): h.append(f"Set-Cookie: {k}={v}; Path=/; Max-Age=31536000")
        
    if status: h.append(f"Status: {status}")
    
    if location: h.append(f"Location: {location}")
    
    print("\r\n".join(h)+"\r\n"); print(content)
