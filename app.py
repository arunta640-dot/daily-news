"""Daily News - run:  streamlit run app.py"""
import datetime as dt

import pandas as pd
import streamlit as st

import news_engine
import news_history
import news_ui

st.set_page_config(page_title="Daily News", page_icon="📰", layout="centered")
st.markdown(f"<style>{news_ui.CSS}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=1800, show_spinner=False)
def get_daily_news():
    return news_engine.build_digest()


def get_must_know(digest):
    history = news_history.load_days(days=7)
    today = digest["generated_at"][:10]
    if digest["sections"] and today not in {d["date"] for d in history}:
        history.append({"date": today, "sections": digest["sections"]})  # include today's live news
    return news_history.build_must_know(history)


with st.spinner("Reading news feeds..."):
    digest = get_daily_news()

must_tab, today_tab = st.tabs(["Must know", "Today"])

with must_tab:
    st.markdown(news_ui.must_know_html(get_must_know(digest)), unsafe_allow_html=True)

with today_tab:
    st.markdown(news_ui.page_html(digest), unsafe_allow_html=True)
    if st.button("Refresh news"):
        get_daily_news.clear()
        st.rerun()
    with st.expander("Source report"):
        st.dataframe(pd.DataFrame(digest["source_report"]).T, use_container_width=True)
