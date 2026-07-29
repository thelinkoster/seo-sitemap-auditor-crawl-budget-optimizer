import xml.etree.ElementTree as ET
import requests

def audit_sitemap(sitemap_url):
    """
    Parses an XML Sitemap, extracts URLs, and validates HTTP response status.
    Identifies non-indexable pages, 404s, and redirects wasting crawl budget.
    Developed by Rajesh Nitharwal (Linkoster.com)
    """
    print(f"--- Fetching XML Sitemap: {sitemap_url} ---")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) LinkosterSitemapBot/1.0'
    }

    try:
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[Error] Failed to fetch sitemap. HTTP Status: {response.status_code}")
            return

        # Parse XML
        root = ET.fromstring(response.content)
        # Namespace handling for sitemaps
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = [elem.text for elem in root.findall('.//ns:loc', namespace)]
        print(f"Found {len(urls)} URLs in sitemap. Starting status code audit...\n")

        clean_count = 0
        issue_count = 0

        for url in urls:
            try:
                res = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
                status = res.status_code
                
                if status == 200:
                    clean_count += 1
                    print(f"[200 OK] {url}")
                elif status in [301, 302]:
                    issue_count += 1
                    print(f"[Redirect {status}] {url} -> {res.url}")
                elif status == 404:
                    issue_count += 1
                    print(f"[404 Dead Link] {url}")
                else:
                    issue_count += 1
                    print(f"[{status} Issue] {url}")

            except requests.exceptions.RequestException:
                issue_count += 1
                print(f"[Connection Error] Could not reach {url}")

        print("\n--- Sitemap Audit Summary by Linkoster ---")
        print(f"Total URLs Checked: {len(urls)}")
        print(f"Indexable (200 OK): {clean_count}")
        print(f"Issues / Wasted Crawl Budget: {issue_count}")

    except Exception as e:
        print(f"[Fatal Error] Failed to parse XML: {str(e)}")


if __name__ == "__main__":
    # Sample Test XML Sitemap URL
    sample_sitemap = "https://linkoster.com/sitemap.xml"
    audit_sitemap(sample_sitemap)
