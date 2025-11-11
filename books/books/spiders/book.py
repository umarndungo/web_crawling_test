import scrapy
from books.items import BooksItem

class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        try:

            for book in response.css("article.product_pod"):
                item = BooksItem()
                item["url"] = book.css("h3 > a::attr(href)").get()

                # Instead of adding the title and price, 
                # let's follow the link to the book page to scrape what we need
                yield response.follow(
                    item["url"],
                    callback=self.parse_book_details,
                    meta={'item': item}
                )

            # Handling pagination: Crawling through the pages
            next_page = response.css("li.next > a::attr(href)").get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                yield scrapy.Request(url=next_page_url, callback=self.parse)

        except Exception as e:
            self.logger.error(
                f"An error occured in parse method for URL {response.url}: {e}",
                exc_info=True
            )

    def parse_book_details(self, response):
        '''
        TODO: Figure out how to handle pagination by using the book item url, 
            to gather the following data:        
                • Name of the book 
                • Description of the book 
                • Book category 
                • Book prices (Including and Excluding taxes) 
                • Availability

                • Number of reviews 
                • The image URL of the book cover 
                • Rating of the book
        '''
        try:

            item = response.meta['item']

            # Scrape the data from the detail page
            main = response.css("div.product_main")
            title = main.css("h1::text").get()
            if title:
                item["title"] = title
            else:
                self.logger.warning(f"Title not found for page: {response.url}")
                item['title'] = "N/A"
            item["description"] = response.css("article.product_page > p::text").get()
            item["category"] = response.css("ul.breadcrumb > li:nth-last-child(2)> a::text").get()

            # Prices and availability
            table = response.css("table.table-striped")
            item["price_excl_tax"] = table.css("tr:nth-child(3) > td::text").get()
            item["price_incl_tax"] = table.css("tr:nth-child(4) > td::text").get()
            item["availability"] = table.css("tr:nth-child(6) > td::text").get()
            
            # Number of reviews
            item["reviews"] = table.css("tr:nth-child(7) > td::text").get()
            
            # Image URL
            item["image_url"] = response.urljoin(response.css("div.item.active > img::attr(src)").get())
            
            # Rating
            star_rating_class = response.css("p.star-rating::attr(class)").get()
            item["rating"] = star_rating_class.replace("star-rating ", "") if star_rating_class else "Not rated"
            
            yield item

        except Exception as e:
            self.logger.error(
                f"Failed to parse book details for URL {response.url}: {e}", 
                exc_info=True
            )

