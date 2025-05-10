import re
# 공연제목
TITLE_PATTERS = [

]

# 공연날짜
DATE_PATTERNS = [
    r'(\d{4}[.\-/년 ]\s*\d{1,2}[.\-/월 ]\s*\d{1,2}[일]?)',
    r'(\d{1,2}[.\-/월 ]\s*\d{1,2}[일]?)',
    r'(\d{2}[.]\d{2}[.]\d{2})'
]

# 공연시간
TIME_PATTERNS = [
    r'(오전|오후|저녁|밤|AM|PM)?\s*\d{1,2}[:시]\s*(\d{2})?',
    r'\d{1,2}:\d{2}'
]

# 라인업
LINEUP_PATTERS = [

]

# 가격
PRICE_PATTERNS = [
    r'(예매|현매)?\s*[0-9,]+[원]?'
]

# 가격(현장)
PRICE_ONSITE_PATTERNS = [

]

# 티켓오픈날짜/시긴
TICKET_OPEN_PATTERS = [

]

# 티켓링크
TICKET_LINK_PATTERNS = [
    r'(https?://[^\s]+)'
]