# app/scraping/quote_scraper.py
import argparse
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from tortoise import Tortoise

from app.db.database import TORTOISE_ORM
from app.models.quote import Quote

DATA_DIR = Path("data/raw/quotes")


@dataclass(frozen=True)
class QuoteItem:
    content: str
    author: Optional[str] = None


# ---------- HTML 파싱 ----------
def _parse_page(html: str, base_url: str) -> Tuple[List[QuoteItem], Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[QuoteItem] = []
    for q in soup.select(".quote"):
        text_el = q.select_one(".text")
        if not text_el:
            continue
        text = text_el.get_text(strip=True)
        # 사이트 특성상 양쪽에 “ ” 가 붙는 경우가 있어 제거
        text = text.strip("“”\"' \n\t")
        author_el = q.select_one(".author")
        author = author_el.get_text(strip=True) if author_el else None
        items.append(QuoteItem(content=text, author=author or None))

    next_a = soup.select_one("li.next > a")
    next_url = (
        urljoin(base_url, next_a["href"])
        if next_a and next_a.has_attr("href")
        else None
    )
    return items, next_url


# ---------- 수집 ----------
async def scrape_quotes(
    base_url: str, max_pages: Optional[int] = None
) -> List[QuoteItem]:
    """
    quotes.toscrape.com 페이지네이션을 따라가며 전부 수집.
    max_pages 지정 시 해당 페이지 수까지만 수집.
    """
    out: List[QuoteItem] = []
    url = base_url
    page = 0
    async with httpx.AsyncClient(
        timeout=30, headers={"User-Agent": "DiaryScraper/1.0"}
    ) as client:
        while url:
            page += 1
            r = await client.get(url)
            r.raise_for_status()
            items, next_url = _parse_page(r.text, base_url)
            out.extend(items)
            if max_pages and page >= max_pages:
                break
            url = next_url
    # 중복 제거 (content+author 기준)
    seen: set[tuple[str, Optional[str]]] = set()
    uniq: List[QuoteItem] = []
    for it in out:
        key = (it.content, it.author)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(it)
    return uniq


# ---------- 저장 ----------
def save_to_file(items: List[QuoteItem]) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = DATA_DIR / f"quotes-{ts}.json"
    payload = [{"content": it.content, "author": it.author} for it in items]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


async def upsert_to_db(items: List[QuoteItem]) -> int:
    """
    content+author 조합으로 중복을 피하며 insert.
    (모델에 unique 제약이 없어도 애플리케이션 레벨에서 중복 방지)
    """
    existing = {(c, a) for c, a in await Quote.all().values_list("content", "author")}
    to_create = [
        Quote(content=it.content, author=it.author or "")
        for it in items
        if (it.content, it.author) not in existing
    ]
    if not to_create:
        return 0
    await Quote.bulk_create(to_create, batch_size=200)
    return len(to_create)


# ---------- CLI ----------
async def main():
    parser = argparse.ArgumentParser(
        description="Scrape quotes.toscrape.com and store into DB"
    )
    parser.add_argument(
        "--base-url",
        default="https://quotes.toscrape.com/",
        help="Base URL to start scraping",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit the number of pages to scrape",
    )
    parser.add_argument("--store", choices=["db", "file", "both"], default="db")
    args = parser.parse_args()

    items = await scrape_quotes(args.base_url, args.max_pages)
    print(f"Scraped {len(items)} unique quotes")

    if args.store in ("file", "both"):
        path = save_to_file(items)
        print(f"Saved file: {path}")

    if args.store in ("db", "both"):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        try:
            created = await upsert_to_db(items)
            print(f"DB inserted new rows: {created}")
        finally:
            await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
