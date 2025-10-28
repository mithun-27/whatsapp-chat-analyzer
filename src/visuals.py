from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from wordcloud import WordCloud

from .analyzer import (
    messages_per_sender, daily_timeline, hourly_timeline,
    weekday_hour_heatmap, top_words, emoji_freq, _clean_messages
)
from .utils import ensure_dir

PURPLE = "#7C3AED"
FG     = "#EAEAF2"
BG     = "#0B0B10"

def _set_theme():
    plt.rcParams.update({
        "axes.facecolor": BG,
        "figure.facecolor": BG,
        "axes.edgecolor": FG,
        "axes.labelcolor": FG,
        "xtick.color": FG,
        "ytick.color": FG,
        "text.color": FG,
        "axes.titleweight": "bold",
        "grid.alpha": 0.25
    })

def _set_emoji_font():
    """Try to use an emoji-capable font so emoji labels render correctly."""
    candidates = [
        "Segoe UI Emoji",       # Windows
        "Noto Color Emoji",     # Linux
        "Apple Color Emoji",    # macOS
        "Twemoji Mozilla",
    ]
    for fam in candidates:
        try:
            matplotlib.font_manager.findfont(fam, fallback_to_default=False)
            plt.rcParams["font.family"] = fam
            return fam
        except Exception:
            continue
    return None

def _save(path: Path, title: str):
    plt.title(title)
    plt.grid(True, linestyle=":")
    plt.tight_layout()
    plt.savefig(path, dpi=160, facecolor=BG)
    plt.close()

def plot_all(df: pd.DataFrame, outdir: Path):
    ensure_dir(outdir)
    _set_theme()
    _set_emoji_font()

    # 1) Messages per sender
    mps = messages_per_sender(df).head(15)
    plt.figure()
    plt.barh(mps["sender"], mps["message_count"], color=PURPLE)
    plt.gca().invert_yaxis()
    _save(outdir / "chart_messages_per_sender.png", "Messages per Sender")

    # 2) Daily timeline
    tl = daily_timeline(df)
    plt.figure()
    plt.plot(pd.to_datetime(tl["date"]), tl["messages"], linewidth=2, color=PURPLE)
    plt.xticks(rotation=45, ha="right")
    _save(outdir / "chart_daily_timeline.png", "Daily Message Timeline")

    # 3) Hourly distribution
    ha = hourly_timeline(df)
    plt.figure()
    plt.bar(ha["hour"], ha["messages"], color=PURPLE)
    plt.xticks(range(0, 24, 1))
    _save(outdir / "chart_hourly_timeline.png", "Hourly Message Distribution")

    # 4) Weekday x Hour heatmap
    hm = weekday_hour_heatmap(df)
    plt.figure()
    im = plt.imshow(hm.values, aspect="auto", cmap="magma")
    plt.yticks(ticks=range(7), labels=hm.index.tolist())
    plt.xticks(ticks=range(0,24,1), labels=list(range(0,24,1)))
    plt.colorbar(im, label="Messages")
    _save(outdir / "chart_weekday_hour_heatmap.png", "Activity Heatmap (Weekday × Hour)")

    # 5) WordCloud (built ONLY from clean messages; excludes <Media omitted>)
    clean_msgs = _clean_messages(df)
    # Build a weighted text using the same filtering as top_words (keeps results consistent)
    tw = top_words(df, 200)
    wc_text = " ".join([(w + " ") * c for w, c in tw.values])

    # Choose an emoji-capable font if available; otherwise default
    font_path = None
    for candidate in [
        "C:/Windows/Fonts/seguiemj.ttf",                 # Segoe UI Emoji (Windows)
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/System/Library/Fonts/Apple Color Emoji.ttc",
    ]:
        if Path(candidate).exists():
            font_path = candidate
            break

    wc = WordCloud(
        width=1400, height=700, background_color=BG,
        colormap="magma", prefer_horizontal=0.9,
        font_path=font_path
    ).generate(wc_text if wc_text.strip() else "chat")

    plt.figure(figsize=(10,5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    _save(outdir / "chart_wordcloud.png", "Word Cloud (Top Words)")

    # 6) Emoji frequency
    ef = emoji_freq(df, 25)
    plt.figure()
    plt.barh(ef["emoji"], ef["count"], color=PURPLE)
    plt.gca().invert_yaxis()
    _save(outdir / "chart_emoji_top.png", "Top Emojis")
