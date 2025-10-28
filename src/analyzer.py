from collections import Counter
import pandas as pd
import numpy as np
from pathlib import Path
from .utils import extract_urls, ensure_dir

STOPWORDS = set((
    "the","to","you","and","a","of","in","is","for","on","it","i","me","my","we","our","your","yours",
    "at","this","that","was","are","be","with","as","not","have","has","had","but","or","so","if","then",
    "they","them","he","she","him","her","from","by","an","am","its","there","here"
))

def basic_stats(df: pd.DataFrame) -> dict:
    data = df.copy()
    data = data[~data["is_system"].fillna(False)]
    total_msgs = len(data)
    participants = sorted([s for s in data["sender"].dropna().unique()])
    media_msgs = int(data["is_media"].sum())
    emojis = int(data["emoji_count"].sum())
    links = sum(len(extract_urls(t)) for t in data["message"].dropna())
    return {
        "total_messages": total_msgs,
        "participants": participants,
        "media_messages": media_msgs,
        "total_emojis": emojis,
        "links_shared": links,
        "date_min": str(df["timestamp"].min()) if "timestamp" in df else None,
        "date_max": str(df["timestamp"].max()) if "timestamp" in df else None,
    }

def messages_per_sender(df: pd.DataFrame) -> pd.DataFrame:
    d = df[~df["is_system"] & df["sender"].notna()].groupby("sender")["message"] \
        .count().sort_values(ascending=False).reset_index(name="message_count")
    return d

def daily_timeline(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["timestamp"].notna()].groupby("date")["message"].count().reset_index(name="messages")
    return d

def hourly_timeline(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["hour"].notna()].groupby("hour")["message"].count().reindex(range(24), fill_value=0) \
        .reset_index(name="messages")
    return d

def weekday_hour_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["timestamp"].notna()].copy()
    sub["weekday_num"] = pd.to_datetime(sub["date"]).dt.dayofweek  # Mon=0
    mat = sub.pivot_table(index="weekday_num", columns="hour", values="message", aggfunc="count", fill_value=0)
    mat = mat.reindex(index=range(7), fill_value=0).reindex(columns=range(24), fill_value=0)
    mat.index = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    return mat

def top_words(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    counter = Counter()

    # Remove system messages and detected media messages entirely
    text_df = df[(~df["is_system"]) & (~df["is_media"]) & (df["message"].notna())]

    # Additional unwanted tokens
    EXCLUDE = {"media", "omitted"}

    for t in text_df["message"]:
        for w in t.lower().split():
            w = "".join(ch for ch in w if ch.isalnum())  # keep only alphanumeric
            if not w or w.isdigit() or w in STOPWORDS or w in EXCLUDE:
                continue
            counter[w] += 1

    items = counter.most_common(top_n)
    return pd.DataFrame(items, columns=["word", "count"])


def emoji_freq(df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    counter = Counter()
    for s in df["emoji_list"].dropna():
        for e in list(s):
            counter[e] += 1
    items = counter.most_common(top_n)
    return pd.DataFrame(items, columns=["emoji","count"])

def export_csv_summaries(df: pd.DataFrame, outdir: Path):
    ensure_dir(outdir)
    pd.DataFrame([basic_stats(df)]).to_csv(outdir / "summary_overall.csv", index=False)
    messages_per_sender(df).to_csv(outdir / "summary_messages_per_sender.csv", index=False)
    daily_timeline(df).to_csv(outdir / "summary_daily_timeline.csv", index=False)
    hourly_timeline(df).to_csv(outdir / "summary_hourly_timeline.csv", index=False)
    top_words(df).to_csv(outdir / "summary_top_words.csv", index=False)
    emoji_freq(df).to_csv(outdir / "summary_emoji_freq.csv", index=False)
    weekday_hour_heatmap(df).to_csv(outdir / "summary_weekday_hour_heatmap.csv")
