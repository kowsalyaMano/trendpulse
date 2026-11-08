-- =============================================================================
-- TrendPulse Part 4 — MySQL schema, load, and analysis queries
-- Run in MySQL Workbench in this order (top to bottom).
-- Prerequisite: cleaned CSVs in part4_sql_spreadsheet/data/
--   categories.csv, videos.csv, trending_records.csv
-- =============================================================================

-- 1) Schema design

DROP DATABASE IF EXISTS trendpulse;
CREATE DATABASE trendpulse
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE trendpulse;

-- Lookup table for YouTube category ids
CREATE TABLE categories (
  category_id   INT          NOT NULL,
  category_name VARCHAR(100) NOT NULL,
  PRIMARY KEY (category_id)
) ENGINE=InnoDB;

-- One row per unique video
CREATE TABLE videos (
  video_id      VARCHAR(32)  NOT NULL,
  title         VARCHAR(500) NOT NULL,
  channel_title VARCHAR(255) NOT NULL,
  category_id   INT          NOT NULL,
  publish_time  DATETIME     NULL,
  PRIMARY KEY (video_id),
  CONSTRAINT fk_videos_category
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
      ON UPDATE CASCADE
      ON DELETE RESTRICT
) ENGINE=InnoDB;

-- One row per video per trending day per country
CREATE TABLE trending_records (
  record_id     INT          NOT NULL AUTO_INCREMENT,
  video_id      VARCHAR(32)  NOT NULL,
  country       CHAR(2)      NOT NULL,
  trending_date DATE         NOT NULL,
  views         BIGINT       NOT NULL DEFAULT 0,
  likes         BIGINT       NOT NULL DEFAULT 0,
  dislikes      BIGINT       NOT NULL DEFAULT 0,
  comment_count BIGINT       NOT NULL DEFAULT 0,
  PRIMARY KEY (record_id),
  UNIQUE KEY uq_video_day_country (video_id, trending_date, country),
  KEY idx_country (country),
  KEY idx_views (views),
  CONSTRAINT fk_records_video
    FOREIGN KEY (video_id) REFERENCES videos (video_id)
      ON UPDATE CASCADE
      ON DELETE CASCADE
) ENGINE=InnoDB;

-- 2) Loading (Workbench Table Data Import Wizard is also fine)
--    Adjust the absolute paths below to your machine, then run.
--    Example Windows path style is shown; keep forward slashes or escaped
--    backslashes. Enable "local_infile" if using LOAD DATA LOCAL.
-- SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/kk/LLM/trendpulse/part4_sql_spreadsheet/data/categories.csv'
INTO TABLE categories
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(category_id, category_name);

LOAD DATA LOCAL INFILE 'C:/kk/LLM/trendpulse/part4_sql_spreadsheet/data/videos.csv'
INTO TABLE videos
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(video_id, title, channel_title, category_id, publish_time);

LOAD DATA LOCAL INFILE 'C:/kk/LLM/trendpulse/part4_sql_spreadsheet/data/trending_records.csv'
INTO TABLE trending_records
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(record_id, video_id, country, trending_date, views, likes, dislikes, comment_count);

-- Row counts after loading
SELECT 'categories' AS table_name, COUNT(*) AS n FROM categories
UNION ALL
SELECT 'videos', COUNT(*) FROM videos
UNION ALL
SELECT 'trending_records', COUNT(*) FROM trending_records;


-- 3) Basic queries — SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, aliases


-- Q1: 10 most-viewed trending records in the US (WHERE, ORDER BY, LIMIT, aliases)
SELECT
  video_id      AS vid,
  country       AS market,
  trending_date AS trend_day,
  views         AS view_count
FROM trending_records
WHERE country = 'US'
ORDER BY views DESC
LIMIT 10;

-- Q2: distinct countries present
SELECT DISTINCT country AS market
FROM trending_records
ORDER BY country;

-- Q3: distinct category names that actually appear on videos
SELECT DISTINCT c.category_name AS category
FROM categories c
INNER JOIN videos v ON v.category_id = c.category_id
ORDER BY category;


-- 4) Grouping — GROUP BY, aggregates, HAVING


-- Q4: categories whose average views exceed 1,000,000
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

-- Q5: channels with at least 5 distinct trending videos
SELECT
  v.channel_title AS channel,
  COUNT(DISTINCT v.video_id) AS distinct_videos
FROM videos v
GROUP BY v.channel_title
HAVING COUNT(DISTINCT v.video_id) >= 5
ORDER BY distinct_videos DESC
LIMIT 15;


-- 5) Joins — INNER, LEFT, RIGHT (each justified in the README)


-- Q6: INNER JOIN — list GB trending rows with video title and category name
--     (only rows that match in all three tables)
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

-- Q7: LEFT JOIN — find categories that have no video in this dataset
--     (keeps every category; unmatched videos side is NULL)
SELECT
  c.category_id,
  c.category_name,
  COUNT(v.video_id) AS video_count
FROM categories c
LEFT JOIN videos v ON v.category_id = c.category_id
GROUP BY c.category_id, c.category_name
HAVING COUNT(v.video_id) = 0
ORDER BY c.category_id;

-- Q8: RIGHT JOIN — keep every video and show if its category is missing
--     (RIGHT JOIN from categories to videos = all videos retained)
SELECT
  v.video_id,
  v.title,
  c.category_name
FROM categories c
RIGHT JOIN videos v ON v.category_id = c.category_id
WHERE c.category_id IS NULL
LIMIT 10;


-- Cross-check helpers (used against the spreadsheet)

SELECT COUNT(*) AS us_records
FROM trending_records
WHERE country = 'US';

SELECT ROUND(AVG(t.views), 2) AS music_avg_views
FROM trending_records t
INNER JOIN videos v ON v.video_id = t.video_id
INNER JOIN categories c ON c.category_id = v.category_id
WHERE c.category_name = 'Music';
