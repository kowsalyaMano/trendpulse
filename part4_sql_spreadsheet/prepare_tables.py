"""
Prepare the three cleaned CSV tables for Part 4 from country trending CSVs.

Run once from part4_sql_spreadsheet/:
    python prepare_tables.py

Looks for USvideos.csv / GBvideos.csv / INvideos.csv + categories.csv in data/
(or falls back to ../part2_numpy_pandas/data/).
Writes:
    data/categories.csv
    data/videos.csv
    data/trending_records.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

COUNTRIES = ["US", "GB", "IN"]
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def find_source_dir() -> Path:
    # Prefer sibling Part folders for the original country CSVs.
    # Part 4's own data/ should hold only the three cleaned output tables.
    candidates = [
        HERE.parent / "part2_numpy_pandas" / "data",
        HERE.parent / "part1_python_foundations" / "data",
        DATA / "_raw_source",
        DATA,
    ]
    for folder in candidates:
        if (folder / "USvideos.csv").exists() and (folder / "categories.csv").exists():
            return folder
    raise FileNotFoundError("Could not find country CSVs + categories.csv")


def clean_and_export() -> None:
    src = find_source_dir()
    print("Source folder:", src)

    frames = []
    for code in COUNTRIES:
        one = pd.read_csv(src / f"{code}videos.csv")
        one["country"] = code
        frames.append(one)
        print(f"  loaded {code}: {len(one)} rows")

    raw = pd.concat(frames, ignore_index=True)

    # types / dates
    raw["trending_date"] = pd.to_datetime(raw["trending_date"], format="%y.%d.%m", errors="coerce")
    raw["publish_time"] = pd.to_datetime(raw["publish_time"], errors="coerce", utc=True)
    for col in ["views", "likes", "dislikes", "comment_count", "category_id"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")

    raw["likes"] = raw["likes"].fillna(0).astype("int64")
    raw["dislikes"] = raw["dislikes"].fillna(0).astype("int64")
    raw["comment_count"] = raw["comment_count"].fillna(0).astype("int64")
    raw["views"] = raw["views"].fillna(0).astype("int64")

    # drop bad dates, removed videos, duplicates
    before = len(raw)
    raw = raw.dropna(subset=["trending_date", "publish_time", "video_id", "category_id"]).copy()
    if "video_error_or_removed" in raw.columns:
        raw = raw[raw["video_error_or_removed"] != True]
    raw = raw.drop_duplicates(subset=["video_id", "trending_date", "country"], keep="first")
    print(f"Rows after cleaning: {len(raw)} (removed {before - len(raw)})")

    # --- categories ---
    categories = pd.read_csv(src / "categories.csv")
    categories = categories.drop_duplicates(subset=["category_id"]).sort_values("category_id")
    categories["category_id"] = categories["category_id"].astype("int64")
    categories.to_csv(DATA / "categories.csv", index=False)
    print("Wrote categories.csv:", len(categories))

    # --- videos: one row per unique video_id ---
    videos = (
        raw.sort_values(["video_id", "trending_date"])
        .groupby("video_id", as_index=False)
        .agg(
            title=("title", "first"),
            channel_title=("channel_title", "first"),
            category_id=("category_id", "first"),
            publish_time=("publish_time", "first"),
        )
    )
    videos["category_id"] = videos["category_id"].astype("int64")
    videos["publish_time"] = videos["publish_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    videos.to_csv(DATA / "videos.csv", index=False)
    print("Wrote videos.csv:", len(videos))

    # --- trending_records: one row per video per day per country ---
    records = raw.loc[
        :,
        [
            "video_id",
            "country",
            "trending_date",
            "views",
            "likes",
            "dislikes",
            "comment_count",
        ],
    ].copy()
    records = records.sort_values(["trending_date", "country", "video_id"]).reset_index(drop=True)
    records.insert(0, "record_id", range(1, len(records) + 1))
    records["trending_date"] = records["trending_date"].dt.strftime("%Y-%m-%d")
    records.to_csv(DATA / "trending_records.csv", index=False)
    print("Wrote trending_records.csv:", len(records))

    print("\nDone. Counts:")
    print("  categories       ", len(categories))
    print("  videos           ", len(videos))
    print("  trending_records ", len(records))


if __name__ == "__main__":
    DATA.mkdir(parents=True, exist_ok=True)
    clean_and_export()
