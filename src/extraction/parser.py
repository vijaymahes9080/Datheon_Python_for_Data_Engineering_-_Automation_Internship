"""HTML parsing module using BeautifulSoup4 for structured record extraction."""

from __future__ import annotations

import datetime
import logging
from typing import Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger("streamforge.extraction.parser")


class HTMLParser:
    """Resilient HTML parser for technical job board extraction and pagination discovery."""

    def __init__(self, base_url: str = ""):
        self.base_url = base_url

    def parse_page(self, html_content: str, current_url: str = "") -> tuple[list[dict[str, Any]], str | None]:
        """Parse HTML string and extract job records and the next page URL.

        Args:
            html_content: Raw HTML text of the page.
            current_url: Context URL used to resolve relative links.

        Returns:
            A tuple of (extracted_records, next_page_url).
        """
        soup = BeautifulSoup(html_content, "html.parser")
        effective_base = current_url or self.base_url

        records: list[dict[str, Any]] = []
        card_elements = soup.select(".job-card") or soup.select("article") or soup.select(".listing-item")

        logger.info(f"Found {len(card_elements)} card elements on page")

        for card in card_elements:
            record = self._extract_card(card, effective_base)
            if record:
                records.append(record)

        next_page_url = self._extract_next_page(soup, effective_base)
        return records, next_page_url

    def _extract_card(self, card: Tag, base_url: str) -> dict[str, Any] | None:
        """Safely extract individual record fields from a card element."""
        # 1. Job Title & Source Link
        title_el = card.select_one(".job-title") or card.select_one("h2") or card.select_one("h3")
        link_el = card.select_one(".job-link") or card.select_one("a")
        
        job_title = title_el.get_text(strip=True) if title_el else ""
        raw_url = link_el.get("href", "") if link_el else ""
        source_url = urljoin(base_url, str(raw_url)) if raw_url else base_url

        # 2. Company Name
        comp_el = card.select_one(".job-company") or card.select_one(".company") or card.select_one(".org")
        company_name = comp_el.get_text(strip=True) if comp_el else ""

        # 3. Location
        loc_el = card.select_one(".job-location") or card.select_one(".location")
        location = loc_el.get_text(strip=True) if loc_el else "Unspecified"

        # 4. Salary / Compensation
        sal_el = card.select_one(".job-salary") or card.select_one(".salary") or card.select_one(".compensation")
        salary_raw = sal_el.get_text(strip=True) if sal_el else "Unspecified"

        # 5. Category / Badge
        cat_el = card.select_one(".job-badge") or card.select_one(".category") or card.select_one(".tag")
        category = cat_el.get_text(strip=True) if cat_el else "General"

        # 6. Employment Type
        type_el = card.select_one(".job-type") or card.select_one(".employment-type")
        employment_type = type_el.get_text(strip=True) if type_el else "Full-time"

        # 7. Posted Date
        date_el = card.select_one(".job-date") or card.select_one("time") or card.select_one(".date")
        posted_date_raw = ""
        if date_el:
            posted_date_raw = date_el.get("datetime") or date_el.get_text(strip=True)
        else:
            posted_date_raw = datetime.date.today().isoformat()

        # 8. Extraction Timestamp
        extraction_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {
            "job_title": job_title,
            "company_name": company_name,
            "salary_raw": salary_raw,
            "location": location,
            "category": category,
            "employment_type": employment_type,
            "posted_date_raw": str(posted_date_raw),
            "source_url": source_url,
            "extraction_timestamp": extraction_timestamp,
        }

    def _extract_next_page(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Find the next page URL through CSS class, rel attribute, or link text."""
        # Check explicit class .pagination-next
        next_tag = soup.select_one(".pagination-next") or soup.select_one("a[rel='next']")
        
        # Check for anchor with text containing 'Next'
        if not next_tag:
            for a in soup.select("a"):
                text = a.get_text(strip=True).lower()
                if "next" in text and ">" in text or text == "next":
                    next_tag = a
                    break

        if next_tag and next_tag.get("href"):
            href = str(next_tag.get("href"))
            # Avoid disabled links
            if "disabled" in next_tag.get("class", []):
                return None
            return urljoin(base_url, href)

        return None
