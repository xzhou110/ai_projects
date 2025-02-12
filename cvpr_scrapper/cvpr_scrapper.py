import requests
from bs4 import BeautifulSoup
import time
import csv
from pathlib import Path
import logging
from typing import Optional, Tuple, Dict, Any, List

# Configure logging to display timestamps and log levels.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

BASE_URL = "https://openaccess.thecvf.com"
MAIN_URL = "https://openaccess.thecvf.com/CVPR2024?day=all"
MAX_PAPERS = 20         # Limit for demo purposes.
DELAY_SECONDS = 3       # Delay between requests to be polite.


def build_full_url(relative_link: str) -> str:
    """
    Build a full URL given a relative link.
    """
    if relative_link.startswith('/'):
        return BASE_URL + relative_link
    return relative_link


def scrape_paper_details(paper_url: str) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    """
    Given a paper detail page URL, extract the abstract, PDF link, and supplemental link.
    
    Returns:
        A tuple (abstract, pdf_link, supp_link) if successful; otherwise, None.
    """
    try:
        response = requests.get(paper_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {paper_url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the abstract (it might be in a <div> with id or class "abstract")
    abstract_div = soup.find('div', id='abstract') or soup.find('div', class_='abstract')
    abstract = abstract_div.get_text(strip=True) if abstract_div else ""

    # Extract PDF and supplementary links.
    pdf_link = None
    supp_link = None
    for a in soup.find_all('a'):
        link_text = a.get_text(strip=True).lower()
        href = a.get('href')
        if not href:
            continue
        if "pdf" in link_text and not pdf_link:
            pdf_link = build_full_url(href)
        elif ("supp" in link_text or "supplement" in link_text) and not supp_link:
            supp_link = build_full_url(href)

    return abstract, pdf_link, supp_link


def scrape_papers(main_url: str, max_papers: int = MAX_PAPERS) -> List[Dict[str, Any]]:
    """
    Scrape the main CVPR 2024 page for paper entries and return a list of paper data dictionaries.
    
    Args:
        main_url: URL of the main conference page.
        max_papers: Maximum number of papers to scrape.
    
    Returns:
        A list of dictionaries, each containing data for one paper.
    """
    try:
        response = requests.get(main_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching the main CVPR 2024 page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    paper_entries = soup.find_all('dt', class_='ptitle')
    if not paper_entries:
        logging.error("No paper entries found. Please check the page structure.")
        return []

    papers_data = []
    for count, entry in enumerate(paper_entries):
        if count >= max_papers:
            break

        a_tag = entry.find('a')
        if not a_tag:
            continue

        title = a_tag.get_text(strip=True)
        paper_relative_link = a_tag.get('href')
        if not paper_relative_link:
            continue
        paper_url = build_full_url(paper_relative_link)

        # Extract authors from the corresponding <dd> tag (usually the next sibling).
        dd_authors = entry.find_next_sibling('dd')
        authors = dd_authors.get_text(strip=True) if dd_authors else ""

        logging.info(f"Scraping paper: {title}")
        time.sleep(DELAY_SECONDS)

        details = scrape_paper_details(paper_url)
        if details is None:
            continue
        abstract, pdf_link, supp_link = details

        paper_info = {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'paper_url': paper_url,
            'pdf_link': pdf_link,
            'supplemental_link': supp_link
        }
        papers_data.append(paper_info)

    return papers_data


def save_to_csv(data: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Save the list of paper data dictionaries to a CSV file.
    
    Args:
        data: List of dictionaries containing paper information.
        output_path: Path to the output CSV file.
    """
    fieldnames = ['title', 'authors', 'abstract', 'paper_url', 'pdf_link', 'supplemental_link']
    try:
        with output_path.open('w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Data successfully saved to {output_path}")
    except IOError as e:
        logging.error(f"Error writing CSV file: {e}")


def main():
    logging.info("Starting the CVPR 2024 scraping process.")
    papers_data = scrape_papers(MAIN_URL)
    if not papers_data:
        logging.error("No paper data scraped; exiting.")
        return

    # Ensure the CSV is saved to the same folder as this script.
    output_file = Path(__file__).parent / "cvpr2024_papers.csv"
    save_to_csv(papers_data, output_file)
    logging.info("Scraping complete.")


if __name__ == "__main__":
    main()

