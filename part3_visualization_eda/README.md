# Part 3 — Visualization, EDA & Business Thinking

## Data source
**Trending YouTube Video Statistics** (public dataset; also on Kaggle).  
Files live in this Part’s own `data/` folder. Not claimed as original work.  
This Part does **not** read from Part 1 or Part 2.

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
1. Open `trendpulse_part3.ipynb` in Google Colab or Jupyter.
2. Set the working directory to `part3_visualization_eda` so `data/` is found.
3. **Runtime → Restart and run all** (offline; no API calls).
4. Plotly charts need an interactive notebook front-end (Colab / Jupyter).

## Cleaning applied in this Part
| Issue | Handling |
|-------|----------|
| Missing likes / comment_count | Fill with `0` |
| Missing description | Fill with `""` |
| Bad/unparseable dates | Drop those rows |
| Duplicate same video_id + trending_date + country | Keep first, drop rest |
| `video_error_or_removed == True` | Drop those rows |
| `trending_date` as `yy.dd.mm` | Parse with `%y.%d.%m` |
| Category names | Left-merge from `categories.csv` |
| `days_to_trend` | trending day − publish day |

After cleaning: about **45,908** rows and about **15,047** unique country–video pairs. Date window: **2017-11-14** to **2018-02-01**.

---

## Chart interpretations (also in notebook Markdown)

1. **Bar — counts by category.** Entertainment (~27%) and Music (~22%) dominate; niche categories are much smaller. Bar charts fit categorical counts and make rank clear.  
2. **Histogram — log1p(views).** Raw views are right-skewed; log scale shows a usable center with a long viral tail. Histograms fit one continuous variable’s shape.  
3. **Scatter — views vs likes.** The two rise together on a log–log scale across countries. Scatter plots fit two continuous numerics.  
4. **Line — records per day.** Daily volume is fairly stable over the window. Line charts fit ordered time series.  
5. **Box — log views by category.** Reach differs by category (Music tends higher than News & Politics). Box plots compare a continuous metric across categories.  
6. **Plotly scatter.** Category color + title hover highlights Music/Entertainment mega-hits. Interactive scatter fits two numerics + a categorical color + text hover.  
7. **Plotly grouped bars.** Average views differ by category **and** country. Grouped bars fit a numeric summary by two categoricals.

---

## Distributions and outliers

| Metric | Pattern | IQR outliers | Decision |
|--------|---------|--------------|----------|
| **views** | mean ≫ median > mode → **right-skewed** | thousands above the upper fence | **Keep** — mega-hits are the point of trending analysis |
| **likes** | mean > median, low mode → **right-skewed** | thousands above the upper fence | **Keep** for the same reason |

Exact mean/median/mode/outlier counts print when the notebook runs.

---

## Correlation (heatmap in notebook)

Numeric columns: `views`, `likes`, `dislikes`, `comment_count`, `days_to_trend`.

**Two strongest off-diagonal pairs (approx.):**
1. **views–likes** (r ≈ **0.92**)
2. **views–comment_count** (r ≈ **0.92**)

`days_to_trend` is only weakly related to engagement size.  
**Causation note:** correlation does not prove likes cause views (or vice versa); a third factor such as topic popularity or channel reach can lift both.

---

## Funnel table (unique country + video_id)

Approximate values from the cleaned data (recomputed live in the notebook):

| Stage | Count (approx.) | Conversion from previous |
|-------|-----------------|--------------------------|
| All videos that ever trended | 15,047 | 100% |
| Peak views > median (~263,559) | 7,523 | ~50% |
| Peak views > 90th pct (~1.63M) | 1,505 | ~20% |
| And 1,000+ comments | 1,474 | ~98% |

**Largest drop-off:** moving from above-median reach into the top-decile peak-views band. That suggests **breakout reach** is the scarce step; among mega-hits, heavy commenting is already common.

---

## Retention results

Day 1 = first trending day for each unique video (per country).

| Day | Still trending (approx.) |
|-----|--------------------------|
| 1 | 100% |
| 2 | ~63% |
| 3 | ~42% |
| 5 | ~19% |
| 7 | ~10% |

**Comparison:** On day 2, Music still has ~**80%** of videos on the list vs ~**40%** for News & Politics; US day-2 retention (~65%) beats India’s (~57%). One-day disappearances are common for news/short bursts; longer stays cluster in Music.

---

## Cohort view

Videos grouped by **first trending week**. Middle weeks are fairly similar on average lifespan; edge weeks can look different on peak views or lifespan, often because they have fewer videos or are censored by the fixed date window. Always check `n_videos` before treating a cohort spike as a real content shift.

---

## Content strategy briefing

Entertainment (~27%) and Music (~22%) dominate trending volume, with People & Blogs and Comedy next. Videos typically reach the list quickly — median `days_to_trend` is about **3 days** — so launch packaging in the first few days matters more than long warm-ups. Retention falls fast (~63% day 2, ~42% day 3, ~19% day 5, under 10% day 7); Music sticks longer than News & Politics. The funnel shows the hard step is breakout reach (only ~1.5k unique videos clear the top-decile peak-views bar), after which 1,000+ comments are almost automatic. Countries differ: US/GB often show higher average views in several categories, while India contributes heavy Entertainment/News volume — briefs should be market-specific. Views and likes move together (r ≈ 0.92), but that is association, not proof of causation. **Limitation:** the file covers a fixed window (mid-Nov 2017–early Feb 2018) and only videos that *did* trend, so failure rates for non-trending uploads are unknown.

---

## Design notes
- Charts match data types (bars, histogram, scatter, line, box, heatmap).  
- Log scaling is used where raw views would squash the plot.  
- All required written interpretation lives in notebook Markdown cells **and** in this README.  
- Git practice for this Part: use a `part3-eda` feature branch with 2+ commits, then merge to `main` (scored for Part 3).
