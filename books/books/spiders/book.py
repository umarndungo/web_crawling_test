import scrapy
from books.items import BooksItem

class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book in response.css("article.product_pod"):
            item = BooksItem()
            item["url"] = book.css("h3 > a::attr(href)").get()
            item["title"] = book.css("h3 > a::attr(title)").get()
            item["price"] = book.css(".price_color::text").get()
            yield item

        # Handling pagination: Crawling through the pages
        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

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
