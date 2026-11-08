# Part 2 — NumPy & Pandas Data Wrangling

## Data source
**Trending YouTube Video Statistics** (public dataset; also on Kaggle).  
Files live in this Part’s own `data/` folder. Not claimed as original work.  
This Part does **not** read from Part 1.

## Countries / files
- `data/USvideos.csv`
- `data/GBvideos.csv`
- `data/INvideos.csv`
- `data/categories.csv`

## Install
```bash
pip install -r requirements.txt
```

## How to run
1. Open `trendpulse_part2.ipynb` in Google Colab or Jupyter.
2. Set the working directory to `part2_numpy_pandas` so `data/` is found.
3. **Runtime → Restart and run all** (offline; no API calls).

## Engagement score weights
- **views = 0.50** — reach is the main “trending” signal  
- **likes = 0.30** — positive reaction, secondary to reach  
- **comments = 0.20** — discussion signal; noisier / smaller scale  

Each input is min–max normalized before weighting so huge raw views cannot alone dominate the score.  
Also computed: safe like-ratio, comment-rate, `log1p(views)` for plotting scale, and a top-10% engagement mask.

## Data-quality issues and cleaning
| Issue | Handling |
|-------|----------|
| Missing likes / comment_count | Fill with `0` (`fillna`) |
| Missing description | Fill with `""` (`fillna`) |
| Bad/unparseable dates | Drop those rows (`dropna` on `trending_date`, `publish_time`) |
| Duplicate same video_id + trending_date + country | Keep first, drop rest (`drop_duplicates`) |
| `trending_date` as `yy.dd.mm` | Parse with `%y.%d.%m` |
| `publish_time` string/UTC | `pd.to_datetime(..., utc=True)` |
| Removed/errored videos | Kept (still valid for counts); can filter with the flag |

## Missing values and duplicates
- Report count and % per affected column in the notebook.  
- **Duplicate definition:** same `video_id` on the same `trending_date` in the same `country`.  
- Exact duplicate count removed is printed when the notebook runs.

## Design notes
- NumPy section uses vectorized ops only (no Python loops for ratios/score/broadcast).  
- Category join uses a **left** merge so no trending rows are lost.  
- Lifespan = number of distinct trending days per video within each country.
