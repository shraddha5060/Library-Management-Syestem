# utils.py
from datetime import datetime, date, timedelta

def today_iso():
    return date.today().isoformat()

def parse_iso(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()

def add_days_iso(s: str, days: int):
    d = parse_iso(s)
    return (d + timedelta(days=days)).isoformat()

def pretty_date_iso(s: str):
    d = parse_iso(s)
    return d.strftime("%d-%b-%Y")
