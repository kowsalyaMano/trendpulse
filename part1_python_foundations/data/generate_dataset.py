"""
Generates a SYNTHETIC reference dataset that mirrors the schema and quirks of the public
"Trending YouTube Video Statistics" dataset (one CSV per country + a categories lookup).

It is NOT real YouTube data. It exists so instructors can run the solutions end to end and so
the answer key is reproducible (fixed seed). Swap in the real files for the real thing.

Run:  python generate_dataset.py
"""
import numpy as np
import pandas as pd
import string
from datetime import date, datetime, timedelta

SEED = 42
rng = np.random.default_rng(SEED)

CATEGORIES = {
    1: "Film & Animation", 2: "Autos & Vehicles", 10: "Music", 15: "Pets & Animals",
    17: "Sports", 19: "Travel & Events", 20: "Gaming", 22: "People & Blogs",
    23: "Comedy", 24: "Entertainment", 25: "News & Politics", 26: "Howto & Style",
    27: "Education", 28: "Science & Technology", 29: "Nonprofits & Activism",
    30: "Movies", 43: "Shows",
}
# categories 29, 30, 43 are deliberately never used by any video (useful for LEFT JOIN tasks)
USED = [1, 2, 10, 15, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28]

# per-category behaviour: mean lifespan (days on list), like rate, dislike/like ratio, comment rate, view scale
CAT = {
    1:  dict(life=3.0, like=0.030, dis=0.06, com=0.0030, scale=1.0),
    2:  dict(life=2.5, like=0.028, dis=0.05, com=0.0030, scale=0.7),
    10: dict(life=6.0, like=0.040, dis=0.04, com=0.0020, scale=3.0),
    15: dict(life=2.5, like=0.035, dis=0.03, com=0.0030, scale=0.8),
    17: dict(life=2.5, like=0.025, dis=0.05, com=0.0030, scale=1.0),
    19: dict(life=2.0, like=0.030, dis=0.04, com=0.0030, scale=0.6),
    20: dict(life=3.0, like=0.040, dis=0.06, com=0.0050, scale=1.2),
    22: dict(life=3.0, like=0.035, dis=0.08, com=0.0060, scale=1.0),
    23: dict(life=3.0, like=0.045, dis=0.04, com=0.0040, scale=1.4),
    24: dict(life=4.0, like=0.030, dis=0.07, com=0.0040, scale=1.3),
    25: dict(life=2.0, like=0.010, dis=0.35, com=0.0070, scale=0.8),
    26: dict(life=2.5, like=0.035, dis=0.04, com=0.0030, scale=0.8),
    27: dict(life=2.5, like=0.035, dis=0.03, com=0.0020, scale=0.7),
    28: dict(life=2.5, like=0.030, dis=0.05, com=0.0030, scale=0.8),
}
COUNTRIES = {
    # code: (days, category weights tweaks, view multiplier, extra life multiplier)
    "US": dict(days=80, tweak={10: 1.0, 24: 1.2, 23: 1.1}, vmul=1.0, lmul=1.0),
    "GB": dict(days=75, tweak={10: 1.8, 17: 1.2, 25: 0.8}, vmul=0.8, lmul=1.1),
    "IN": dict(days=75, tweak={24: 2.0, 25: 1.8, 10: 0.9, 27: 1.5}, vmul=1.4, lmul=0.8),
}
START = date(2017, 11, 14)
PER_DAY = 200

ARTISTS = ["Nova Kane", "Mira Solis", "The Hollow Pines", "DJ Aster", "Lena Ortiz", "Rook & Vale",
           "Kairo", "Sunny Park", "Blue Harbor", "Zed Rivera", "Anya Lux", "Echo District"]
NOUNS = ["Mystery", "Secret", "Challenge", "Reaction", "Review", "Trailer", "Highlights", "Tutorial",
         "Vlog", "Prank", "Interview", "Speech", "Recipe", "Unboxing", "Update", "Finale", "Breakdown"]
ADJ = ["Amazing", "Ultimate", "Crazy", "Official", "Honest", "Epic", "Surprising", "Incredible",
       "Insane", "Quiet", "Wild", "Perfect", "Final", "Brand New", "Shocking"]
TOPIC = ["Space", "Cars", "Cats", "Cricket", "Football", "Bangalore", "Paris", "Minecraft", "Phones",
         "Election", "Budget", "Guitar", "Pasta", "Robots", "Monsoon", "Chess", "Winter", "Festival"]
CAPS = ["OFFICIAL", "NEW", "LIVE", "FULL", "HD", "MUST", "WATCH", "EXCLUSIVE", "LEAKED", "FINALE"]

def vid_id():
    chars = list(string.ascii_letters + string.digits + "-_")
    return "".join(rng.choice(chars, 11))

def make_title(cat):
    if cat == 10:
        t = f"{rng.choice(ARTISTS)} - {rng.choice(TOPIC)} ({rng.choice(['Official Video','Lyric Video','Live'])})"
    else:
        t = f"{rng.choice(ADJ)} {rng.choice(TOPIC)} {rng.choice(NOUNS)}"
    r = rng.random()
    if r < 0.22:
        t += f" {rng.choice(CAPS)}"
    if rng.random() < 0.20:
        t += rng.choice(["!", "?", "!!", "?!"])
    if rng.random() < 0.10:
        t = t.upper()
    return t

def make_channels(n=450):
    names = [f"{rng.choice(ADJ)}{rng.choice(NOUNS)}{rng.integers(1,99)}" for _ in range(n)]
    cats = rng.choice(USED, n)
    pop = 1.0 / np.arange(1, n + 1) ** 0.9            # Zipf-like popularity
    return list(zip(names, cats)), pop / pop.sum()

CHANNELS, CH_POP = make_channels()
CH_BY_CAT = {c: [i for i, (_, cc) in enumerate(CHANNELS) if cc == c] for c in USED}

def new_video(country_cfg, start_day):
    w = np.array([1.0] * len(USED))
    for i, c in enumerate(USED):
        w[i] *= country_cfg["tweak"].get(c, 1.0)
    # weight categories so Entertainment / Music / People & Blogs dominate like the real data
    base = {24: 3.0, 10: 2.0, 22: 1.6, 23: 1.4, 25: 1.4, 1: 1.0, 20: 1.0, 17: 1.0, 26: 0.9, 28: 0.8,
            27: 0.7, 15: 0.5, 2: 0.5, 19: 0.4}
    w = w * np.array([base[c] for c in USED])
    cat = int(rng.choice(USED, p=w / w.sum()))
    pool = CH_BY_CAT[cat]
    pw = CH_POP[pool] / CH_POP[pool].sum()
    ch = CHANNELS[int(rng.choice(pool, p=pw))][0]
    p = CAT[cat]
    life = int(min(25, rng.geometric(1.0 / max(1.05, p["life"] * country_cfg["lmul"]))))
    base_views = float(np.exp(rng.normal(np.log(150000 * p["scale"] * country_cfg["vmul"]), 1.1)))
    like_rate = p["like"] * float(np.exp(rng.normal(0, 0.35)))
    dis_ratio = p["dis"] * float(np.exp(rng.normal(0, 0.5)))
    com_rate = p["com"] * float(np.exp(rng.normal(0, 0.4)))
    publish_offset = int(min(40, rng.geometric(0.45) - 1 + (rng.random() < 0.08) * rng.integers(5, 30)))
    first = START + timedelta(days=start_day)
    pub_dt = datetime.combine(first - timedelta(days=publish_offset), datetime.min.time()) + timedelta(
        seconds=int(rng.integers(0, 86400)))
    tags = "|".join(rng.choice(TOPIC, rng.integers(1, 5), replace=False)) if rng.random() > 0.08 else "[none]"
    return dict(
        video_id=vid_id(), title=make_title(cat), channel_title=ch, category_id=cat,
        publish_time=pub_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"), tags=tags,
        life=life, base_views=base_views, like_rate=like_rate, dis_ratio=dis_ratio, com_rate=com_rate,
        comments_disabled=bool(rng.random() < 0.02), ratings_disabled=bool(rng.random() < 0.012),
        description=("Watch this video. Subscribe for more content about "
                     f"{rng.choice(TOPIC).lower()}. Business enquiries in the channel about page.")
        if rng.random() > 0.035 else np.nan,
        age=0, start_day=start_day, views_now=0.0,
    )

def simulate_country(code, cfg, shared_pool):
    active, rows = [], []
    for d in range(cfg["days"]):
        # age out finished videos
        active = [v for v in active if v["age"] < v["life"]]
        # reuse a few videos already seen in other countries
        while len(active) < PER_DAY:
            if shared_pool and rng.random() < 0.10:
                src = shared_pool[int(rng.integers(0, len(shared_pool)))]
                # a video cannot trend before it is published, and should not be very old either
                gap = (START + timedelta(days=d) - datetime.strptime(src["publish_time"][:10], "%Y-%m-%d").date()).days
                if gap < 0 or gap > 30:
                    continue
                v = dict(src)
                v.update(age=0, start_day=d, life=int(min(25, rng.geometric(0.4))),
                         base_views=src["base_views"] * float(np.exp(rng.normal(0, 0.4))))
                if any(a["video_id"] == v["video_id"] for a in active):
                    continue
            else:
                v = new_video(cfg, d)
            active.append(v)
        # if somehow >200 (never, given the fill loop), trim
        today = START + timedelta(days=d)
        tdate = today.strftime("%y.%d.%m")
        for v in active[:PER_DAY]:
            k = v["age"]
            growth = (1 + 0.28) ** (k * 0.8)
            views = int(v["base_views"] * growth * float(np.exp(rng.normal(0, 0.03))))
            likes = int(views * v["like_rate"])
            dislikes = int(likes * v["dis_ratio"])
            comments = int(views * v["com_rate"])
            if v["ratings_disabled"]:
                likes = dislikes = 0
            if v["comments_disabled"]:
                comments = 0
            rows.append(dict(
                video_id=v["video_id"], trending_date=tdate, title=v["title"],
                channel_title=v["channel_title"], category_id=v["category_id"],
                publish_time=v["publish_time"], tags=v["tags"], views=views, likes=likes,
                dislikes=dislikes, comment_count=comments,
                thumbnail_link=f"https://i.ytimg.com/vi/{v['video_id']}/default.jpg",
                comments_disabled=v["comments_disabled"], ratings_disabled=v["ratings_disabled"],
                video_error_or_removed=False, description=v["description"]))
            v["age"] += 1
        # keep a sample of seen videos for cross-country reuse
    pool = {}
    for r in rows:
        pool.setdefault(r["video_id"], r)
    return rows

def finish(rows):
    df = pd.DataFrame(rows)
    # --- introduce realistic mess ---
    n = len(df)
    # a handful of removed/errored videos
    idx = rng.choice(n, int(n * 0.002), replace=False)
    df.loc[idx, "video_error_or_removed"] = True
    # a few blank comment counts and blank views
    idx = rng.choice(n, int(n * 0.0008), replace=False)
    df.loc[idx, "comment_count"] = np.nan
    idx = rng.choice(n, 4, replace=False)
    df.loc[idx, "likes"] = np.nan
    # exact duplicate rows (~0.5%)
    dup = df.sample(int(n * 0.005), random_state=int(rng.integers(0, 10**6)))
    df = pd.concat([df, dup]).sort_index(kind="stable").reset_index(drop=True)
    return df

shared = []
for code, cfg in COUNTRIES.items():
    rows = simulate_country(code, cfg, shared)
    # remember each video's meta for later countries to reuse
    seen = {}
    for r in rows:
        if r["video_id"] not in seen:
            seen[r["video_id"]] = dict(
                video_id=r["video_id"], title=r["title"], channel_title=r["channel_title"],
                category_id=r["category_id"], publish_time=r["publish_time"], tags=r["tags"],
                life=3, base_views=float(r["views"]), like_rate=(r["likes"] / max(r["views"], 1)) or 0.03,
                dis_ratio=(r["dislikes"] / max(r["likes"], 1)) or 0.05,
                com_rate=(r["comment_count"] / max(r["views"], 1)) or 0.003,
                comments_disabled=r["comments_disabled"], ratings_disabled=r["ratings_disabled"],
                description=r["description"], age=0, start_day=0, views_now=0.0)
    shared.extend(list(seen.values())[:1500])
    df = finish(rows)
    df.to_csv(f"{code}videos.csv", index=False)
    print(code, df.shape, df["video_id"].nunique(), "unique videos")

pd.DataFrame({"category_id": list(CATEGORIES), "category_name": list(CATEGORIES.values())}).to_csv(
    "categories.csv", index=False)
print("categories.csv written")
