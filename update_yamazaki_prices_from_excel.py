#!/usr/bin/env python3
"""Update Yamazaki prices from the Excel price list.

- Updates modal/cart data in assets/products.json
- Updates visible catalog prices in Markalar/Yamazaki/index.html

It matches Excel rows (MARKA contains 'YAMAZ') to products.json entries by the
trailing numeric part of the stock code (e.g. 'YM 1688' -> tail '1688' -> 'WH1688').

For composite SKUs in HTML (e.g. 'WH1688,BK1689'), it updates the displayed price
only when all variants have the same Excel price.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


@dataclass(frozen=True)
class UpdateResult:
    updated_products: int
    updated_html_blocks: int
    skipped_html_blocks: int
    missing_excel_rows: int


def _parse_item_positions_from_css(css_text: str) -> dict[str, tuple[float, float]]:
    positions: dict[str, tuple[float, float]] = {}
    # Example:
    # #item310602 {
    # 	left:352px !important;
    # 	top:159px !important;
    # }
    for match in re.finditer(r"#(?P<id>item\d+)\s*\{(?P<body>[^}]+)\}", css_text, re.DOTALL):
        item_id = match.group("id")
        body = match.group("body")
        left_match = re.search(r"\bleft\s*:\s*(?P<val>-?\d+(?:\.\d+)?)px", body)
        top_match = re.search(r"\btop\s*:\s*(?P<val>-?\d+(?:\.\d+)?)px", body)
        if not left_match or not top_match:
            continue
        positions[item_id] = (float(left_match.group("val")), float(top_match.group("val")))
    return positions


def _tail_digits(text: str) -> str | None:
    match = re.search(r"(\d+)(?!.*\d)", text)
    return match.group(1) if match else None


def _norm_stock_code(value: Any) -> str:
    text = str(value).replace("\u00a0", " ")
    return " ".join(text.split())


def _format_try_currency(value: float) -> str:
    # Turkish formatting with thousands '.' and decimals ','
    # 9997.21 -> ₺9.997,21
    return "₺" + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _load_products(products_path: Path) -> list[dict[str, Any]]:
    with products_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_products(products_path: Path, products: list[dict[str, Any]]) -> None:
    with products_path.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _build_yamazaki_tail_index(products: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_tail: dict[str, list[dict[str, Any]]] = {}
    for product in products:
        if str(product.get("brand", "")).lower().startswith("yam"):
            sku = str(product.get("sku", ""))
            tail = _tail_digits(sku)
            if not tail:
                continue
            by_tail.setdefault(tail, []).append(product)
    return by_tail


def _read_excel_yamazaki_rows(excel_path: Path) -> pd.DataFrame:
    df = pd.read_excel(excel_path, sheet_name="KATALOG", header=1)
    df.columns = [str(c).strip() for c in df.columns]

    if "MARKA" not in df.columns or "STOK KODU" not in df.columns or "FİYAT" not in df.columns:
        raise ValueError(
            "Excel format unexpected: expected columns MARKA, STOK KODU, FİYAT in sheet 'KATALOG'."
        )

    df_y = df[df["MARKA"].astype(str).str.contains("YAMAZ", case=False, na=False)].copy()
    df_y["STOK_KODU_N"] = df_y["STOK KODU"].map(_norm_stock_code)
    df_y["TAIL"] = df_y["STOK_KODU_N"].map(_tail_digits)
    return df_y


def _update_products_from_excel(
    products: list[dict[str, Any]],
    excel_rows: pd.DataFrame,
) -> tuple[dict[str, float], int, int, list[dict[str, Any]]]:
    """Returns (sku_to_price, missing_excel_rows_count, changed_products_count, missing_rows_details)."""

    by_tail = _build_yamazaki_tail_index(products)

    sku_to_price: dict[str, float] = {}
    missing = 0
    missing_rows: list[dict[str, Any]] = []

    for _, row in excel_rows.iterrows():
        tail = row.get("TAIL")
        if not tail:
            missing += 1
            missing_rows.append(
                {
                    "stok_kodu": row.get("STOK_KODU_N"),
                    "fiyat": row.get("FİYAT"),
                    "urun_adi": row.get("ÜRÜN ADI"),
                    "reason": "no_tail_digits",
                }
            )
            continue

        matches = by_tail.get(str(tail), [])
        if len(matches) != 1:
            missing += 1
            missing_rows.append(
                {
                    "stok_kodu": row.get("STOK_KODU_N"),
                    "fiyat": row.get("FİYAT"),
                    "urun_adi": row.get("ÜRÜN ADI"),
                    "reason": "no_unique_product_match",
                    "matched_skus": [m.get("sku") for m in matches],
                }
            )
            continue

        price = float(row["FİYAT"])
        sku = str(matches[0].get("sku"))
        sku_to_price[sku] = price

    changed = 0
    for product in products:
        sku = str(product.get("sku", ""))
        if sku not in sku_to_price:
            continue

        price = sku_to_price[sku]
        price_display = _format_try_currency(price)

        # Only update if it actually changes, to keep diffs smaller.
        if product.get("price") == price and product.get("price_value") == price and product.get("price_display") == price_display:
            continue

        product["price"] = price
        product["price_value"] = price
        product["price_display"] = price_display
        changed += 1

    return sku_to_price, missing, changed, missing_rows


def _update_html_prices(html_text: str, sku_expr: str, new_price_display: str) -> tuple[str, int]:
    """Update the HTML price near a given sku expression.

    Returns (new_html_text, replacements_count).
    """

    sku_pat = re.escape(sku_expr)

    # Pattern A: in5 "add-to-cart" group block:
    # <div alt="₺..." ... class="pageItem group "><a ... sku:'SKU' ...> ... </a>
    #   <div ... alt="₺... "><span ...>₺...</span></div>
    pattern_group = re.compile(
        rf"(<div\s+alt=\")₺[^\"]+(\"[^>]*?class=\"pageItem\s+group\s*[^\"]*\"[^>]*>\s*<a[^>]*?sku:'{sku_pat}'[^>]*?>.*?</a>\s*<div[^>]*?alt=\")₺[^\"]+(\s*\"[^>]*?>\s*<span[^>]*?>)₺[^<]+(</span>)",
        re.DOTALL,
    )

    # Pattern B: simple anchor + price div (no group wrapper):
    # <a ... sku:'SKU' ...>...</a><div ... alt="₺..."><span>₺...</span></div>
    # Important: do not allow the match to "jump" over another <a> tag.
    pattern_simple = re.compile(
        rf"(<a[^>]*?sku:'{sku_pat}'[^>]*?>.*?</a>(?!\s*<a\b)\s*<div[^>]*?alt=\")₺[^\"]+(\s*\"[^>]*?>\s*<span[^>]*?>)₺[^<]+(</span>)",
        re.DOTALL,
    )

    def repl_group(match: re.Match[str]) -> str:
        return (
            match.group(1)
            + new_price_display
            + match.group(2)
            + new_price_display
            + " "
            + match.group(3)
            + new_price_display
            + match.group(4)
        )

    def repl_simple(match: re.Match[str]) -> str:
        return (
            match.group(1)
            + new_price_display
            + " "
            + match.group(2)
            + new_price_display
            + match.group(3)
        )

    new_text, count = pattern_group.subn(repl_group, html_text)
    if count and new_text != html_text:
        return new_text, count

    new_text2, count2 = pattern_simple.subn(repl_simple, html_text)
    changed2 = count2 if count2 and new_text2 != html_text else 0
    return new_text2, changed2


def _update_html_two_sku_two_price_blocks(
    html_text: str,
    sku_to_price: dict[str, float],
    item_positions: dict[str, tuple[float, float]],
) -> tuple[str, int, set[str]]:
    """Handle layout where two separate SKU anchors are followed by two price divs.

    Example (simplified):
      <a ... sku:'WH5611'>...</a><a ... sku:'BK5612'>...</a>
      <div alt="₺..."><span>₺...</span></div>
      <div alt="₺..."><span>₺...</span></div>

    Assumption: first price block corresponds to first SKU; second to second SKU.
    Returns (new_html_text, updated_block_count).
    """

    pattern = re.compile(
        r"(?P<a1><a[^>]*?sku:'(?P<sku1>[A-Z0-9]+)'[^>]*?>.*?<button[^>]*?\bid=\"(?P<btn1>item\d+)\"[^>]*?>.*?</a>)\s*"
        r"(?P<a2><a[^>]*?sku:'(?P<sku2>[A-Z0-9]+)'[^>]*?>.*?<button[^>]*?\bid=\"(?P<btn2>item\d+)\"[^>]*?>.*?</a>)\s*"
        r"(?P<p1_open><div[^>]*?\bid=\"(?P<p1id>item\d+)\"[^>]*?alt=\")(?P<p1alt>₺[^\"]+)(?P<p1_after>\"[^>]*?>\s*<span[^>]*?>)(?P<p1text>₺[^<]+)(?P<p1_close></span>\s*</div>)\s*"
        r"(?P<p2_open><div[^>]*?\bid=\"(?P<p2id>item\d+)\"[^>]*?alt=\")(?P<p2alt>₺[^\"]+)(?P<p2_after>\"[^>]*?>\s*<span[^>]*?>)(?P<p2text>₺[^<]+)(?P<p2_close></span>\s*</div>)",
        re.DOTALL,
    )

    changed = 0
    updated_skus: set[str] = set()

    def repl(match: re.Match[str]) -> str:
        nonlocal changed, updated_skus

        sku1 = match.group("sku1")
        sku2 = match.group("sku2")
        p1 = sku_to_price.get(sku1)
        p2 = sku_to_price.get(sku2)
        if p1 is None or p2 is None:
            return match.group(0)

        d_sku1 = _format_try_currency(p1)
        d_sku2 = _format_try_currency(p2)

        btn1 = match.group("btn1")
        btn2 = match.group("btn2")
        p1id = match.group("p1id")
        p2id = match.group("p2id")

        # Choose mapping based on CSS left positions (min total distance).
        def x(item_id: str) -> float | None:
            pos = item_positions.get(item_id)
            return pos[0] if pos else None

        btn1_x = x(btn1)
        btn2_x = x(btn2)
        p1_x = x(p1id)
        p2_x = x(p2id)

        # Default: p1->sku1, p2->sku2
        d1 = d_sku1
        d2 = d_sku2

        if None not in (btn1_x, btn2_x, p1_x, p2_x):
            cost_direct = abs(btn1_x - p1_x) + abs(btn2_x - p2_x)
            cost_swapped = abs(btn1_x - p2_x) + abs(btn2_x - p1_x)
            if cost_swapped < cost_direct:
                d1, d2 = d_sku2, d_sku1

        p1_alt_suffix = " " if match.group("p1alt").endswith(" ") else ""
        p2_alt_suffix = " " if match.group("p2alt").endswith(" ") else ""

        new = (
            match.group("a1")
            + match.group("a2")
            + match.group("p1_open")
            + d1
            + p1_alt_suffix
            + match.group("p1_after")
            + d1
            + match.group("p1_close")
            + match.group("p2_open")
            + d2
            + p2_alt_suffix
            + match.group("p2_after")
            + d2
            + match.group("p2_close")
        )

        if new != match.group(0):
            changed += 1
            updated_skus.update([sku1, sku2])

        return new

    new_text = pattern.sub(repl, html_text)
    return new_text, changed, updated_skus


def update(
    excel_path: Path,
    products_path: Path,
    html_path: Path,
    dry_run: bool,
    report_path: Path | None = None,
) -> UpdateResult:
    products = _load_products(products_path)
    excel_rows = _read_excel_yamazaki_rows(excel_path)

    sku_to_price, missing_excel_rows, changed_products, missing_rows = _update_products_from_excel(products, excel_rows)

    # Update HTML (paired blocks + single + composite)
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")

    css_path = html_path.parent / "assets" / "css" / "pages.css"
    item_positions: dict[str, tuple[float, float]] = {}
    if css_path.exists():
        item_positions = _parse_item_positions_from_css(
            css_path.read_text(encoding="utf-8", errors="ignore")
        )

    updated_html = 0
    skipped_html = 0

    # 0) Two SKU anchors followed by two price blocks (use CSS positions to map correctly)
    html_text, pair_updates, pair_updated_skus = _update_html_two_sku_two_price_blocks(
        html_text, sku_to_price, item_positions
    )
    if pair_updates:
        updated_html += pair_updates

    # 1) Single SKUs (avoid overriding pair-mapped blocks)
    for sku, price in sku_to_price.items():
        if sku in pair_updated_skus:
            continue
        price_display = _format_try_currency(price)
        html_text, count = _update_html_prices(html_text, sku, price_display)
        if count:
            updated_html += 1

    # 2) Composite SKU expressions, only if all parts share the same price
    composites = set(re.findall(r"sku:'([^']+,[^']+)'", html_text))
    skipped_composites: list[dict[str, Any]] = []
    for sku_expr in sorted(composites):
        parts = [p.strip() for p in sku_expr.split(",") if p.strip()]
        prices = [sku_to_price.get(p) for p in parts]
        if any(p is None for p in prices):
            skipped_html += 1
            skipped_composites.append(
                {
                    "sku_expr": sku_expr,
                    "reason": "missing_variant_price",
                    "parts": parts,
                    "prices": prices,
                }
            )
            continue
        if len(set(prices)) != 1:
            skipped_html += 1
            skipped_composites.append(
                {
                    "sku_expr": sku_expr,
                    "reason": "variant_prices_differ",
                    "parts": parts,
                    "prices": prices,
                }
            )
            continue

        price_display = _format_try_currency(prices[0])
        html_text, count = _update_html_prices(html_text, sku_expr, price_display)
        if count:
            updated_html += 1

    if not dry_run:
        _write_products(products_path, products)
        html_path.write_text(html_text, encoding="utf-8")

    if report_path is not None:
        report = {
            "updated_products": changed_products,
            "updated_html_blocks": updated_html,
            "skipped_html_blocks": skipped_html,
            "missing_excel_rows": missing_excel_rows,
            "missing_rows": missing_rows,
            "skipped_composites": skipped_composites,
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return UpdateResult(
        updated_products=changed_products,
        updated_html_blocks=updated_html,
        skipped_html_blocks=skipped_html,
        missing_excel_rows=missing_excel_rows,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--excel",
        default="İNTERAKTİF KATALOG FİYAT LİSTESİ 09.01.2026.xlsx",
        help="Excel file path (sheet 'KATALOG', header row index 1).",
    )
    parser.add_argument("--products", default="assets/products.json")
    parser.add_argument("--html", default="Markalar/Yamazaki/index.html")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--report",
        default=None,
        help="Optional path to write a JSON report (missing rows, skipped composites, counts).",
    )

    args = parser.parse_args()

    result = update(
        excel_path=Path(args.excel),
        products_path=Path(args.products),
        html_path=Path(args.html),
        dry_run=args.dry_run,
        report_path=Path(args.report) if args.report else None,
    )

    print(
        "Update complete:",
        f"products_updated={result.updated_products}",
        f"html_blocks_updated={result.updated_html_blocks}",
        f"html_blocks_skipped={result.skipped_html_blocks}",
        f"excel_rows_missing_product={result.missing_excel_rows}",
        sep="\n- ",
    )


if __name__ == "__main__":
    main()
