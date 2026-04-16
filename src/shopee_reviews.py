from __future__ import annotations

import json
import re
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

import pandas as pd

DEFAULT_TIMEOUT = 15
PAGE_SIZE = 50
ID_PATTERNS = (
    re.compile(r"i\.(\d+)\.(\d+)"),
    re.compile(r"/product/(\d+)/(\d+)"),
)
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}


class ShopeeReviewError(Exception):
    pass


def _ensure_scheme(url: str) -> str:
    normalized = url.strip()
    if not normalized:
        raise ShopeeReviewError("Vui long nhap link san pham Shopee.")
    if "://" not in normalized:
        normalized = f"https://{normalized}"
    return normalized


def _is_shopee_host(host: str) -> bool:
    return "shopee." in host.lower()


def extract_ids_from_url(url: str) -> tuple[int, int]:
    normalized = _ensure_scheme(url)

    for pattern in ID_PATTERNS:
        match = pattern.search(normalized)
        if match:
            return int(match.group(1)), int(match.group(2))

    parsed = urlparse(normalized)
    query = parse_qs(parsed.query)
    shop_id = query.get("shopid", query.get("shop_id", [None]))[0]
    item_id = query.get("itemid", query.get("item_id", [None]))[0]

    if shop_id and item_id:
        return int(shop_id), int(item_id)

    raise ShopeeReviewError(
        "Khong doc duoc shop_id va item_id tu link Shopee. "
        "Hay dung link san pham day du."
    )


def resolve_product_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    normalized = _ensure_scheme(url)
    parsed = urlparse(normalized)
    if not _is_shopee_host(parsed.netloc):
        raise ShopeeReviewError("Link phai thuoc domain Shopee.")

    try:
        extract_ids_from_url(normalized)
        return normalized
    except ShopeeReviewError:
        pass

    request = Request(normalized, headers=DEFAULT_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.geturl()
    except (HTTPError, URLError) as exc:
        raise ShopeeReviewError("Khong the mo link san pham Shopee.") from exc


def build_reviews_dataframe(
    ratings: Iterable[dict],
    shop_id: int,
    item_id: int,
    source_url: str,
) -> pd.DataFrame:
    records = []
    seen_ids = set()

    for rating in ratings:
        comment = str(rating.get("comment") or "").strip()
        if not comment:
            continue

        review_id = rating.get("cmtid") or (
            rating.get("userid"),
            rating.get("ctime"),
            comment,
        )
        if review_id in seen_ids:
            continue
        seen_ids.add(review_id)

        records.append(
            {
                "comment": comment,
                "rating_star": rating.get("rating_star"),
                "author_username": rating.get("author_username"),
                "created_at": rating.get("ctime"),
                "shop_id": shop_id,
                "item_id": item_id,
                "source_url": source_url,
            }
        )

    dataframe = pd.DataFrame.from_records(records)
    if dataframe.empty:
        return dataframe

    dataframe["created_at"] = pd.to_datetime(
        dataframe["created_at"], unit="s", errors="coerce"
    )
    return dataframe


def _load_json(url: str, headers: dict, timeout: int) -> dict:
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        raise ShopeeReviewError("Khong the lay du lieu danh gia tu Shopee.") from exc


def _fetch_ratings_page(
    origin: str,
    shop_id: int,
    item_id: int,
    offset: int,
    limit: int,
    referer: str,
    timeout: int,
) -> dict:
    query = urlencode(
        {
            "filter": 0,
            "flag": 1,
            "itemid": item_id,
            "limit": limit,
            "offset": offset,
            "shopid": shop_id,
            "type": 0,
        }
    )
    headers = {**DEFAULT_HEADERS, "Referer": referer}
    endpoints = (
        f"{origin}/api/v4/item/get_ratings?{query}",
        f"{origin}/api/v2/item/get_ratings?{query}",
    )

    last_error = None
    for endpoint in endpoints:
        try:
            payload = _load_json(endpoint, headers=headers, timeout=timeout)
        except ShopeeReviewError as exc:
            last_error = exc
            continue

        data = payload.get("data") or {}
        ratings = data.get("ratings")
        if ratings is not None:
            return data

    if last_error is not None:
        raise last_error

    raise ShopeeReviewError("Shopee da thay doi API lay danh gia.")


def fetch_product_reviews(
    product_url: str,
    max_reviews: int = 100,
    timeout: int = DEFAULT_TIMEOUT,
) -> pd.DataFrame:
    if max_reviews <= 0:
        raise ShopeeReviewError("So luong binh luan can lon hon 0.")

    resolved_url = resolve_product_url(product_url, timeout=timeout)
    parsed = urlparse(resolved_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    shop_id, item_id = extract_ids_from_url(resolved_url)

    dataframes = []
    collected = 0
    offset = 0

    while collected < max_reviews:
        limit = min(PAGE_SIZE, max_reviews - collected)
        page = _fetch_ratings_page(
            origin=origin,
            shop_id=shop_id,
            item_id=item_id,
            offset=offset,
            limit=limit,
            referer=resolved_url,
            timeout=timeout,
        )
        ratings = page.get("ratings") or []
        if not ratings:
            break

        frame = build_reviews_dataframe(
            ratings=ratings,
            shop_id=shop_id,
            item_id=item_id,
            source_url=resolved_url,
        )
        if not frame.empty:
            remaining = max_reviews - collected
            frame = frame.head(remaining)
            dataframes.append(frame)
            collected += len(frame)

        has_more = bool(page.get("has_more"))
        next_offset = page.get("next_offset")
        if isinstance(next_offset, int) and next_offset > offset:
            offset = next_offset
        else:
            offset += len(ratings)

        if not has_more or len(ratings) < limit:
            break

    if not dataframes:
        raise ShopeeReviewError(
            "Khong lay duoc binh luan co noi dung tu link nay. "
            "Link co the khong hop le hoac Shopee dang chan truy cap."
        )

    combined = pd.concat(dataframes, ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["author_username", "created_at", "comment"],
        keep="first",
    )
    return combined.reset_index(drop=True)
