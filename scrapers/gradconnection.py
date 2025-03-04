from utils import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

DOMAIN = "https://au.gradconnection.com"
DEFAULT_URL = "https://au.gradconnection.com/graduate-jobs/computer-science/australia/"
PAGE_QUERY = "?page="
PAGE_START = 1
PAGE_END = 100

def scrape_job_urls(html):
    """Get job description links."""
    soup = parse_html(html)
    job_title_links = soup.select(".box_container .box-header .box-header-title")
    urls = [DOMAIN + link["href"] for link in job_title_links]
    return urls

def scrape_job_details(url):
    """Get job details from detail page."""

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    # Expand details
    try:
        show_more_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-show-link")
        for link in show_more_buttons:
            link.click()
    except:
        # Some pages simply don't have a show more button
        pass

    # Expand AI job summary
    try:
        ai_job_summary_read_more_buttons = driver.find_element(By.CSS_SELECTOR, ".ai-summary_scroll-overlay-campaign p")
        ai_job_summary_read_more_buttons.click()
    except:
        # Some pages simply don't have an AI job summary
        pass

    html = driver.page_source
    driver.quit()

    soup = parse_html(html)

    # Get job details
    employer_title = soup.select_one(".employers-panel .employers-panel-title").get_text(strip=True)
    job_title = soup.select_one(".employers-profile-hgroup .employers-profile-h1").get_text(strip=True)
    job_description = soup.select_one(".campaign-content-container").get_text(strip=True)

    job_type = None
    diciplines = None
    work_rights = None
    locations = None
    start_date = None
    end_date = None

    application_detail_categories = soup.select(".box-content-catagories")
    for category in application_detail_categories:
        category_title_element = category.select_one(".box-content-catagories-bold")
        category_title = category_title_element.get_text(strip=True).lower()
        if "job type" in category_title:
            category_title_element.decompose()
            job_type = category.get_text(strip=True)
        elif "disciplines" in category_title:
            diciplines = category.select_one(".ellipsis-text-paragraph").get_text(strip=True)
        elif "work rights" in category_title:
            work_rights = category.select_one(".ellipsis-text-paragraph").get_text(strip=True)
        elif "locations" in category_title:
            locations = category.select_one(".ellipsis-text-paragraph").get_text(strip=True)
        elif "start date" in category_title:
            start_date = category.select_one(".ellipsis-text-paragraph").get_text(strip=True)
        elif "closing date" in category_title:
            category_title_element.decompose()
            end_date = category.get_text(strip=True)

    # Get AI job summary
    try:
        ai_job_summary_element = soup.select_one(".ai-summary_campaign-summary-container.ai-summary_campaign-summary-expanded")
        
        # Remove feedback section from AI job summary
        ai_job_summary_feedback = ai_job_summary_element.select_one(".ai-summary_user-rating-container")
        if ai_job_summary_feedback:
            ai_job_summary_feedback.decompose()

        # Remove overlay campaign from AI job summary
        ai_job_overlay_campign = ai_job_summary_element.select_one(".ai-summary_scroll-overlay-campaign")
        if ai_job_overlay_campign:
            ai_job_overlay_campign.decompose()

        ai_job_summary = ai_job_summary_element.get_text(strip=True)
    except:
        ai_job_summary = None

    return {
        "url": url,
        "employer_title": employer_title,
        "job_title": job_title,
        "job_description": job_description,
        "ai_job_summary": ai_job_summary,
        "job_type": job_type,
        "diciplines": diciplines,
        "work_rights": work_rights,
        "locations": locations,
        "start_date": start_date,
        "end_date": end_date
    }

def get_paginated_job_urls():
    """Get all job links from paginated pages."""

    # Set base URL and headers
    base_url = input("Paste GradConnection URL or press return for default: ") or DEFAULT_URL 
    headers = {"User-Agent": "Mozilla/5.0"}

    # Store failed URLs
    failed_urls = []
    csv_headers = ["page", "url"]
    job_urls = set()

    # Get job URLs from paginated pages
    for page_number in range(PAGE_START, PAGE_END + 1):
        # Build URL
        url = base_url if page_number == 1 else base_url + PAGE_QUERY + str(page_number)

        print(f"Scraping page {page_number}, URL = {url}")

        html = fetch_html(url, headers)

        if html is None:
            save_to_csv("gradconnection-job-urls-failed", "a+", csv_headers, [[page_number, url]])
        else:
            new_urls = scrape_job_urls(html)

            # Add new URLs to set
            job_urls |= set(new_urls)

            # Append new URLs to CSV
            save_to_csv("gradconnection-job-urls", "a+", csv_headers, [[page_number, url] for url in new_urls])

    return job_urls

def get_job_details(job_urls):
    """Get job descriptions."""

    job_details = []
    job_count = len(job_urls)
    for index, url in enumerate(job_urls):
        try:
            print(f"Fetching job details ({index + 1}/{job_count}), URL = {url}")
            details = scrape_job_details(url)
            job_details.append(details)

            # Save to CSV every nth job
            if index % 1 == 0:
                csv_headers = job_details[0].keys()
                save_to_csv("gradconnection-job-details", "a+", csv_headers, [job.values() for job in job_details])
        except Exception as ex:
            print(f"Failed to scrape {url}. {ex}")
            csv_headers = ["url", "exception"]
            save_to_csv("gradconnection-job-details-failed", "a+", csv_headers, [[url, ex]])

def main():
   # Ask user if they want to clear previously saved job URLs
    while True:
        clear_saved_urls = input("Do you want to clear previously saved job URLs? (y/n): ").lower()
        if clear_saved_urls == "y":
            clear_file("gradconnection-job-urls")
            clear_file("gradconnection-job-urls-failed")
            clear_file("gradconnection-job-details")
            clear_file("gradconnection-job-details-failed")
            break
        elif clear_saved_urls == "n":
            create_file("gradconnection-job-urls")
            create_file("gradconnection-job-urls-failed")
            create_file("gradconnection-job-details")
            create_file("gradconnection-job-details-failed")
            break

    job_urls = get_paginated_job_urls()

    # Load previously saved job URLs
    # job_urls_data = read_csv("gradconnection-job-urls")
    # job_urls = [row[1] for row in job_urls_data[1:]]

    get_job_details(job_urls)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Scraping operation cancelled.")