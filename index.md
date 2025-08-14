---
# Title: Game Market Analysis Portfolio
---

# 🧙 Biography

My name is Alec Bravo, and I’ve spent the last 6+ years bridging the gap between business and technology. I’ve designed scalable processes, integrated systems, and built data-driven solutions for global teams using **SQL, Python, ETL pipelines, Redshift, Salesforce, Power BI, and process mapping.**  

From developing global dashboards tracking $5B+ in opportunities to launching automation tools that save thousands of manual hours annually, I have a proven track record of automating workflows, improving data quality, and delivering actionable insights.

Beyond my career, my adventures include traveling with my girlfriend, spending time with my 10 week old Labrador puppy named Bilbo, and exploring immersive RPGs and MMOs. Whether in the real world or virtual realms, I’m on the quest to conquer the next challenge. 

<p align="center">
  <img src="Bilbo Git.JPG" alt="Bilbo the Labrador" width="300" style="margin-right:10px;"/>
  <img src="fam git.JPG" alt="Alec and Girlfriend" width="300"/>
</p>

---

# Game Market Analysis (EA vs Full Release)

Alec Bravo — SQL • Python • DuckDB • Matplotlib • Plotly • VS Code

---

## Process Map
![Process Map](game_data_process.drawio.png)

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

- **Plot C — Sankey (Top Dev → Release Type → Price Range):**  
  ![Plot C](Sankey Top 10 Developers last 5 years.png)

## Methods & Code
- **SQL:** price bucketing, EA join, rank windows (`ROW_NUMBER`), date parsing.
- **Python:** DuckDB query → pandas shaping → robust plotting with Matplotlib/Plotly.
- [SQL script](../sql/analysis.sql) • [Notebook/Script](../notebooks/analysis.py)

## About & Resume
- [Resume (PDF)](assets/resume.pdf)
- Contact: you@domain.com • LinkedIn: https://linkedin.com/in/yourname
