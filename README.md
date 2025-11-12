# Book Crawler & Change Detector

This Scrapy project is a robust web crawler designed to scrape book data from the [books.toscrape.com](http://books.toscrape.com) sandbox website. It stores the data in MongoDB, intelligently detects changes between crawls, and provides reporting on all new and updated book information.

## Features

-   **Asynchronous Crawling**: Built on Scrapy and `motor` for high-performance, non-blocking network requests.
-   **Data Validation**: Uses Pydantic models to ensure data integrity and structure before processing.
-   **MongoDB Integration**: Stores all scraped data in a MongoDB database.
-   **Change Detection & Logging**:
    -   Automatically detects newly added books.
    -   Monitors key fields (price, availability, rating) and logs any updates to existing books.
    -   Maintains a comprehensive `changelog` collection for a full audit trail of all changes.
-   **Data Archiving**: Saves a raw HTML snapshot of each book page to a separate collection for archival and fallback purposes.
-   **Resumable Crawls**: Crawls can be stopped and resumed, picking up right where they left off, which is ideal for long-running jobs.
-   **Daily Reporting**: Includes a standalone script to generate a daily report of all detected changes in either JSON or CSV format.

## Project Structure

```
.
├── books/
│   ├── books/
│   │   ├── __init__.py
│   │   ├── pipelines.py      # Handles data processing, change detection, and storage.
│   │   ├── schema.py         # Contains Pydantic models for data validation.
│   │   ├── settings.py       # Scrapy project settings.
│   │   └── spiders/
│   │       └── book.py       # The main spider for crawling the website.
│   └── scrapy.cfg            # Scrapy project configuration file.
├── reporting.py              # Standalone script for generating daily change reports.
├── requirements.txt          # Project dependencies.
└── README.md                 # This file.
```

## Setup Instructions

### Prerequisites

-   Python 3.13+
-   A running MongoDB instance.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/umarndungo/web_crawling_test.git
    cd web_crawling_test
    ```

2.  **Create and activate a virtual environment:**
    *   On Linux/macOS:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the database (optional):**
    The MongoDB connection settings are located in `books/books/settings.py`. The default values are:
    ```python
    MONGO_URI = "mongodb://127.0.0.1:27017"
    MONGO_DATABASE = "books_db"
    ```
    Update these if your MongoDB instance is running on a different host or port.

## How to Use

### Running the Crawler

To start the crawl, navigate to the `books` directory and run the `book` spider.

```bash
cd books
scrapy crawl book
```
The spider will begin crawling, and you will see log messages in your console as it processes pages and saves data.

### Generating a Change Report

After the crawler has run, you can generate a report of all changes detected in the last 24 hours.

1.  Navigate to the project's root directory (`web_crawling_test`).
2.  Run the `reporting.py` script.

    *   **To generate a JSON report (default):**
        ```bash
        python reporting.py
        ```
        This will create a `daily_report.json` file.

    *   **To generate a CSV report:**
        ```bash
        python reporting.py --format csv
        ```
        This will create a `daily_report.csv` file.

### Automating the Report

You can schedule the reporting script to run automatically using a system scheduler.

**Example (Linux/macOS using `cron`):**

Run `crontab -e` and add the following line to generate a CSV report every day at 2:00 AM. Make sure to use the absolute path to your virtual environment's Python interpreter and the script.

```
0 2 * * * /path/to/your/project/venv/bin/python /path/to/your/project/reporting.py --format csv
```

## Dependencies

This project uses Python 3.13. The main dependencies are listed in `requirements.txt` and include:

-   Scrapy
-   Pydantic
-   motor (Asynchronous MongoDB driver)
-   pymongo