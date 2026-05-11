# CBHDS Activity Dashboard

This Streamlit dashboard aggregates and visualizes multiple CBHDS data sources, including publications, funding, staffing (FTE), drop-ins, collaborations, and salary expenses.

---

# Overview

The dashboard combines data from:
- PubMed publications
- Google Sheets (FTE, Grants, Contracts, Internal Funding, Salaries)
- REDCap databases (Drop-ins and Collaborations)

It standardizes everything into **Fiscal Year (FY)** format (July–June cycle) for consistent reporting.

---

# Data Sources & Mapping

## 1. Publications
**Source:** `get_pubmed_publications()` (local Python module)

| Field | Source Column | Notes |
|------|--------------|------|
| Publication count | `pub_date` | Filtered by user-selected date range |

---

## 2. FTE Growth Over Time
**Source:** Google Sheet  
`FTE_URL`

### Columns Used:
| Dashboard Category | Sheet Column |
|-------------------|-------------|
| Affiliated Stats Faculty | `Affiliated Stats Faculty` |
| Students | `Students` |
| Admin | `Admin` |
| Undergraduate | `Bachelor's` |
| Master's | `Master's` |
| PhD | `PhD` |

### Output:
Stacked bar chart by **Year (Semester/FY index)** showing total FTE distribution.

---

## 3. Sponsored Research Funding

**Sources:**
Google Sheets via `load_sheet()`:
- `Grants`
- `Contracts/IPAs/TAPs`
- `Internal Funding`

### Key Transformation:
All funding is:
- Cleaned (removes `$`, `,`)
- Allocated across months of project duration
- Aggregated into **Fiscal Year (FY)**

---

### Grants

| Dashboard Metric | Sheet Column |
|-----------------|-------------|
| Total CBHDS Grant Funding | `Total Directs to CBHDS` |
| Start Date | `Start Date` |
| Duration | `Project Duration (# of Months)` |
| Status filter | `status_clean` (must contain "funded") |

---

### Contracts / IPAs / TAPs

| Dashboard Metric | Sheet Column |
|-----------------|-------------|
| Contract CBHDS Funding | `Total Directs to CBHDS` |
| Start Date | `Start Date` |
| Duration | `Project Duration (# of Months)` |

---

### Internal Funding

| Dashboard Metric | Sheet Column |
|-----------------|-------------|
| Internal Funding | `Total Funds ($)` |
| Start Date | `Start Date` |
| End Date | `End Date` |

---

### Derived Metrics

| Metric | Definition |
|-------|------------|
| External CBHDS Funding | Grants + Contracts |
| Total Funding | Internal + External + Statistics (COS) |

---

## 4. Salary Expenses

**Source:** Google Sheet  
`Salaries`

### Columns Used:

| Dashboard Metric | Sheet Column |
|-----------------|-------------|
| Salary Expenses | All salary columns excluding `Shared Costs` |
| Statistics (COS) | `Alexandra Hanlon` |
| Fiscal Year | extracted from `FY` column |

### Notes:
- “Shared Costs” are excluded from totals
- All salary values are cleaned from currency formatting
- Summed across all personnel columns

---

## 5. Drop-ins (REDCap)

**Source:** REDCap API  
`API_TOKEN`

### Mapping:

| Dashboard Metric | REDCap Field |
|-----------------|-------------|
| Drop-ins | `contact_date` |

### Processing:
- Converted to date
- Grouped into Fiscal Year:
  - FY starts in July
  - `FY = year + 1 if month >= 7 else year`

---

## 6. Collaborations (REDCap)

**Sources:**
- `API_TOKEN_COLLAB_1`
- `API_TOKEN_COLLAB_2`

### Mapping:

| Dataset | Date Field |
|--------|-----------|
| REDCap 1 | `todays_date` |
| REDCap 2 | `todays_date_c` |

### Filtering Rules:
- Dataset 2 only includes records where:
  - `sessiontype_c == "1"`

### Output:
Combined count of collaboration events per Fiscal Year.

---

## 7. Pending Funding

**Source:** Grants dataset (filtered)

### Definition:
Pending grants = `status_clean` contains `"pending"`

### Columns Used:
| Metric | Column |
|--------|-------|
| VT Funding | `Total Directs to VT` |
| CBHDS Funding | `Total Directs to CBHDS` |
| Duration | `Project Duration (# of Months)` |
| Start Date | `Start Date` |

### Output:
Stacked bar chart showing projected funding over time.

---

# Fiscal Year Logic

Across all datasets:

```python
FY = year + 1 if month >= 7 else year
