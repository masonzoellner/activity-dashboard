#!/usr/bin/env python
# coding: utf-8

# In[ ]:



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
from pubmed_publications import get_pubmed_publications


@st.cache_data(ttl=86400)
def load_publications():
    df = get_pubmed_publications()
    df["pub_date"] = pd.to_datetime(df["pub_date"])
    return df


df = load_publications()

st.title("CBHDS Publications Dashboard")

min_date = df["pub_date"].min().date()
today = date.today()

start_date, end_date = st.date_input(
    "Select publication date range",
    value=(min_date, today),
    min_value=min_date,
    max_value=today
)

filtered_df = df[
    (df["pub_date"].dt.date >= start_date) &
    (df["pub_date"].dt.date <= end_date)
]

st.metric(
    label="Publications in Selected Range",
    value=len(filtered_df)
)

st.dataframe(filtered_df)

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

st.divider()
st.subheader("Sponsored CBHDS Research Funding Over Time")

BASE_URL = "https://docs.google.com/spreadsheets/d/1kwP-OlmUgbtC_Rn8Hl2yaaV7GSLK_-zdVQOvmGLURUE/gviz/tq?tqx=out:csv&sheet="

from urllib.parse import quote

def load_sheet(sheet_name):
    encoded_name = quote(sheet_name)
    url = BASE_URL + encoded_name
    return pd.read_csv(url)


def get_fiscal_year(dt):
    if dt.month >= 7:
        return dt.year + 1
    return dt.year


def allocate_funding(df, amount_col, duration_col, start_col, funded_only=False):

    totals = {}

    for _, row in df.iterrows():

        try:
            if funded_only:
                if str(row["Funded "]).strip().lower() != "funded":
                    continue

            st.write("STATUS VALUE:", repr(row["Funded "]))
            
            raw_value = str(row[amount_col])
            clean_value = raw_value.replace("$", "").replace(",", "").strip()
            total = float(clean_value)

            duration_raw = row[duration_col]
            if pd.isna(duration_raw):
                continue
            duration = int(float(str(duration_raw).strip()))

            start = pd.to_datetime(row[start_col], errors="coerce")
            if pd.isna(start):
                continue

            monthly = total / duration

            for m in range(duration):
                current_date = start + pd.DateOffset(months=m)
                fy = get_fiscal_year(current_date)
                totals[fy] = totals.get(fy, 0) + monthly

        except:
            continue

    return totals


@st.cache_data(ttl=86400)
def load_funding_data():

    grants = load_sheet("Grants")
    st.write("Grants columns:")
    st.write(grants.columns)
    contracts = load_sheet("Contracts/IPAs/TAPs")
    internal = load_sheet("Internal Funding")

    g_totals = allocate_funding(
        grants,
        "Total Directs to CBHDS",
        "Project Duration (# of Months)",
        "Start Date",
        funded_only=True
    )

    c_totals = allocate_funding(
        contracts,
        "Total Directs to CBHDS",
        "Project Duration (# of Months)",
        "Start Date"
    )

    i_totals = allocate_funding(
        internal,
        "Total Funds ($)",
        "Project Duration (# of Months)",
        "Start Date"
    )

    all_years = set(g_totals) | set(c_totals) | set(i_totals)

    combined = {}
    for year in all_years:
        combined[year] = (
            g_totals.get(year, 0)
            + c_totals.get(year, 0)
            + i_totals.get(year, 0)
        )

    df = pd.DataFrame(
        [(int(k), v) for k, v in combined.items() if str(k).isdigit()],
        columns=["Fiscal Year", "Funding"]
    ).sort_values("Fiscal Year")

    return df


# -----------------------------
# Load + Filter
# -----------------------------

funding_df = load_funding_data()

from datetime import datetime

today = datetime.today()

current_fy = today.year + 1 if today.month >= 7 else today.year

funding_df = funding_df[
    (funding_df["Fiscal Year"] >= 2019) &
    (funding_df["Fiscal Year"] <= current_fy)
]

funding_df["FY Label"] = funding_df["Fiscal Year"].apply(
    lambda x: f"FY{int(x) % 100}"
)

# -----------------------------
# Plot
# -----------------------------

fig2, ax2 = plt.subplots()

ax2.plot(
    funding_df["FY Label"],
    funding_df["Funding"],
    marker='o'
)

# ✅ Add value labels
for x, y in zip(funding_df["FY Label"], funding_df["Funding"]):
    ax2.text(
        x,
        y,
        f"${y/1e6:.1f}M",
        ha='center',
        va='bottom',
        fontsize=9
    )

ax2.set_xlabel("Fiscal Year")
ax2.set_ylabel("Total Funding ($)")
ax2.set_title("Sponsored CBHDS Research Funding")

st.pyplot(fig2)

def clean_money(value):
    try:
        val = str(value).replace("$", "").replace(",", "").strip()
        if val == "" or val.lower() == "nan":
            return 0.0
        return float(val)
    except:
        return 0.0

def allocate_pending_funding(df):

    vt_totals = {}
    cbhds_totals = {}

    for _, row in df.iterrows():
        try:
            status = str(row["Funded "]).strip().lower()

            if "pending" not in status:
                continue

            vt_total = clean_money(row["Total Directs to VT"])
            cbhds_total = clean_money(row["Total Directs to CBHDS"])

            duration_raw = row["Project Duration (# of Months)"]
            if pd.isna(duration_raw):
                continue

            duration = int(float(str(duration_raw).strip()))

            start = pd.to_datetime(row["Start Date"], errors="coerce")
            if pd.isna(start):
                continue

            vt_monthly = vt_total / duration
            cbhds_monthly = cbhds_total / duration

            for m in range(duration):
                current_date = start + pd.DateOffset(months=m)
                fy = get_fiscal_year(current_date)

                vt_totals[fy] = vt_totals.get(fy, 0) + vt_monthly
                cbhds_totals[fy] = cbhds_totals.get(fy, 0) + cbhds_monthly

        except Exception as e:
            print("Row error:", e)
            continue

    return vt_totals, cbhds_totals

@st.cache_data(ttl=86400)
def load_pending_data():

    grants = load_sheet("Grants")

    vt_totals, cbhds_totals = allocate_pending_funding(grants)

    all_years = set(vt_totals) | set(cbhds_totals)

    data = []

    for year in all_years:
        if str(year).isdigit():
            data.append((
                int(year),
                vt_totals.get(year, 0),
                cbhds_totals.get(year, 0)
            ))

    df = pd.DataFrame(
        data,
        columns=["Fiscal Year", "VT", "CBHDS"]
    ).sort_values("Fiscal Year")

    return df

from datetime import datetime

today = datetime.today()
current_fy = today.year + 1 if today.month >= 7 else today.year

pending_df = load_pending_data()

pending_df = pending_df[
    pending_df["Fiscal Year"] >= current_fy
]

pending_df["FY Label"] = pending_df["Fiscal Year"].apply(
    lambda x: f"FY{int(x) % 100}"
)

st.subheader("Pending Funding")

fig3, ax3 = plt.subplots()

ax3.bar(
    pending_df["FY Label"],
    pending_df["VT"],
    label="Total Directs to VT"
)

ax3.bar(
    pending_df["FY Label"],
    pending_df["CBHDS"],
    bottom=pending_df["VT"],
    label="Total Directs to CBHDS"
)

for i, (vt, cbhds) in enumerate(zip(pending_df["VT"], pending_df["CBHDS"])):

    # Label for VT (bottom bar)
    if vt > 0:
        ax3.text(
            i,
            vt / 2,  # middle of VT bar
            f"${vt/1e6:.1f}M",
            ha='center',
            va='center',
            fontsize=8,
            color='white'
        )

    # Label for CBHDS (top bar)
    if cbhds > 0:
        ax3.text(
            i,
            vt + (cbhds / 2),  # middle of CBHDS segment
            f"${cbhds/1e6:.1f}M",
            ha='center',
            va='center',
            fontsize=8,
            color='white'
        )

ax3.set_xlabel("Fiscal Year")
ax3.set_ylabel("Funding ($)")
ax3.set_title("Pending CBHDS Research Funding")

ax3.legend()

st.pyplot(fig3)

API_TOKEN = "71F77DB5020F97309F14880D1E2D254A"

import requests

@st.cache_data(ttl=3600)
def load_redcap_data():

    url = "https://redcap.vtc.vt.edu/api/" 

    payload = {
        'token': API_TOKEN,
        'content': 'record',
        'format': 'json',
        'type': 'flat'
    }

    response = requests.post(url, data=payload)
    data = response.json()

    df = pd.DataFrame(data)
    print(df.columns)

    return df


def process_dropins(df):

    # 🔁 CHANGE THIS to your actual date column name
    df["date"] = pd.to_datetime(df["contact_date"], errors="coerce")

    df = df.dropna(subset=["date"])

    df["Fiscal Year"] = df["date"].apply(
        lambda x: x.year + 1 if x.month >= 7 else x.year
    )

    counts = df.groupby("Fiscal Year").size().reset_index(name="Drop-ins")

    counts["FY Label"] = counts["Fiscal Year"].apply(
        lambda x: f"FY{int(x) % 100}"
    )

    return counts

st.subheader("Drop-ins by Fiscal Year")

dropins_df = process_dropins(load_redcap_data())

fig4, ax4 = plt.subplots()

ax4.plot(
    dropins_df["FY Label"],
    dropins_df["Drop-ins"],
    marker='o'
)

# Labels on points
for x, y in zip(dropins_df["FY Label"], dropins_df["Drop-ins"]):
    ax4.text(x, y, str(int(y)), ha='center', va='bottom')

ax4.set_xlabel("Fiscal Year")
ax4.set_ylabel("Number of Drop-ins")
ax4.set_title("CBHDS Drop-ins Over Time")

st.pyplot(fig4)
