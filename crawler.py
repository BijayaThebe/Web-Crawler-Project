
import os
import re
import time
import json
import logging
import requests
from urllib.parse import urljoin, urldefrag, urlparse
from bs4 import BeautifulSoup
from collections import deque
from datetime import datetime
from pathlib import Path

# ---------------- CONFIGURATION ---------------- #

# Input seed file (list of websites to crawl)
INPUT_SEEDS_PATH = r"C:\Users\BijayaThebe\Downloads\Web Craweler Python Automation Project\seeds.txt"
# Output folder setup
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Subfolder to store Markdown pages
MD_DIR = OUTPUT_DIR / "MDs"
MD_DIR.mkdir(exist_ok=True)

# Crawler behavior
MAX_DEPTH = 1          # How deep to crawl links (0 = only seed page)
REQUEST_TIMEOUT = 10   # Seconds before giving up on a request
RETRY_COUNT = 3        # How many times to retry a failed request
POLITE_DELAY = 0.5     # Seconds to wait between requests

# Domains we allow crawling
ALLOWED_DOMAINS = [
    "jeevee.com",
    "tranquilityspa.com",
    "tranquilityspa.com.np",
    "kiec.edu.np",
    "prettyclickcosmetics.com",
]
ALLOWED_DOMAINS = [d.lower().strip() for d in ALLOWED_DOMAINS]

# Domains we want to block (social media, streaming, etc.)
BLOCKED_DOMAINS = [
    "facebook.com", "tiktok.com", "youtube.com", "twitter.com", "instagram.com",
    "linkedin.com", "pinterest.com", "reddit.com", "quora.com", "whatsapp.com",
    "snapchat.com", "x.com", "netflix.com", "spotify.com"
]
BLOCKED_DOMAINS = [d.lower().strip() for d in BLOCKED_DOMAINS]

# Patterns we don’t want (files, trackers, tel/mailto links, etc.)
BLOCK_PATTERNS = [
    r"\.(jpg|jpeg|png|gif|svg|webp|pdf|zip|mp4|avi|mov|mp3|wav)$",  # media/files
    r"/wp-json/",     # WP JSON API
    r"^tel:",         # phone links
    r"^mailto:",      # email links
    r"^javascript:",  # inline JS
    r"\?utm_",        # tracking params
    r"#",             # fragment-only links
]

# ---------------- LOGGING SETUP ---------------- #
LOG_FILE = OUTPUT_DIR / "crawlLog.txt"
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# File paths for results
FAILED_URLS_FILE = OUTPUT_DIR / "failed_urls.txt"
SUCCESS_URLS_FILE = OUTPUT_DIR / "success_urls.txt"
INDEX_JSON_FILE = OUTPUT_DIR / "index.json"  # final metadata file

# ---------------- HELPER FUNCTIONS ---------------- #

def normalize_hostname(hostname: str) -> str:
    """Convert hostname to lowercase and remove leading www."""
    hostname = hostname.lower().strip()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname

def is_allowed_url(url: str) -> bool:
    """Check if a URL should be crawled based on allowed/blocked domains."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = normalize_hostname(parsed.netloc)

        # Check blocked domains
        if any(hostname == b or hostname.endswith("." + b) for b in BLOCKED_DOMAINS):
            return False

        # Check allowed domains
        if any(hostname == a or hostname.endswith("." + a) for a in ALLOWED_DOMAINS):
            return True

        return False
    except Exception as e:
        logging.warning(f"Error checking URL {url}: {e}")
        return False

def normalize_url(base: str, link: str) -> str | None:
    """Resolve relative links into full absolute URLs and strip fragments (#)."""
    try:
        joined = urljoin(base, link)       # resolve relative paths
        clean_url, _ = urldefrag(joined)   # remove #fragment
        parsed = urlparse(clean_url)
        if parsed.scheme not in ("http", "https"):
            return None
        return clean_url.strip()
    except Exception as e:
        logging.warning(f"Failed to normalize URL {link} from {base}: {e}")
        return None

def fetch_url(url: str):
    """Try to fetch a URL with retries (handles slow or unstable sites)."""
    for attempt in range(RETRY_COUNT):
        try:
            return requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
        except Exception as e:
            logging.warning(f"Retry {attempt+1}/{RETRY_COUNT} for {url} failed: {e}")
            time.sleep(1)
    return None

def extract_title(soup: BeautifulSoup) -> str:
    """Extract a meaningful title (title tag → h1 → h2 → fallback)."""
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    for tag in ["h1", "h2"]:
        found = soup.find(tag)
        if found:
            return found.get_text(strip=True)
    return "Untitled Page"

def extract_clean_markdown(html_content: str) -> str:
    """Convert HTML into clean, readable Markdown."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove noise tags
    for tag in soup(["script", "style", "nav", "aside", "footer", "header", "iframe", "noscript"]):
        tag.decompose()

    lines = []
    for el in soup.find_all(['h1','h2','h3','h4','h5','h6','p','li','blockquote']):
        text = el.get_text(strip=True)
        if not text:
            continue
        if el.name.startswith("h"):
            level = int(el.name[1])
            lines.append(f"{'#' * level} {text}")
        elif el.name == "li":
            lines.append(f"- {text}")
        elif el.name == "blockquote":
            lines.append(f"> {text}")
        else:
            lines.append(text)
    return "\n\n".join(lines)

def generate_filename_from_url(url: str) -> str:
    """Create a safe filename based on URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "index"
    domain = parsed.netloc.replace("www.", "").replace(".", "_")
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", f"{domain}_{path}")[:150]
    return safe_name + ".md"

# ---------------- MAIN CRAWLER ---------------- #

def crawl(seed: str, all_results: list):
    """Crawl a single seed URL up to MAX_DEPTH and save results."""
    visited = set()
    queue = deque([(seed.strip(), 0, None)])  # (url, depth, parent)
    stats = {"processed": 0, "failed": 0, "blocked": 0, "saved": 0}

    while queue:
        raw_url, depth, parent = queue.popleft()
        url = raw_url.strip()

        if url in visited or depth > MAX_DEPTH:
            continue
        visited.add(url)

        # Check if URL is allowed
        if not is_allowed_url(url):
            stats["blocked"] += 1
            continue

        logging.info(f"Processing: {url} (depth={depth})")

        # Fetch page
        response = fetch_url(url)
        if not response:
            stats["failed"] += 1
            with open(FAILED_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{url}|error:unreachable|{datetime.now().isoformat()}\n")
            continue

        status = response.status_code
        content_type = response.headers.get("Content-Type", "").lower()
        html_content = response.text if "text/html" in content_type else ""

        # Extract title
        title, soup = "", None
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            title = extract_title(soup)

        # Save Markdown
        file_path = None
        if html_content:
            md = extract_clean_markdown(html_content)
            filename = generate_filename_from_url(url)
            file_path = MD_DIR / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md)
            stats["saved"] += 1

        # Build metadata entry
        entry = {
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "status_code": status,
            "file_path": str(file_path) if file_path else None,
            "depth": depth
        }
        all_results.append(entry)

        # Log success
        if status == 200 and file_path:
            with open(SUCCESS_URLS_FILE, "a", encoding="utf-8") as f:
                f.write(url + "\n")

        # Extract links for next depth
        if html_content and depth < MAX_DEPTH:
            for a in soup.find_all("a", href=True):
                norm_url = normalize_url(url, a["href"])
                if not norm_url or norm_url in visited:
                    continue
                if is_allowed_url(norm_url):
                    queue.append((norm_url, depth + 1, url))
                else:
                    stats["blocked"] += 1

        # Be polite
        time.sleep(POLITE_DELAY)
        stats["processed"] += 1

    logging.info(f"Finished crawling {seed}. Stats: {stats}")
    print(f"[✓] {seed} → {stats['processed']} pages (Saved: {stats['saved']})")
    return stats

# ---------------- RUNNER ---------------- #

if __name__ == "__main__":
    # Reset logs
    open(FAILED_URLS_FILE, "w").close()
    open(SUCCESS_URLS_FILE, "w").close()

    # Load seeds
    if not os.path.exists(INPUT_SEEDS_PATH):
        print(f"❌ Seed file not found: {INPUT_SEEDS_PATH}")
        exit(1)

    with open(INPUT_SEEDS_PATH, "r", encoding="utf-8") as f:
        seeds = [line.strip() for line in f if line.strip()]

    if not seeds:
        print("❌ No seeds found.")
        exit(1)

    # Start crawl
    print(f"🚀 Starting crawl with {len(seeds)} seeds...")
    all_metadata, global_stats = [], {"processed": 0, "failed": 0, "blocked": 0, "saved": 0}

    for i, seed in enumerate(seeds, start=1):
        if not seed.startswith(("http://", "https://")):
            seed = "https://" + seed
        print(f"\n🌱 Crawling seed {i}: {seed}")
        seed_stats = crawl(seed, all_metadata)
        for k in global_stats:
            global_stats[k] += seed_stats[k]

    # Save metadata
    with open(INDEX_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "="*60)
    print("✅ CRAWL COMPLETED")
    print("="*60)
    print(f"📄 Pages Saved: {global_stats['saved']}")
    print(f"📂 Metadata: {INDEX_JSON_FILE}")
    print(f"📝 Markdowns: {MD_DIR}")
    print("="*60)
    print("\n🎉 Done! All results saved in pretty JSON + Markdown format.")
