# app/scraping/question_scraper.py
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
from app.models.question import Question

DATA_DIR = Path("data/raw/questions")


@dataclass(frozen=True)
class QuestionItem:
    question_text: str


# ---------- 공통 유틸 ----------
def _dedupe(items: List[QuestionItem]) -> List[QuestionItem]:
    seen: set[str] = set()
    out: List[QuestionItem] = []
    for it in items:
        t = it.question_text.strip()
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(QuestionItem(question_text=t))
    return out


def _save_to_file(items: List[QuestionItem]) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = DATA_DIR / f"questions-{ts}.json"
    payload = [{"question_text": it.question_text} for it in items]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


async def _upsert_to_db(items: List[QuestionItem]) -> int:
    created = 0
    for it in items:
        if await Question.filter(question_text=it.question_text).exists():
            continue
        await Question.create(question_text=it.question_text)
        created += 1
    return created


# ---------- HTML 모드 ----------
def _parse_html_page(
    html: str,
    base_url: str,
    item_selector: str,
    text_selector: Optional[str],
    next_selector: Optional[str],
) -> Tuple[List[QuestionItem], Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[QuestionItem] = []

    for node in soup.select(item_selector):
        text_node = node.select_one(text_selector) if text_selector else node
        if not text_node:
            continue
        text = text_node.get_text(strip=True)
        if text:
            items.append(QuestionItem(question_text=text))

    next_url = None
    if next_selector:
        next_a = soup.select_one(next_selector)
        if next_a and next_a.has_attr("href"):
            next_url = urljoin(base_url, next_a["href"])

    return items, next_url


async def _scrape_html(
    start_url: str,
    item_selector: str,
    text_selector: Optional[str],
    next_selector: Optional[str],
    max_pages: Optional[int],
) -> List[QuestionItem]:
    url = start_url
    page = 0
    out: List[QuestionItem] = []

    async with httpx.AsyncClient(
        timeout=30, headers={"User-Agent": "DiaryScraper/1.0"}
    ) as client:
        while url:
            page += 1
            r = await client.get(url)
            r.raise_for_status()
            items, next_url = _parse_html_page(
                r.text, start_url, item_selector, text_selector, next_selector
            )
            out.extend(items)
            if max_pages and page >= max_pages:
                break
            url = next_url
    return _dedupe(out)


# ---------- JSON 모드 ----------
def _get_by_path(obj, path: str):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list) and part.isdigit():
            cur = cur[int(part)]
        else:
            return None
    return cur


async def _scrape_json(url: str, list_path: str, field: str) -> List[QuestionItem]:
    async with httpx.AsyncClient(
        timeout=30, headers={"User-Agent": "DiaryScraper/1.0"}
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    rows = _get_by_path(data, list_path)
    items: List[QuestionItem] = []
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and row.get(field):
                items.append(QuestionItem(question_text=str(row[field]).strip()))
    return _dedupe(items)


# ---------- CLI ----------
async def main():
    parser = argparse.ArgumentParser(
        description="Scrape self-reflection questions and store into DB"
    )
    parser.add_argument("--mode", choices=["html", "json"], required=True)
    parser.add_argument(
        "--url", required=True, help="Start URL (HTML page or JSON endpoint)"
    )
    parser.add_argument("--store", choices=["db", "file", "both"], default="db")

    # HTML 옵션
    parser.add_argument(
        "--item-selector", help="CSS selector for each question container (HTML)"
    )
    parser.add_argument(
        "--text-selector", help="CSS selector under item for the text (HTML) [optional]"
    )
    parser.add_argument(
        "--next-selector",
        help="CSS selector to find the 'next page' link (HTML) [optional]",
    )
    parser.add_argument("--max-pages", type=int, default=None)

    # JSON 옵션
    parser.add_argument(
        "--list-path", help="Dot-path to the list in JSON (e.g. data.items)"
    )
    parser.add_argument(
        "--field", help="Field name containing question text in each item"
    )

    args = parser.parse_args()

    if args.mode == "html":
        if not args.item_selector:
            raise SystemExit("--item-selector is required for HTML mode")
        items = await _scrape_html(
            start_url=args.url,
            item_selector=args.item_selector,
            text_selector=args.text_selector,
            next_selector=args.next_selector,
            max_pages=args.max_pages,
        )
    else:
        if not (args.list_path and args.field):
            raise SystemExit("--list-path and --field are required for JSON mode")
        items = await _scrape_json(args.url, args.list_path, args.field)

    print(f"Scraped {len(items)} unique questions")

    if args.store in ("file", "both"):
        path = _save_to_file(items)
        print(f"Saved file: {path}")

    if args.store in ("db", "both"):
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        try:
            created = await _upsert_to_db(items)
            print(f"DB inserted new rows: {created}")
        finally:
            await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
