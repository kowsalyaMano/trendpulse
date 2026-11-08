# Part 4 — SQL & Spreadsheet Analysis

## Tools
- **MySQL Workbench** (schema design, `LOAD DATA` / Import Wizard, SQL queries)
- **Python / Pandas / openpyxl** (prepare cleaned CSVs; build `trendpulse_briefing.xlsx`)
- Data source: **Trending YouTube Video Statistics** (same synthetic course files used in earlier Parts; not claimed as original work)

## How the cleaned CSV tables were prepared
Run (from this folder, after the original country files are available e.g. in `../part2_numpy_pandas/data/`):

```bash
pip install -r requirements.txt
python prepare_tables.py
```

`prepare_tables.py` does the following:

1. Load `USvideos.csv`, `GBvideos.csv`, `INvideos.csv` and add a `country` column.
2. Parse `trending_date` (`%y.%d.%m`) and `publish_time`; coerce numeric engagement fields; fill missing likes/comments with `0`.
3. Drop bad dates, rows with `video_error_or_removed == True`, and duplicates on `(video_id, trending_date, country)` via `drop_duplicates()`.
4. Write **`data/categories.csv`** from the categories lookup (`drop_duplicates` on `category_id`).
5. Write **`data/videos.csv`** — one row per unique `video_id` (`groupby` / first title, channel, category, publish time).
6. Write **`data/trending_records.csv`** — one row per video per day per country, with a `record_id`, via column select + `to_csv(..., index=False)`.

Committed cleaned tables (after prepare):

| Table | Rows | Grain |
|-------|------|--------|
| `categories` | 17 | one category |
| `videos` | 14,688 | one unique video |
| `trending_records` | 45,908 | one video × day × country |

## Schema design decisions
Three related tables with PK/FK:

| Table | PK | FK | Why |
|-------|----|----|-----|
| `categories` | `category_id` | — | Small lookup; avoids repeating names |
| `videos` | `video_id` | `category_id → categories` | Video attributes stored once |
| `trending_records` | `record_id` | `video_id → videos` | Daily country metrics; unique `(video_id, trending_date, country)` |

This matches how trending data is generated (daily snapshots) and how analysts query it (filter by country/date, join titles/categories).

## Run order (MySQL Workbench)
1. Open `trendpulse_part4.sql`.
2. Edit the three `LOAD DATA LOCAL INFILE` paths to your local absolute path for `part4_sql_spreadsheet/data/`.
3. Enable local infile if needed (`SET GLOBAL local_infile = 1;`) **or** use **Table Data Import Wizard** for each CSV into the matching table (same column order as the CSV headers).
4. Execute the script top to bottom: `CREATE DATABASE` → `CREATE TABLE` → load → `SELECT COUNT(*)` → analysis queries.
5. Open `trendpulse_briefing.xlsx` in Excel / Google Sheets-compatible tools for the spreadsheet half.
6. Rebuild the workbook anytime with `python build_workbook_and_outputs.py`.

### Row counts after loading
```
table_name         n
categories        17
videos         14688
trending_records 45908
```

---

## SQL queries and text output (≥ 8)

### Q1 — SELECT / WHERE / ORDER BY / LIMIT / aliases
Top 10 most-viewed US trending records.

```sql
SELECT
  video_id      AS vid,
  country       AS market,
  trending_date AS trend_day,
  views         AS view_count
FROM trending_records
WHERE country = 'US'
ORDER BY views DESC
LIMIT 10;
```

**Output:**
```
        vid market  trend_day  view_count
HPG-bd_JLxn     US 2018-01-11   129229245
yd4LMLxXzWE     US 2018-01-06   119711498
HPG-bd_JLxn     US 2018-01-10   109129467
Nc1MUQvmyWO     US 2017-12-18    97553795
yd4LMLxXzWE     US 2018-01-05    97342335
HPG-bd_JLxn     US 2018-01-09    90679797
Nc1MUQvmyWO     US 2017-12-17    83611280
h5eHGd1GiiS     US 2017-12-11    82623566
yd4LMLxXzWE     US 2018-01-04    80368655
HPG-bd_JLxn     US 2018-01-08    70261074
```

### Q2 — DISTINCT (+ alias)
```sql
SELECT DISTINCT country AS market
FROM trending_records
ORDER BY country;
```

**Output:**
```
market
    GB
    IN
    US
```

### Q3 — DISTINCT categories that appear on videos
```sql
SELECT DISTINCT c.category_name AS category
FROM categories c
INNER JOIN videos v ON v.category_id = c.category_id
ORDER BY category;
```

**Output:**
```
            category
    Autos & Vehicles
              Comedy
           Education
       Entertainment
    Film & Animation
              Gaming
       Howto & Style
               Music
     News & Politics
      People & Blogs
      Pets & Animals
Science & Technology
              Sports
     Travel & Events
```

### Q4 — GROUP BY + HAVING (categories with avg views > 1,000,000)
```sql
SELECT
  c.category_name AS category,
  ROUND(AVG(t.views), 2) AS avg_views,
  COUNT(*) AS n_records
FROM trending_records t
INNER JOIN videos v ON v.video_id = t.video_id
INNER JOIN categories c ON c.category_id = v.category_id
GROUP BY c.category_name
HAVING AVG(t.views) > 1000000
ORDER BY avg_views DESC;
```

**Output:**
```
category  avg_views  n_records
   Music 3193066.33      10286
```

### Q5 — GROUP BY + HAVING (channels with ≥ 5 distinct videos)
```sql
SELECT
  v.channel_title AS channel,
  COUNT(DISTINCT v.video_id) AS distinct_videos
FROM videos v
GROUP BY v.channel_title
HAVING COUNT(DISTINCT v.video_id) >= 5
ORDER BY distinct_videos DESC
LIMIT 15;
```

**Output (top 15):**
```
              channel  distinct_videos
   UltimateUnboxing65              522
     QuietChallenge75              466
     OfficialReview41              457
     InsaneReaction46              321
 Brand NewChallenge45              302
     UltimateSpeech20              292
       CrazyTrailer91              283
      WildHighlights7              245
       UltimateVlog96              233
SurprisingChallenge82              216
        CrazyRecipe67              202
    Brand NewSecret51              188
 SurprisingTutorial85              184
         QuietPrank55              178
     FinalBreakdown11              164
```

### Q6 — INNER JOIN (three tables)
```sql
SELECT
  t.country AS market,
  t.trending_date AS trend_day,
  v.title AS video_title,
  c.category_name AS category,
  t.views AS view_count
FROM trending_records t
INNER JOIN videos v ON v.video_id = t.video_id
INNER JOIN categories c ON c.category_id = v.category_id
WHERE t.country = 'GB'
ORDER BY t.views DESC
LIMIT 5;
```

**Why INNER JOIN:** We only want trending rows that successfully match a video **and** a category name. Rows that fail either match are not useful for a “title + category” listing, so INNER JOIN (not LEFT/RIGHT) is correct.

**Output:**
```
market  trend_day                                      video_title category  view_count
    GB 2018-01-05                      Lena Ortiz - Monsoon (Live)    Music   360760164
    GB 2018-01-27 The Hollow Pines - Phones (Official Video) WATCH    Music   343297002
    GB 2018-01-04                      Lena Ortiz - Monsoon (Live)    Music   286714357
    GB 2018-01-26 The Hollow Pines - Phones (Official Video) WATCH    Music   282812154
    GB 2017-12-24      Rook & Vale - Phones (Official Video) WATCH    Music   255362869
```

### Q7 — LEFT JOIN (categories with no videos)
```sql
SELECT
  c.category_id,
  c.category_name,
  COUNT(v.video_id) AS video_count
FROM categories c
LEFT JOIN videos v ON v.category_id = c.category_id
GROUP BY c.category_id, c.category_name
HAVING COUNT(v.video_id) = 0
ORDER BY c.category_id;
```

**Why LEFT JOIN:** Starting from `categories`, we must keep categories even when there is no matching video. An INNER JOIN would hide empty categories; a RIGHT JOIN from videos would never surface unused category ids.

**Output:**
```
 category_id         category_name  video_count
          29 Nonprofits & Activism            0
          30                Movies            0
          43                 Shows            0
```

### Q8 — RIGHT JOIN (all videos; flag missing category)
```sql
SELECT
  v.video_id,
  v.title,
  c.category_name
FROM categories c
RIGHT JOIN videos v ON v.category_id = c.category_id
WHERE c.category_id IS NULL
LIMIT 10;
```

**Why RIGHT JOIN:** The driving question is “do any **videos** lack a category?” so every video must be retained (`videos` on the right). LEFT JOIN with `videos` on the left would be equivalent; RIGHT JOIN is used here deliberately to show that form. INNER JOIN would drop orphans; LEFT JOIN from categories would not list every video.

**Output:**
```
(empty — no orphan videos; every video_id has a matching category_id)
```

---

## Spreadsheet workbook (`trendpulse_briefing.xlsx`)

Sheets: `records`, `categories`, `videos`, `summary`, `lookup_demo`, `Pivot_AvgViews`.

### (a) Pivot table — average views by category and country
- **Sheet:** `Pivot_AvgViews`
- **Rows:** `category_name`
- **Columns:** `country` (`US`, `GB`, `IN`)
- **Values:** AVERAGE of `views`
- Built from the cleaned records joined to video/category names (same aggregation you would get from Insert → PivotTable on the `records` sheet).

### (b) Lookup sheet + VLOOKUP / XLOOKUP
- **Sheet:** `lookup_demo`
- Input `category_id` in column A (examples: 10, 24, 25, 20, 29).
- **VLOOKUP formula (row 2):**  
  `=VLOOKUP(A2,categories!$A$2:$B$18,2,FALSE)`
- **XLOOKUP formula (row 2):**  
  `=XLOOKUP(A2,categories!$A$2:$A$18,categories!$B$2:$B$18,"(not found)")`
- Lookup range lives on the `categories` sheet (also formatted as Excel table `CategoryTable`).

### (c) COUNTIF, SUM, AVERAGE headline numbers
- **Sheet:** `summary`
- US / GB / IN counts:  
  `=COUNTIF(CountryCol,"US")` (and `"GB"`, `"IN"`)
- Total views: `=SUM(AllViews)`
- Overall average views: `=AVERAGE(AllViews)`

### (d) Filters and sorting on the records sheet
- `records` has **AutoFilter** enabled on `A1:L{last_row}`.
- Rows are **pre-sorted** by `country` ascending, then `views` descending (largest views first within each country).
- Header row is frozen (`freeze_panes = A2`).

### (e) Conditional formatting — top 10% of views
- Applied to `records!A2:L{last_row}`.
- **Rule (formula):** `$E2>=PERCENTILE($E$2:$E${last_row},0.9)`
- **Format:** light yellow fill (`FFF2CC`) on the whole row when views are in the top decile.

### (f) Named ranges used inside formulas
| Name | Refers to | Used in |
|------|-----------|---------|
| `AllViews` | `records!$E$2:$E${last_row}` | `=SUM(AllViews)`, `=AVERAGE(AllViews)` |
| `CountryCol` | `records!$C$2:$C${last_row}` | `=COUNTIF(CountryCol,"US")` etc. |

---

## Cross-check (SQL vs spreadsheet)

| Check | SQL result | Spreadsheet (static cross-check cells on `summary`) |
|-------|------------|------------------------------------------------------|
| US record count | **15,968** | **15,968** (`summary!B11`, also `COUNTIF(CountryCol,"US")`) |
| Music average views | **3,193,066.33** | **3,193,066.33** (`summary!B12`) |

They agree. (Minor floating display differences can appear only if Excel rounds differently; the stored values match.)

---

## Files in this folder
```
part4_sql_spreadsheet/
├── README.md
├── requirements.txt
├── prepare_tables.py
├── build_workbook_and_outputs.py
├── trendpulse_part4.sql
├── trendpulse_briefing.xlsx
└── data/
    ├── categories.csv
    ├── videos.csv
    └── trending_records.csv
```
