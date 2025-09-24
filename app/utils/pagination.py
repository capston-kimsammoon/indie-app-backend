from typing import List

def paginate(items: List, page: int, size: int):
    start = (page - 1) * size
    end = start + size
    paginated = items[start:end]
    total_pages = (len(items) + size - 1) // size
    return paginated, total_pages
