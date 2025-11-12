import scrapy
from ..schema import Book

class BookSpider(scrapy.Spider):
    """
    A Scrapy spider designed to crawl the 'books.toscrape.com' website.

    This spider performs the following actions:
    1. Starts on the main page.
    2. Navigates through each book category's pagination.
    3. Follows the link to each individual book's detail page.
    4. Scrapes the required data from the detail page.
    5. Yields a Pydantic `Book` object for each book to be processed by the pipeline.
    """
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response, **kwargs):
        """
        Parses category or main pages, follows links to book detail pages,
        and handles pagination for the current page.

        Args:
            response: The Scrapy Response object for the current page.
        """
        # Find all book links on the current page and schedule them to be parsed.
        for book_link in response.css("article.product_pod h3 > a::attr(href)").getall():
            yield response.follow(book_link, callback=self.parse_book_details)

        # Find the 'next' page button and, if it exists, follow it to continue crawling.
        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response, **kwargs):
        """
        Parses the book detail page to extract all required data fields.

        This method constructs a Pydantic `Book` item from the scraped data
        and yields it for the item pipeline to process.

        Args:
            response: The Scrapy Response object for the book detail page.
        """
        try:
            # A helper function to robustly extract data from the product information table.
            def get_table_value(key: str) -> str:
                """Finds a key in the product table and returns its corresponding value."""
                return response.xpath(f"//th[text()='{key}']/following-sibling::td/text()").get()

            # Create a dictionary with all the scraped data.
            # This dictionary will be used to instantiate the Pydantic `Book` model.
            book_data = {
                "url": response.url,
                "_id": Book.compute_id(response.url),
                "title": response.css("div.product_main h1::text").get(),
                "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
                "category": response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get(),
                "price_incl_tax": get_table_value("Price (incl. tax)"),
                "price_excl_tax": get_table_value("Price (excl. tax)"),
                "availability": get_table_value("Availability"),
                "reviews": int(get_table_value("Number of reviews") or 0),
                "image_url": response.urljoin(response.css("div.item.active > img::attr(src)").get()),
                "rating": response.css("p.star-rating::attr(class)").get().replace("star-rating ", ""),
                "raw_html": response.body.decode('utf-8'),
            }
            
            # Yield a validated Book object for the pipeline.
            yield Book(**book_data)

        except Exception as e:
            self.logger.error(
                f"Failed to parse book details for URL {response.url}: {e}", 
                exc_info=True
            )
