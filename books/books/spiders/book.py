import scrapy
from ..schema import Book

class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        """
        This function parses the main page, extracts links to individual book pages,
        and follows them. It also handles pagination.
        """
        # Follow links to individual book pages
        for book_link in response.css("article.product_pod h3 > a::attr(href)").getall():
            yield response.follow(book_link, callback=self.parse_book_details)

        # Follow pagination link
        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):
        """
        This function parses the book detail page, extracts all the required data,
        and yields a Pydantic `Book` object.
        """
        try:
            # Helper for extracting table data
            def get_table_value(key: str) -> str:
                return response.xpath(f"//th[text()='{key}']/following-sibling::td/text()").get()

            # Construct the Pydantic item
            book_data = {
                "url": response.url,
                "_id": Book.compute_id(response.url),
                "title": response.css("div.product_main h1::text").get(),
                "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
                "category": response.xpath("//ul[@class='breadcrumb']/li[3]/a/text()").get(),
                "price_incl_tax": get_table_value("Price (incl. tax)"),
                "price_excl_tax": get_table_value("Price (excl. tax)"),
                "availability": get_table_value("Availability"),
                "reviews": int(get_table_value("Number of reviews")),
                "image_url": response.urljoin(response.css("div.item.active > img::attr(src)").get()),
                "rating": response.css("p.star-rating::attr(class)").get().replace("star-rating ", ""),
                "raw_html": response.body.decode('utf-8'),
            }
            
            yield Book(**book_data)

        except Exception as e:
            self.logger.error(
                f"Failed to parse book details for URL {response.url}: {e}", 
                exc_info=True
            )
