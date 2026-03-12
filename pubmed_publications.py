#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import time


def get_pubmed_publications():

    authors = [
        "Alexandra Hanlon",
        "Alicia Lozano",
        "Wenyan Ji",
        "Muyao Lin",
        "Rachel Silverman",
        "Christopher Grubb",
        "Xuemei Zhang",
        "Emmanuel Nartey",
        "Benjamin Brewer"
    ]

    affiliation = "Virginia"

    start_date = "2025/03/10"
    end_date = "2026/03/10"

    start_dt = datetime.strptime(start_date, "%Y/%m/%d")
    end_dt = datetime.strptime(end_date, "%Y/%m/%d")

    # Store articles by PMID
    articles_dict = {}

    for author_name in authors:

        query = f'{author_name}[Author] AND {affiliation}[Affiliation]'
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 1000,
            "retmode": "xml"
        }

        response = requests.get(search_url, params=params)
        root = ET.fromstring(response.content)

        id_list = [id_elem.text for id_elem in root.findall(".//Id")]

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        for pmid in id_list:

            fetch_params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml"
            }

            resp = requests.get(fetch_url, params=fetch_params)

            try:
                article_root = ET.fromstring(resp.content)
            except ET.ParseError:
                continue

            for article in article_root.findall(".//PubmedArticle"):

                medline = article.find("MedlineCitation")
                article_info = medline.find("Article")

                title = article_info.findtext("ArticleTitle", default="n/a").strip()

                journal = article_info.find("Journal").findtext("Title", default="n/a")

                pub_date_elem = article_info.find("Journal/JournalIssue/PubDate")

                year = pub_date_elem.findtext("Year")
                month = pub_date_elem.findtext("Month", "Jan")
                day = pub_date_elem.findtext("Day", "01")

                try:
                    pub_dt = datetime.strptime(f"{year}-{month}-{day}", "%Y-%b-%d")
                except:
                    pub_dt = None

                if pub_dt:

                    if pmid not in articles_dict:

                        articles_dict[pmid] = {
                            "title": title,
                            "authors": [author_name],
                            "journal": journal,
                            "pub_date": pub_dt,
                            "pubmed_link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                            
                        }

                    else:

                        if author_name not in articles_dict[pmid]["authors"]:
                            articles_dict[pmid]["authors"].append(author_name)

            time.sleep(0.1)

    # Convert to DataFrame
    df = pd.DataFrame(articles_dict.values())

    # Turn author list into readable string
    df["authors"] = df["authors"].apply(lambda x: ", ".join(x))

    return df

