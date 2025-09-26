# 🕷️ Web Crawler & Content Archiver

A focused, ethical web crawler that extracts clean, readable content from specified domains and saves structured metadata in JSON format along with human-readable Markdown files.

---

## 📌 Introduction

This Python-based web crawler is designed to:
- Crawl websites **only within allowed domains** (e.g., `jeevee.com`, `kiec.edu.np`)
- Respect depth limits and avoid external/social media links
- Convert HTML pages into **clean, readable Markdown**
- Generate a **structured JSON index** with full metadata for every crawled page
- Log successes, failures, and activity for auditability

Ideal for **content archiving, documentation, research, or compliance** use cases where clean, structured data extraction from trusted domains is required.

---

## 🛠️ Tools and Technologies Used

| Component | Technology |
|---------|------------|
| **Language** | Python 3.8+ |
| **HTTP Client** | `requests` |
| **HTML Parsing** | `BeautifulSoup4` |
| **URL Handling** | `urllib.parse` |
| **Data Structure** | `collections.deque` (BFS queue) |
| **File I/O** | Built-in `pathlib`, `json`, `re` |
| **Logging** | `logging` module |
| **Output Format** | JSON (metadata), Markdown (content) |

---

## 🏗️ Project Architecture

The system follows a **breadth-first crawl** strategy with configurable depth, domain whitelisting, and content sanitization.
```mermaid
flowchart TD
    A[Project Root] --> B[.web_crawler/]
    A --> C[outputs/]
    A --> D[seeds.txt]
    A --> E[requirements.txt]
    A --> F[README.md]
    A --> R[crawler.py]
    B --> G[Include/]
    B --> H[Lib/]
    B --> I[Scripts/]
    B --> J[.gitignore]
    B --> K[pyvenv.cfg]
    C --> L[MDs/]
    C --> M[crawlLog.txt]
    C --> N[failed_urls.txt]
    C --> O[index.json]
    C --> P[success_urls.txt]
    D --> Q[Seed URLs]

    style A fill:#f9f,stroke:#333
    style B fill:#ccf,stroke:#333
    style C fill:#cfc,stroke:#333
    style D fill:#ffc,stroke:#333
    style E fill:#fcc,stroke:#333
    style F fill:#cff,stroke:#333
    style R fill:#eef,stroke:#333
  
```

---

## 🔄 Program Execution Flowchart
```mermaid
flowchart TD
    A([Start]) --> B{Read seeds.txt}
    B -->|File missing| C([Exit with error])
    B -->|Valid seeds| D[Initialize output directories and files]
    D --> E[For each seed URL]
    E --> F[Normalize to https:// if needed]
    F --> G[Initialize BFS queue]
    G --> H{Queue not empty?}
    H -->|No| I[Next seed]
    H -->|Yes| J[Dequeue URL]
    J --> K{URL visited or depth > MAX_DEPTH?}
    K -->|Yes| H
    K -->|No| L[Mark URL as visited]
    L --> M{URL in allowed domains?}
    M -->|No| N[Increment blocked count]
    N --> H
    M -->|Yes| O[Fetch URL with retries]
    O -->|Fail| P[Log to failed_urls.txt]
    P --> H
    O -->|Success| Q[Parse HTML with BeautifulSoup]
    Q --> R[Extract clean title]
    R --> S[Convert HTML to clean Markdown]
    S --> T[Save .md file in /MDs/]
    T --> U[Append metadata to global list]
    U --> V[Log to success_urls.txt]
    V --> W{Depth < MAX_DEPTH?}
    W -->|No| H
    W -->|Yes| X[Extract all <a href> links]
    X --> Y[Normalize and validate each link]
    Y --> Z{Link allowed and not visited?}
    Z -->|Yes| AA[Enqueue link with depth+1]
    AA --> H
    Z -->|No| AB[Increment blocked count]
    AB --> H
    I --> AC[Save all_metadata to index.json]
    AC --> AD[Print summary statistics]
    AD --> AE([End])

    %% Color styles
    style A fill:#FFD700,stroke:#333,stroke-width:2px
    style B fill:#87CEFA,stroke:#333,stroke-width:2px
    style C fill:#FF6347,stroke:#333,stroke-width:2px
    style D fill:#FFDEAD,stroke:#333,stroke-width:2px
    style E fill:#FFA07A,stroke:#333,stroke-width:2px
    style F fill:#7FFFD4,stroke:#333,stroke-width:2px
    style G fill:#D8BFD8,stroke:#333,stroke-width:2px
    style H fill:#E6E6FA,stroke:#333,stroke-width:2px
    style I fill:#98FB98,stroke:#333,stroke-width:2px
    style J fill:#AFEEEE,stroke:#333,stroke-width:2px
    style K fill:#F0E68C,stroke:#333,stroke-width:2px
    style L fill:#FFDAB9,stroke:#333,stroke-width:2px
    style M fill:#ADD8E6,stroke:#333,stroke-width:2px
    style N fill:#F08080,stroke:#333,stroke-width:2px
    style O fill:#90EE90,stroke:#333,stroke-width:2px
    style P fill:#FA8072,stroke:#333,stroke-width:2px
    style Q fill:#FFE4B5,stroke:#333,stroke-width:2px
    style R fill:#E0FFFF,stroke:#333,stroke-width:2px
    style S fill:#FFFACD,stroke:#333,stroke-width:2px
    style T fill:#FFD700,stroke:#333,stroke-width:2px
    style U fill:#ADFF2F,stroke:#333,stroke-width:2px
    style V fill:#7CFC00,stroke:#333,stroke-width:2px
    style W fill:#87CEEB,stroke:#333,stroke-width:2px
    style X fill:#DDA0DD,stroke:#333,stroke-width:2px
    style Y fill:#F5DEB3,stroke:#333,stroke-width:2px
    style Z fill:#FFB6C1,stroke:#333,stroke-width:2px
    style AA fill:#98FB98,stroke:#333,stroke-width:2px
    style AB fill:#FA8072,stroke:#333,stroke-width:2px
    style AC fill:#B0E0E6,stroke:#333,stroke-width:2px
    style AD fill:#EEE8AA,stroke:#333,stroke-width:2px
    style AE fill:#32CD32,stroke:#333,stroke-width:3px

```

---
## 🚀 Getting Started [Run Program File]

Follow the steps below to set up and run the project on your local machine.

---

### 1. Clone the Repository
```bash
git clone <REPOSITORY_URL>
cd <PROJECT_FOLDER>

```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

Windows (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```
Windows (CMD):
```bash
.venv\Scripts\activate.bat
```
Linux / macOS:
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Crawler
```bash
python Crawler.py
```

## ⚙️ Configuration & Hyperparameters

You can control the crawler behavior by modifying variables inside **`Crawler.py`** (or through a separate config file if available).  
Below are the main parameters you can tune:

| Parameter         | Description                                                                 | Default Value |
|-------------------|-----------------------------------------------------------------------------|---------------|
| `MAX_DEPTH`       | Maximum depth to crawl (how many link levels from the seed).                | 3             |
| `REQUEST_TIMEOUT` | Timeout for each request in seconds.                                        | 10            |
| `POLITE_DELAY`    | Delay (in seconds) between requests to avoid overloading servers.           | 1             |
| `USER_AGENT`      | User-Agent string to use in requests.                                       | Custom crawler|
| `OUTPUT_DIR`      | Folder where results will be saved.                                         | `output/`     |
| `SEEDS_PATH`      | Path to the seeds file containing initial URLs.                             | `seeds.txt`   |

---

### 🔧 Setting up the Hyper Parameters

The crawler can be controlled by adjusting hyperparameters. These define how deep, fast, and broad the crawler runs.

---

1. Open **`Crawler.py`** (or `config.py` if exists).
2. Locate the **CONFIGURATION section** at the top of the file.
3. Change the parameter values as needed.  

Example:
```python
# ---- CONFIGURATION ----
MAX_DEPTH = 1         
REQUEST_TIMEOUT = 10  
RETRY_COUNT = 3        
POLITE_DELAY = 0.5    
```

<img width="866" height="194" alt="image" src="https://github.com/user-attachments/assets/da121610-c2ea-4c87-b6d8-50fbfe3a7be6" />

4. Set your Allowed_Domain
    <img width="1054" height="238" alt="image" src="https://github.com/user-attachments/assets/a447154d-bdf5-4703-97e3-6d34d70d8ff3" />

5. Set your Blocked Domain
    <img width="1246" height="183" alt="image" src="https://github.com/user-attachments/assets/e6d8152e-7464-4a9d-b149-bbb7496e8347" />
    
6. Set your Blocked Regex Parameter
   <img width="1226" height="308" alt="image" src="https://github.com/user-attachments/assets/1650d3fb-3db4-4297-b788-1f6ba2cb5d63" />




### 🎯 Example Run with Modified Params
```bash
python Crawler.py --max_pages 50 --depth 2
```

## 📂 Output
All results generated by the crawler will be saved in the `output/` directory. 
Here are the samples of the output section
    <img width="1709" height="314" alt="image" src="https://github.com/user-attachments/assets/eb77e95e-bb3d-4470-863d-bebb39fa83b0" />
    <img width="1584" height="319" alt="image" src="https://github.com/user-attachments/assets/f1ab5639-0123-4870-88cc-5e884e50271c" />
    <img width="1380" height="809" alt="image" src="https://github.com/user-attachments/assets/74222333-40ea-4a88-8222-413b7c540f94" />
    <img width="1612" height="319" alt="image" src="https://github.com/user-attachments/assets/ba2399c4-74bf-43ef-a47c-520b66dd47b5" />





## 🙌 Conclusion

This project gives you a flexible and easy-to-use web crawler that you can tune to your own needs.  
By adjusting the hyperparameters, you can decide how deep, how fast, and how broad the crawler should go.  

Start small, experiment with the settings, and scale up as you get more comfortable.  
With just a few tweaks, you’ll have a crawler that works perfectly for your use case. 🚀  






