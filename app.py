#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from pubmed_publications import get_pubmed_publications

@st.cache_data(ttl=86400)
def load_publications():
    return get_pubmed_publications()

df = load_publications()

st.title("CBHDS Publications Dashboard")

st.metric(
    label="Publications (Mar 10 2025 – Mar 10 2026)",
    value=len(df)
)

st.dataframe(df)

