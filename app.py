#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
from datetime import date, timedelta
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

default_start = today - timedelta(days=365)

if default_start < min_date:
    default_start = min_date

start_date, end_date = st.date_input(
    "Select publication date range",
    value=(default_start, today),
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

st.dataframe(filtered_df, hide_index=True)

import matplotlib.pyplot as plt

st.header("CBHDS FTE Growth Over Time")

# Load Excel
fte_df = pd.read_excel("CBHDS Growth FTE Data 11-12-25.xlsx")

# Select only the columns needed
fte_plot = fte_df[
    ["Year", "Affiliated Stats Faculty", "Students", "Admin", "Bachelor's", "Master's", "PhD"]
]

fte_plot = fte_plot.set_index("Year")

# Create stacked bar chart
fig, ax = plt.subplots()

fte_plot.plot(
    kind="bar",
    stacked=True,
    ax=ax
)

ax.set_xlabel("Semester")
ax.set_ylabel("Total FTE")
ax.set_title("CBHDS FTE Growth Over Time")
ax.legend(title="Role", bbox_to_anchor=(1.05, 1))

st.pyplot(fig)
