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

st.markdown(
    f'<div class="section"><h1>💜 WhatsApp Chat Analyzer</h1>'
    f'<p>Upload your exported chat (.txt) to explore timelines, heatmaps, words, emojis, and export reports.</p></div>',
    unsafe_allow_html=True
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")
    uploaded = st.file_uploader("Upload WhatsApp chat (.txt)", type=["txt"])
    show_raw = st.checkbox("Show first 100 rows", value=False)
    st.markdown("---")
    st.caption("Tip: Export from WhatsApp > More > Export chat (without media).")

def _mpl_style():
    plt.rcParams.update({
        "axes.facecolor": BG, "figure.facecolor": BG, "axes.edgecolor": FG,
        "axes.labelcolor": FG, "xtick.color": FG, "ytick.color": FG,
        "text.color": FG, "axes.titleweight": "bold", "grid.alpha": 0.25
    })

def _plot_hourly(df: pd.DataFrame):
    ha = hourly_timeline(df)
    fig, ax = plt.subplots()
    ax.bar(ha["hour"], ha["messages"], color=PURPLE)
    ax.set_xticks(range(0,24,1))
    ax.set_xlabel("Hour of Day (0–23)")
    ax.set_ylabel("Messages")
    ax.set_title("Hourly Message Distribution")
    ax.grid(True, linestyle=":")
    return fig

def _plot_daily(df: pd.DataFrame):
    tl = daily_timeline(df)
    tl["date"] = pd.to_datetime(tl["date"])
    fig, ax = plt.subplots()
    ax.plot(tl["date"], tl["messages"], color=PURPLE, linewidth=2)
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")
    ax.set_title("Daily Message Timeline")
    ax.grid(True, linestyle=":")
    fig.autofmt_xdate()
    return fig

def _plot_mps(df: pd.DataFrame):
    mps = messages_per_sender(df).head(15)
    fig, ax = plt.subplots()
    ax.barh(mps["sender"], mps["message_count"], color=PURPLE)
    ax.invert_yaxis()
    ax.set_xlabel("Messages")
    ax.set_title("Messages per Sender (Top 15)")
    return fig

def _plot_heatmap(df: pd.DataFrame):
    hm = weekday_hour_heatmap(df)
    fig, ax = plt.subplots()
    im = ax.imshow(hm.values, aspect="auto", cmap="magma")
    ax.set_yticks(range(7))
    ax.set_yticklabels(hm.index.tolist())
    ax.set_xticks(range(0,24,1))
    ax.set_title("Activity Heatmap (Weekday × Hour)")
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
        st.warning("Parsed, but no user messages detected. If your export uses a very different format, send 5–10 sample lines.")
    else:
        st.success(f"✅ Parsed {len(df)} rows, {df['sender'].notna().sum()} user messages.")

    if show_raw:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Raw preview")
        st.dataframe(df.head(100), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Tabs
    _mpl_style()
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
        with colA:
            st.pyplot(_plot_mps(df), use_container_width=True)
        with colB:
            st.pyplot(_plot_hourly(df), use_container_width=True)
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
        with col1:
            st.pyplot(_plot_top_words(df), use_container_width=True)
        with col2:
            st.pyplot(_plot_emojis(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Generate and View Reports")
        outdir = ROOT / "reports"
        ensure_dir(outdir)

        if st.button("✨ Generate PNG charts"):
            plot_all(df, outdir)
            st.success(f"Charts saved to: {outdir.resolve()}")

        # If charts exist, show them inline right away
        import os
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
