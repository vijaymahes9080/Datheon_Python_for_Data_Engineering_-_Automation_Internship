"""Generate synthetic benchmark datasets and offline HTML fixtures for StreamForge."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent
HTML_DIR = FIXTURES_DIR / "html"
HTML_DIR.mkdir(parents=True, exist_ok=True)

TITLES = [
    "Senior Data Engineer",
    "Data Platform Architect",
    "Lead ETL Developer",
    "Distributed Systems Engineer",
    "Python Backend Engineer",
    "Analytics Engineer",
    "Data Pipeline Specialist",
    "Cloud Infrastructure Engineer",
    "Database Reliability Engineer",
    "Real-time Stream Developer",
    "MLOps Engineer",
    "Big Data Software Engineer",
]

COMPANIES = [
    "Apex Cloud Systems",
    "DataFlow Labs",
    "Nexus Quant Analytics",
    "BluePeak Health AI",
    "Aether Robotics",
    "Cobalt FinTech",
    "Helios Energy Data",
    "Vanguard Cyber Tech",
    "Synthetix Systems",
    "Lumina Analytics",
    "Orbital Stream Inc",
    "Vertex Data Works",
]

LOCATIONS = [
    "Remote (US)",
    "Remote (EU)",
    "Remote (Global)",
    "Berlin, Germany",
    "London, UK",
    "Toronto, Canada",
    "Bangalore, India",
    "Austin, TX (Remote)",
    "Zurich, Switzerland",
    "Singapore (Remote)",
    "Amsterdam, Netherlands",
    "Seattle, WA",
]

CATEGORIES = [
    "Data Engineering",
    "Cloud & Infrastructure",
    "Backend Systems",
    "Analytics & BI",
    "Database Reliability",
    "ML Infrastructure",
]

SALARIES = [
    "$140,000 - $175,000",
    "$120,000 - $150,000",
    "€90,000 - €115,000",
    "£85,000 - £105,000",
    "CAD 130,000 - 160,000",
    "₹2,800,000 - ₹3,600,000",
    "$160,000 - $190,000",
    "$110,000 - $135,000",
    "€100,000 - €125,000",
    "£95,000 - £120,000",
    "$150,000 - $185,000",
    "CAD 145,000 - 175,000",
]

DATES = [
    "2026-10-10",
    "2026-10-12",
    "2026-10-14",
    "2026-10-15",
    "2026-10-16",
    "2026-10-17",
    "2026-10-18",
    "2026-10-19",
    "2026-10-20",
    "2026-10-21",
    "2 days ago",
    "Yesterday",
]

EMPLOYMENT_TYPES = ["Full-time", "Contract", "Full-time", "Full-time", "Contract", "Full-time"]


def generate_html_fixtures(records_per_page: int = 40, total_pages: int = 3) -> list[dict]:
    """Generate multi-page paginated HTML fixtures containing 100+ synthetic records."""
    all_records = []

    for page in range(1, total_pages + 1):
        cards_html = []
        start_idx = (page - 1) * records_per_page
        for i in range(records_per_page):
            rec_id = start_idx + i + 101
            title = f"{TITLES[rec_id % len(TITLES)]} #{rec_id}"
            company = COMPANIES[(rec_id * 3) % len(COMPANIES)]
            location = LOCATIONS[(rec_id * 5) % len(LOCATIONS)]
            category = CATEGORIES[(rec_id * 7) % len(CATEGORIES)]
            salary = SALARIES[(rec_id * 2) % len(SALARIES)]
            date_str = DATES[(rec_id * 11) % len(DATES)]
            emp_type = EMPLOYMENT_TYPES[rec_id % len(EMPLOYMENT_TYPES)]
            link = f"https://forge-jobs.internal/listings/eng-{rec_id}"

            record = {
                "record_id": rec_id,
                "job_title": title,
                "company_name": company,
                "salary_raw": salary,
                "location": location,
                "category": category,
                "employment_type": emp_type,
                "posted_date_raw": date_str,
                "source_url": link,
            }
            all_records.append(record)

            card = f"""      <article class="job-card" id="job-{rec_id}">
        <div class="job-header">
          <h2 class="job-title"><a class="job-link" href="{link}">{title}</a></h2>
          <span class="job-badge">{category}</span>
        </div>
        <div class="job-meta">
          <span class="job-company">{company}</span> &bull; 
          <span class="job-location">{location}</span> &bull; 
          <span class="job-type">{emp_type}</span>
        </div>
        <div class="job-details">
          <span class="job-salary">{salary}</span>
          <time class="job-date" datetime="{date_str}">{date_str}</time>
        </div>
      </article>"""
            cards_html.append(card)

        prev_link = (
            f'<a class="pagination-prev" href="page_{page - 1}.html">&laquo; Previous</a>'
            if page > 1
            else '<span class="pagination-disabled">&laquo; Previous</span>'
        )
        next_link = (
            f'<a class="pagination-next" href="page_{page + 1}.html">Next &raquo;</a>'
            if page < total_pages
            else '<span class="pagination-disabled">Next &raquo;</span>'
        )

        full_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>StreamForge Job Portal - Page {page}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <header>
    <h1>StreamForge Technical Job Board</h1>
    <p class="subtitle">Synthetic Benchmark Dataset - Page {page} of {total_pages}</p>
  </header>
  <main class="listings-container">
{chr(10).join(cards_html)}
  </main>
  <nav class="pagination">
    {prev_link}
    <span class="current-page">Page {page} of {total_pages}</span>
    {next_link}
  </nav>
</body>
</html>"""

        out_file = HTML_DIR / f"page_{page}.html"
        out_file.write_text(full_page, encoding="utf-8")
        print(f"Generated {out_file.name} with {records_per_page} records.")

    return all_records


def generate_messy_quality_fixtures(all_records: list[dict]) -> None:
    """Generate a realistic messy CSV and JSON dataset containing dirty data for Task 2."""
    import copy
    import pandas as pd

    messy_records = copy.deepcopy(all_records)

    # Inject dirty data cases into specific rows for robust testing:
    # 1. Whitespace and non-standard capitalization
    messy_records[0]["job_title"] = "   Lead Data Architect    "
    messy_records[0]["company_name"] = "  Apex   Cloud   Systems  "
    
    # 2. Currency symbol variations and formatting
    messy_records[1]["salary_raw"] = "EUR 95000 - 120000 / year"
    messy_records[2]["salary_raw"] = "€110,000"
    messy_records[3]["salary_raw"] = "GBP 85k - 95k"
    messy_records[4]["salary_raw"] = "₹25,00,000 - ₹35,00,000"
    messy_records[5]["salary_raw"] = "Negotiable / Competitive"  # Unparseable range
    
    # 3. Missing values / nulls
    messy_records[6]["salary_raw"] = ""
    messy_records[7]["location"] = "   "
    messy_records[8]["employment_type"] = None
    
    # 4. Inconsistent dates
    messy_records[9]["posted_date_raw"] = "15/10/2026"     # DD/MM/YYYY
    messy_records[10]["posted_date_raw"] = "10-18-2026"    # MM-DD-YYYY
    messy_records[11]["posted_date_raw"] = "3 days ago"    # Relative
    messy_records[12]["posted_date_raw"] = "INVALID_DATE"  # Should be flagged
    messy_records[13]["posted_date_raw"] = "2029-01-01"    # Future date violation

    # 5. Schema violation / rejected rows (missing mandatory field)
    messy_records[14]["job_title"] = ""  # Mandatory violation -> reject!
    messy_records[15]["source_url"] = "" # Mandatory violation -> reject!

    # 6. Exact duplicate rows
    messy_records.append(copy.deepcopy(messy_records[20]))
    messy_records.append(copy.deepcopy(messy_records[21]))

    df = pd.DataFrame(messy_records)
    
    # Intentionally use non-snake_case column names to test standardizer
    messy_df = df.rename(columns={
        "record_id": "Record ID",
        "job_title": "Job Title",
        "company_name": "Company Name",
        "salary_raw": "Salary / Compensation",
        "location": "Location (City/Country)",
        "category": "Job Category",
        "employment_type": "Employment Type",
        "posted_date_raw": "Date Posted",
        "source_url": "Source URL",
    })

    csv_path = FIXTURES_DIR / "raw_mock_jobs.csv"
    json_path = FIXTURES_DIR / "raw_mock_jobs.json"

    messy_df.to_csv(csv_path, index=False)
    messy_df.to_json(json_path, orient="records", indent=2)
    print(f"Generated {csv_path.name} and {json_path.name} with {len(messy_records)} records (including duplicates & anomalies).")


if __name__ == "__main__":
    records = generate_html_fixtures(records_per_page=40, total_pages=3)
    generate_messy_quality_fixtures(records)
