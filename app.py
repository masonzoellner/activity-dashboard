#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from datetime import date
from pubmed_publications import get_pubmed_publications


@st.cache_data(ttl=86400)
def load_publications():
    df = get_pubmed_publications()
    df["pub_date"] = pd.to_datetime(df["pub_date"])
    return df


df = load_publications()

st.title("CBHDS Publications Dashboard")

# -----------------------------
# Date limits
# -----------------------------

min_date = df["pub_date"].min().date()
today = date.today()

# -----------------------------
# Date selector
# -----------------------------

start_date, end_date = st.date_input(
    "Select publication date range",
    value=(min_date, today),
    min_value=min_date,
    max_value=today
)

# -----------------------------
# Filter data
# -----------------------------

filtered_df = df[
    (df["pub_date"].dt.date >= start_date) &
    (df["pub_date"].dt.date <= end_date)
]

# -----------------------------
# Metrics
# -----------------------------

st.metric(
    label="Publications in Selected Range",
    value=len(filtered_df)
)

# -----------------------------
# Table
# -----------------------------

st.dataframe(filtered_df)

