---
# Title: Game Market Analysis Portfolio
---

# Biography 🧙

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://linkedin.com/in/yourname)
[![Resume](https://img.shields.io/badge/Resume-PDF-red)](Alec%20Bravo%20Resume%20Business%20Systems%20Analyst.pdf)

Hello, my name is Alec Bravo and I’ve spent the last 6+ years bridging the gap between business and technology. I’ve designed scalable processes, integrated systems, and built data-driven solutions for global teams using **SQL, Python, ETL pipelines, Redshift, Salesforce, Power BI, and process mapping.**  

From developing global dashboards tracking $5B+ in opportunities to launching automation tools that save thousands of manual hours annually, I have a proven track record of automating workflows, improving data quality, and delivering actionable insights.

Beyond my career, my adventures include traveling with my girlfriend, spending time with my 10 week old Labrador puppy named Bilbo, and exploring immersive RPGs and MMOs. Whether in the real world or virtual realms, I’m on the quest to conquer the next challenge. 

<p align="center">
  <figure style="display:inline-block; margin: 10px;">
    <img src="Bilbo Git.JPG" alt="Bilbo the Labrador" width="280" style="border-radius:15px;"/>
    <figcaption><i>Bilbo — 10-week-old Labrador</i></figcaption>
  </figure>
  <figure style="display:inline-block; margin: 10px;">
    <img src="fam git.JPG" alt="Alec and Girlfriend" width="280" style="border-radius:15px;"/>
    <figcaption><i>Traveling with my girlfriend in Kyoto Japan</i></figcaption>
  </figure>
</p>

---

# Game Market Insights: Early Access vs Full Release Performance

## 🛠 Tools & Technologies
![SQL](https://img.shields.io/badge/SQL-4479A1?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?logoColor=black)
![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visualstudiocode&logoColor=white)
![DBeaver](https://img.shields.io/badge/DBeaver-372923?logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)

---

## Process Map
![Process Map](game_data_process.drawio.png)

## Overview
Goal: Understand how Early Access compares to Full Releases in popularity and pricing trends, and which developers and price buckets drive owners.

## **Key Findings**

### **1. Popularity & Performance Trends**
- **Full Releases** consistently dominate in **absolute popularity** (Overall Rank), with a large share of the top spots in the market.  
- **Early Access (EA)**, while less dominant in absolute terms, **often achieves superior rankings within its own category** (Rank in Type) and in certain **release-year cohorts** (Rank in Release Year), suggesting strong appeal to targeted audiences.  
- EA performance shows **higher year-to-year volatility**, while Full Release exhibits steadier but slower shifts in rank.

### **2. Pricing Strategies Over Time (Last 10 Years)**
- **Free Titles**: Both EA and Full show a long-term decline in share, with Full Release maintaining slightly higher free-title proportions until recent years.  
- **Below $5 and Below $10**: Full Release maintains steady market presence, while EA shows small but consistent growth in these ranges.  
- **Below $20 and Below $30**: EA significantly outperforms Full Release in under-$20 share, pointing to **aggressive entry-level pricing** strategies. Full Release holds a more stable but smaller share in these ranges.  
- **$60 and Above**: Very small shares for both, consistent with AAA titles rarely using EA. **Full Release** dominates premium pricing, especially at **exactly $60**, where it holds nearly half of the market in recent years.

### **3. Developer & Market Concentration (Last 5 Years)**
- **Top 10 developers** in the last 5 years overwhelmingly release in **Full Release format** (78.88% of owners from Full Release titles).  
- Premium pricing at **$60** accounts for nearly **half of all Full Release owners** in this group.  
- EA titles from top devs cluster in **sub-$30 price buckets**, with occasional standouts achieving large owner counts.  
- Notable clustering of **AAA studios** in Full Release with high price points, contrasted by EA successes from **smaller or niche-focused developers**.

### **4. Strategic Implications**
- EA is most competitive when **cohort comparisons** are applied—year-specific or release-type specific—rather than in absolute market terms.  
- Pricing differentiation is a major driver of audience capture: **EA leans budget-friendly**, Full Release **retains premium positioning**.  
- Market share in top developer ranks reinforces the **strength of established studios** in dominating high-price tiers, while EA offers **a viable growth path** for emerging developers through affordability and community engagement.
> **Note on Data Scope:**  
> The dataset reflects the status of games **at the time of data extraction** and may not account for titles that have since transitioned out of Early Access into Full Release. This means certain high-impact releases—such as *Baldur’s Gate 3* and similar success stories—may be underrepresented in the EA performance metrics. As a result, some trends may shift if post-release performance for these titles were incorporated.

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
- [SQL script](game_data_project_sqlcode.sql) • [Notebook/Script](analyze_game_view_data.py)

## LinkedIn & Resume
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://linkedin.com/in/yourname)
[![Resume](https://img.shields.io/badge/Resume-PDF-red)](Alec%20Bravo%20Resume%20Business%20Systems%20Analyst.pdf)
