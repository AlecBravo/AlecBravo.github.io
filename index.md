---
# Title: Game Market Analysis Portfolio
---

# Game Market Analysis (EA vs Full Release)

Alec Bravo — SQL • Python • DuckDB • Matplotlib • Plotly • VS Code

## Process Map
- [Process Map (PDF)](game_data_process.drawio.pdf)

## Overview
Goal: Understand how Early Access compares to Full Releases in popularity and pricing trends, and which developers and price buckets drive owners.

## Key Findings
- Full Releases win on absolute popularity; EA performs strongly in year- and type-normalized ranks.
- Pricing share shows growth of EA under \$20; \$60+ is niche for both.
- Sankey reveals top developers flow mostly to Full Release and higher price tiers.

## Charts
- **Plot A — Median Rank bump charts (last 5 years):**  
  ![Plot A](Median Rank by Year & Release Type - Last 5 years.png)

- **Plot B — Price Range Mix (last 10 years):**  
  ![Plot B](price range mix EA vs Full Release over 10 years.png)

- **Plot C — Interactive Sankey (Top Dev → Release Type → Price Range):**  
  👉 [Open interactive Sankey](Sankey Top 10 Developers last 5 years.png)

## Methods & Code
- **SQL:** price bucketing, EA join, rank windows (`ROW_NUMBER`), date parsing.
- **Python:** DuckDB query → pandas shaping → robust plotting with Matplotlib/Plotly.
- [SQL script](../sql/analysis.sql) • [Notebook/Script](../notebooks/analysis.py)

## About & Resume
- [Resume (PDF)](assets/resume.pdf)
- Contact: you@domain.com • LinkedIn: https://linkedin.com/in/yourname
