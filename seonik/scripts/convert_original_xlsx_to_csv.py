#!/usr/bin/env python3
"""Convert CRSP and DataGuide source files to pandas-ready CSV files.

Inputs are read from data/original/{crsp,dataguide}; outputs mirror those
folders under data/refined. The first CSV column is the DatetimeIndex named
``date``. CSV files are written as UTF-8 with a BOM so Korean text is preserved
when opened in Excel as well as in pandas.

Install dependencies with ``python -m pip install pandas openpyxl``.

Read an output file with:
    pd.read_csv(path, index_col="date", parse_dates=["date"], encoding="utf-8-sig")
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd


SUPPORTED_EXCEL = {".xlsx", ".xlsm"}
CRSP_SUFFIXES = SUPPORTED_EXCEL | {".csv"}
DATE_HEADER_TOKENS = {
    "date",
    "caldt",
    "dlycaldt",
    "datadate",
    "tradedate",
    "tradingdate",
    "observationdate",
}
CRSP_HEADER_NAMES = {
    "permno": "security_id",
    "hdr cusip": "cusip",
    "hdrcusip": "cusip",
    "ticker": "ticker",
    "permco": "company_id",
    "dlycaldt": "date",
    "caldt": "date",
    "date": "date",
    "dlyprc": "close_price",
}


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def parse_date(value: Any) -> pd.Timestamp | None:
    """Parse common Excel, YYYYMMDD, and ISO date values without guessing IDs."""
    if is_blank(value) or isinstance(value, bool):
        return None
    if isinstance(value, pd.Timestamp):
        return value.normalize() if not pd.isna(value) else None
    if isinstance(value, (datetime, date)):
        return pd.Timestamp(value).normalize()

    if isinstance(value, (int, float)):
        number = int(value)
        if number != value:
            return None
        text = str(number)
        if len(text) == 8 and text.startswith(("19", "20", "21")):
            parsed = pd.to_datetime(text, format="%Y%m%d", errors="coerce")
        elif 1 <= number <= 100000:
            parsed = pd.to_datetime(number, unit="D", origin="1899-12-30", errors="coerce")
        else:
            return None
    else:
        text = str(value).strip()
        if re.fullmatch(r"\d{8}", text):
            parsed = pd.to_datetime(text, format="%Y%m%d", errors="coerce")
        else:
            parsed = pd.to_datetime(text, errors="coerce")

    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).normalize()


def header_token(value: Any) -> str:
    if is_blank(value):
        return ""
    return re.sub(r"[^a-z0-9]", "", str(value).strip().casefold())


def normalize_crsp_header(value: Any, position: int) -> str:
    if is_blank(value):
        return f"column_{position + 1}"
    text = str(value).strip()
    token = header_token(text)
    if token in {"permno"}:
        return "security_id"
    if token in {"hdrcusip", "cusip"}:
        return "cusip"
    if token == "ticker":
        return "ticker"
    if token == "permco":
        return "company_id"
    if token in DATE_HEADER_TOKENS:
        return "date"
    if token == "dlyprc":
        return "close_price"
    cleaned = re.sub(r"\s+", "_", text)
    return cleaned or f"column_{position + 1}"


def unique_names(names: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    result = []
    for name in names:
        counts[name] = counts.get(name, 0) + 1
        result.append(name if counts[name] == 1 else f"{name}_{counts[name]}")
    return result


def find_crsp_header_row(raw: pd.DataFrame, search_rows: int = 50) -> tuple[int, int]:
    for row_number in range(min(len(raw), search_rows)):
        for column_number, value in enumerate(raw.iloc[row_number].tolist()):
            if header_token(value) in DATE_HEADER_TOKENS:
                return row_number, column_number
    raise ValueError("Could not find a CRSP date column in the first 50 rows.")


def convert_crsp_table(raw: pd.DataFrame) -> pd.DataFrame:
    header_row, date_column = find_crsp_header_row(raw)
    original_headers = raw.iloc[header_row].tolist()
    width = len(original_headers)
    headers = unique_names(
        [normalize_crsp_header(value, i) for i, value in enumerate(original_headers)]
    )
    if headers[date_column] != "date":
        headers[date_column] = "date"

    data = raw.iloc[header_row + 1 :, :width].copy()
    data.columns = headers
    dates = data.iloc[:, date_column].map(parse_date)
    valid = dates.notna()
    if not valid.any():
        raise ValueError("The CRSP table has no rows with a valid date.")

    data = data.loc[valid].copy()
    index = pd.DatetimeIndex(dates.loc[valid], name="date")
    data = data.drop(columns=[headers[date_column]])
    data.index = index
    return data


def first_dataguide_data_row(raw: pd.DataFrame) -> int:
    if raw.empty:
        raise ValueError("The DataGuide worksheet is empty.")
    for row_number, value in enumerate(raw.iloc[:, 0].tolist()):
        if parse_date(value) is not None:
            return row_number
    raise ValueError("Could not find the first date row in the DataGuide worksheet.")


def dataguide_column_name(market_name: Any, item_name: Any, market_code: Any, item_code: Any) -> str:
    market = "" if is_blank(market_name) else str(market_name).strip()
    metric = "" if is_blank(item_name) else str(item_name).strip()
    if market and metric:
        return f"{market}_{metric}"
    code_parts = [str(value).strip() for value in (market_code, item_code) if not is_blank(value)]
    return "_".join(code_parts) or "series"


def convert_dataguide_table(raw: pd.DataFrame) -> pd.DataFrame:
    data_start = first_dataguide_data_row(raw)
    metadata_start = data_start - 6
    if metadata_start < 0:
        raise ValueError("The DataGuide worksheet is missing its six metadata rows.")

    code_row = raw.iloc[metadata_start].tolist()
    market_row = raw.iloc[metadata_start + 1].tolist()
    type_row = raw.iloc[metadata_start + 2].tolist()
    item_code_row = raw.iloc[metadata_start + 3].tolist()
    item_name_row = raw.iloc[metadata_start + 4].tolist()
    frequency_row = raw.iloc[metadata_start + 5].tolist()

    date_values = raw.iloc[data_start:, 0].map(parse_date)
    valid = date_values.notna()
    if not valid.any():
        raise ValueError("The DataGuide worksheet has no dated observations.")
    index = pd.DatetimeIndex(date_values.loc[valid], name="date")
    output = pd.DataFrame(index=index)

    for column_number in range(1, raw.shape[1]):
        market_code = code_row[column_number] if column_number < len(code_row) else None
        market_name = market_row[column_number] if column_number < len(market_row) else None
        item_code = item_code_row[column_number] if column_number < len(item_code_row) else None
        item_name = item_name_row[column_number] if column_number < len(item_name_row) else None
        if all(is_blank(value) for value in (market_code, market_name, item_code, item_name)):
            continue

        column_name = dataguide_column_name(market_name, item_name, market_code, item_code)
        if column_name in output.columns:
            suffix = "" if is_blank(item_code) else f"_{item_code}"
            column_name = f"{column_name}{suffix}"
        if column_name in output.columns:
            column_name = f"{column_name}_{column_number + 1}"

        values = raw.iloc[data_start:, column_number].loc[valid]
        output[column_name] = pd.to_numeric(values.reset_index(drop=True), errors="coerce").to_numpy()

    if output.shape[1] == 0:
        raise ValueError("The DataGuide worksheet has no metric columns.")
    return output


def excel_sheets(path: Path) -> dict[str, pd.DataFrame]:
    return pd.read_excel(path, sheet_name=None, header=None, dtype=object, engine="openpyxl")


def source_files(original_root: Path):
    for provider, suffixes in (("crsp", CRSP_SUFFIXES), ("dataguide", SUPPORTED_EXCEL)):
        provider_root = original_root / provider
        if not provider_root.exists():
            continue
        for path in sorted(provider_root.rglob("*")):
            if not path.is_file() or path.name.startswith(("~$", ".")):
                continue
            if path.suffix.casefold() in suffixes:
                yield provider, path


def output_paths(source: Path, output_root: Path, provider_root: Path, sheet_names: list[str]):
    relative_parent = source.parent.relative_to(provider_root)
    target_dir = output_root / provider_root.name / relative_parent
    if len(sheet_names) == 1:
        return [target_dir / f"{source.stem}.csv"]
    safe_sheets = [re.sub(r"[^\w.-]+", "_", name, flags=re.UNICODE).strip("_.") or "sheet" for name in sheet_names]
    return [target_dir / f"{source.stem}__{sheet}.csv" for sheet in safe_sheets]


def convert_file(provider: str, source: Path, original_root: Path, output_root: Path) -> list[Path]:
    provider_root = original_root / provider
    if source.suffix.casefold() == ".csv":
        raw = pd.read_csv(source, header=None, dtype=object, encoding="utf-8-sig")
        frames = [(source.stem, convert_crsp_table(raw))]
    else:
        sheets = excel_sheets(source)
        frames = []
        for sheet_name, raw in sheets.items():
            if raw.empty:
                continue
            frame = convert_crsp_table(raw) if provider == "crsp" else convert_dataguide_table(raw)
            frames.append((sheet_name, frame))
        if not frames:
            raise ValueError("The workbook has no non-empty worksheets.")

    paths = output_paths(source, output_root, provider_root, [name for name, _ in frames])
    written = []
    for target, (_, frame) in zip(paths, frames):
        target.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(target, index=True, index_label="date", date_format="%Y-%m-%d", encoding="utf-8-sig")
        written.append(target)
    return written


def main() -> int:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root, help="Project root containing data/original and data/refined.")
    args = parser.parse_args()

    project_root = args.root.resolve()
    original_root = project_root / "data" / "original"
    output_root = project_root / "data" / "refined"
    if not original_root.is_dir():
        parser.error(f"Input folder not found: {original_root}")

    inputs = list(source_files(original_root))
    if not inputs:
        print(f"No supported source files found in {original_root}")
        return 0

    failures = 0
    for provider, source in inputs:
        try:
            outputs = convert_file(provider, source, original_root, output_root)
        except Exception as exc:
            failures += 1
            print(f"ERROR {source}: {exc}", file=sys.stderr)
            continue
        for output in outputs:
            rows = sum(1 for _ in output.open("r", encoding="utf-8-sig")) - 1
            print(f"{source.relative_to(original_root)} -> {output.relative_to(project_root)} ({rows:,} rows)")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
