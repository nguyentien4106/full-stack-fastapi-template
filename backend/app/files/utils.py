import json
from io import StringIO

import pandas as pd
import requests
from pandas import DataFrame


def extract_tables_from_ocr(data) -> pd.DataFrame:
    all_dfs: list[DataFrame] = []

    pages = data["result"]["layoutParsingResults"]

    for page_idx, page in enumerate(pages):
        blocks = page.get("prunedResult", {}).get("parsing_res_list", [])

        for block in blocks:
            if block.get("block_label") == "table":
                html = block.get("block_content")

                try:
                    dfs = pd.read_html(StringIO(html))
                    for df in dfs:
                        df["__page__"] = page_idx + 1  # debug tracking
                        all_dfs.append(df)
                except Exception as e:
                    pass
    if not all_dfs:
        raise Exception("No tables found")

    merged = pd.concat(all_dfs, ignore_index=True)

    return merged


def _extract_tables_from_ndjson(text: str) -> DataFrame:
    """Parse NDJSON (one JSON object per line) and extract all tables."""
    all_dfs: list[DataFrame] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        try:
            df = extract_tables_from_ocr(data)
            all_dfs.append(df)
        except Exception:
            pass
    if not all_dfs:
        raise Exception("No tables found")
    return pd.concat(all_dfs, ignore_index=True)


def get_df_from_result_json(url) -> DataFrame:
    res = requests.get(url)
    res.raise_for_status()
    return _extract_tables_from_ndjson(res.text)


def get_df_from_json_bytes(json_bytes: bytes) -> DataFrame:
    text = json_bytes.decode("utf-8")
    return _extract_tables_from_ndjson(text)
