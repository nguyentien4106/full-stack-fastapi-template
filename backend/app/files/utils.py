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
        
    # Merge all tables
    for i in range(1, len(all_dfs)):
        all_dfs[i].drop(0)

    merged = pd.concat(all_dfs, ignore_index=True)

    return merged


def get_df_from_result_json(url) -> DataFrame:
    res = requests.get(url)
    res.raise_for_status()

    data = res.json()

    return extract_tables_from_ocr(data)

def get_df_from_json_bytes(json_bytes: bytes) -> DataFrame:

    json_data = json.loads(json_bytes.decode("utf-8"))

    return extract_tables_from_ocr(json_data)