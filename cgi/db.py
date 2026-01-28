#!/usr/bin/env python3

from config import DB_CONFIG
import pymysql

def get_db(): 
    return pymysql.connect(**DB_CONFIG)
