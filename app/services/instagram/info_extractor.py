# app/services/instagram/info_extractor.py

import re
# from dateutil import parser
from .patterns import DATE_PATTERNS, TIME_PATTERNS, PRICE_PATTERNS, TICKET_LINK_PATTERNS
from .utils import find_first_match

# 공연제목
def extract_title(text):
    return ""

# 공연날짜
def extract_date(text):
    return find_first_match(text, DATE_PATTERNS)

# 공연시간
def extract_time(text):
    return find_first_match(text, TIME_PATTERNS)

# 라인업
def extract_lineup(text):
    lines = text.splitlines()
    artists = []
    return artists

# 가격
def extract_price(text):
    return re.findall(PRICE_PATTERN, text)

# 가격(현장예매 다를 경우)
def extract_price_onsite(text):
    return re.findall(PRICE_PATTERN, text)

# 티켓오픈날짜
def extract_ticket_open_date(text):
    return ""

# 티켓오픈시간
def extract_ticket_open_time(text):
    return ""

def extract_performance_info(text):
    return {
        "title": extract_title(text),
        "date": extract_date(text),
        "time": extract_time(text),
        "lineup": extract_lineup(text),
        "price": extract_price(text),
        "price_onsite": extract_price_onsite(text),
        "ticket_open_date": extract_ticket_open_date(text),
        "ticket_open_time": extract_ticket_open_time(text),
    }
