# --- ensure project root is on sys.path ---
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from src.parser import parse_chat
from src.analyzer import (
    basic_stats, messages_per_sender, daily_timeline, hourly_timeline,
    weekday_hour_heatmap, top_words, emoji_freq
)
from src.visuals import plot_all
from src.utils import ensure_dir

# ---------- THEME ----------
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide", page_icon="💬")
PURPLE = "#7C3AED"; BG="#0B0B10"; FG="#EAEAF2"; CARD="#151523"

st.markdown(f"""
<style>
:root {{ --purple:{PURPLE}; --bg:{BG}; --fg:{FG}; --card:{CARD}; }}
html, body, [data-testid="stAppViewContainer"] {{ background: var(--bg); }}
h1,h2,h3,h4,h5,h6,p,span,div {{ color: var(--fg) !important; }}
.block-container {{ padding-top: 1.25rem; padding-bottom: 2rem; }}
.section {{ background: var(--card); border: 1px solid rgba(255,255,255,.06);
           border-radius: 16px; padding: 18px; margin-bottom: 16px; }}
.metric {{ text-align:center; border-radius:14px; padding:12px; background: rgba(124,58,237,.07); }}
hr {{ border: 0; border-top: 1px solid rgba(255,255,255,.08); margin: 8px 0 16px 0; }}
</style>
""", unsafe_allow_html=True)


# --- Clean Full Banner Header (Final Fix) ---
st.markdown("""
<style>
/* Remove container squeezing */
.block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Full-screen width hero wrapper */
.hero-section {
    width: 100vw;
    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    margin-top: 30px; /* <-- Moves banner DOWN (Fixes your issue) */
    margin-bottom: 30px;
    padding: 50px 60px; /* <-- Makes the banner taller and more premium */
    background: linear-gradient(135deg, #7C3AED, #3B0A68);
    border-radius: 14px;
    box-shadow: 0 8px 35px rgba(124,58,237,0.5);
    border: 1px solid rgba(255,255,255,0.08);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Title */
.hero-title {
    font-size: 42px;
    font-weight: 900;
    color: #FFFFFF;
    margin-bottom: 8px;
}

/* Subtitle */
.hero-sub {
    font-size: 18px;
    font-weight: 400;
    opacity: 0.92;
    color: #EDE9FF;
}
</style>

<div class="hero-section">
    <div class="hero-title">💜 WhatsApp Chat Analyzer</div>
    <div class="hero-sub">Upload your chat (.txt) — media lines are automatically removed for clean analysis.</div>
</div>
""", unsafe_allow_html=True)






# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")
    uploaded = st.file_uploader("Upload WhatsApp chat (.txt)", type=["txt"])
    show_raw = st.checkbox("Show first 100 rows", value=False)
    st.markdown("---")
    st.caption("Tip: Export from WhatsApp > More > Export chat (without media).")

def _mpl_theme():
    plt.rcParams.update({
        "axes.facecolor": BG, "figure.facecolor": BG, "axes.edgecolor": FG,
        "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG,
        "text.color": FG, "axes.titleweight": "bold", "grid.alpha": 0.25
    })

def _emoji_font():
    candidates = ["Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", "Twemoji Mozilla"]
    for fam in candidates:
        try:
            matplotlib.font_manager.findfont(fam, fallback_to_default=False)
            plt.rcParams["font.family"] = fam
            return fam
        except Exception:
            continue
    return None

def _plot_hourly(df: pd.DataFrame):
    ha = hourly_timeline(df)
    fig, ax = plt.subplots()
    ax.bar(ha["hour"], ha["messages"], color=PURPLE)
    ax.set_xticks(range(0,24,1))
    ax.set_xlabel("Hour of Day (0–23)"); ax.set_ylabel("Messages")
    ax.set_title("Hourly Message Distribution"); ax.grid(True, linestyle=":")
    return fig

def _plot_daily(df: pd.DataFrame):
    tl = daily_timeline(df); tl["date"] = pd.to_datetime(tl["date"])
    fig, ax = plt.subplots()
    ax.plot(tl["date"], tl["messages"], color=PURPLE, linewidth=2)
    ax.set_xlabel("Date"); ax.set_ylabel("Messages"); ax.set_title("Daily Message Timeline")
    ax.grid(True, linestyle=":"); fig.autofmt_xdate()
    return fig

def _plot_mps(df: pd.DataFrame):
    mps = messages_per_sender(df).head(15)
    fig, ax = plt.subplots()
    ax.barh(mps["sender"], mps["message_count"], color=PURPLE)
    ax.invert_yaxis(); ax.set_xlabel("Messages"); ax.set_title("Messages per Sender (Top 15)")
    return fig

def _plot_heatmap(df: pd.DataFrame):
    hm = weekday_hour_heatmap(df)
    fig, ax = plt.subplots()
    im = ax.imshow(hm.values, aspect="auto", cmap="magma")
    ax.set_yticks(range(7)); ax.set_yticklabels(hm.index.tolist())
    ax.set_xticks(range(0,24,1)); ax.set_title("Activity Heatmap (Weekday × Hour)")
    fig.colorbar(im, ax=ax, label="Messages")
    return fig

def _plot_top_words(df: pd.DataFrame):
    tw = top_words(df, 25)
    fig, ax = plt.subplots()
    ax.barh(tw["word"][::-1], tw["count"][::-1], color=PURPLE)
    ax.set_title("Top Words")
    return fig

def _plot_emojis(df: pd.DataFrame):
    ef = emoji_freq(df, 25)
    fig, ax = plt.subplots()
    ax.barh(ef["emoji"][::-1], ef["count"][::-1], color=PURPLE)
    ax.set_title("Top Emojis")
    return fig

# ---------- MAIN ----------
if uploaded:
    tmp = ROOT / "data" / "raw" / "_uploaded.txt"
    ensure_dir(tmp.parent)
    tmp.write_bytes(uploaded.getbuffer())
    df = parse_chat(tmp)

    if df.empty or df["sender"].notna().sum() == 0:
        st.warning("Parsed, but no user messages detected. If your export format is unique, share a few sample lines.")
    else:
        st.success(f"Parsed {len(df)} rows, {df['sender'].notna().sum()} user messages.")

    if _emoji_font() is None:
        st.info("Note: Emojis may not render fully unless an emoji font (e.g., Segoe UI Emoji / Noto Color Emoji) is installed.")

    if show_raw:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Raw preview")
        st.dataframe(df.head(100), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    _mpl_theme()
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Activity", "Words & Emojis", "Reports"])

    with tab1:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        stats = basic_stats(df)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Messages", stats["total_messages"])
        c2.metric("Participants", len(stats["participants"]))
        c3.metric("Media msgs", stats["media_messages"])
        c4.metric("Emojis used", stats["total_emojis"])
        c5.metric("Links shared", stats["links_shared"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section">', unsafe_allow_html=True)
        colA, colB = st.columns((1,1))
        with colA: st.pyplot(_plot_mps(df), use_container_width=True)
        with colB: st.pyplot(_plot_hourly(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.pyplot(_plot_daily(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.pyplot(_plot_heatmap(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        col1, col2 = st.columns((1,1))
        with col1: st.pyplot(_plot_top_words(df), use_container_width=True)
        with col2: st.pyplot(_plot_emojis(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Generate and View Reports")
        outdir = ROOT / "reports"
        ensure_dir(outdir)

        if st.button("✨ Generate PNG charts"):
            plot_all(df, outdir)
            st.success(f"Charts saved to: {outdir.resolve()}")

        # show charts if exist
        pngs = [
            "chart_messages_per_sender.png",
            "chart_daily_timeline.png",
            "chart_hourly_timeline.png",
            "chart_weekday_hour_heatmap.png",
            "chart_wordcloud.png",
            "chart_emoji_top.png",
        ]
        available = [p for p in pngs if (outdir / p).exists()]
        if available:
            st.write("Preview of saved charts:")
            cols = st.columns(2)
            for i, name in enumerate(available):
                with cols[i % 2]:
                    st.image(str(outdir / name), caption=name, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Upload a WhatsApp chat `.txt` in the left sidebar to begin.")
