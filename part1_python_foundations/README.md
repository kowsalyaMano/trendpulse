# Part 1 — Python Foundations & Data Structures

## Data source
**Trending YouTube Video Statistics** (public dataset; also available on Kaggle).  
Country CSVs and `categories.csv` are in `data/`. This data is not claimed as original work.

## Countries / files used
- `data/USvideos.csv`
- `data/GBvideos.csv`
- `data/INvideos.csv`
- `data/categories.csv`

Files are used as provided (no column trimming).

## Install
```bash
pip install -r requirements.txt
```

## How to run
1. Open `trendpulse_part1.ipynb` in Google Colab or Jupyter.
2. Make sure a `data/` folder sits next to the notebook with the four CSV files above.
3. In Colab, if needed, set the working directory to the folder that contains `data/` (for example `os.chdir("/content")` or your Drive path).
4. Use **Runtime → Restart session**, then **Run all**. The notebook should finish with no errors.

## Cleaning rules
- **views / likes / dislikes / comment_count:** bad or blank → substitute `0` (keep the row).
- **comments_disabled / ratings_disabled / video_error_or_removed:** bad or blank → substitute `False`.
- **trending_date** (`yy.dd.mm`) and **publish_time:** bad parse → set `None` (keep the row).
- All conversions use `try/except` so one bad value cannot crash the run. Failure counts are printed per field.

## Classification thresholds
- **Unrated:** `ratings_disabled` is True
- **Low Engagement:** views == 0 or (likes + dislikes) == 0
- **Viral Hit:** views >= 1,000,000 and like_ratio >= 0.90
- **Divisive:** enough ratings and like_ratio < 0.50
- **Steady Performer:** otherwise normal engagement  
  `like_ratio = likes / (likes + dislikes)` only when the denominator is not zero.

## Design decisions
- List of dicts for cleaned rows (easy looping).
- Sets for unique `video_id` per country (intersection / difference).
- Dict counter + slicing for top channels.
- Nested dict for country → category → count.
- Helpers like `safe_int` and `like_ratio` remove repeated code.
