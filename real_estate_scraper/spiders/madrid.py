# SPIDER AFTER THE HEALTH CHECK UPDATE

from typing import Any
import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader
from ..items import PropertyItem


class MadridSpider(scrapy.Spider):
    name = "madrid"
    start_urls = ["https://www.properstar.com/spain/madrid/buy/apartment-house"]
    crawled_count = 0  # Counter to track the number of scraped properties
    max_results = 1200  # Stop when reaching this limit

    def __init__(self, check=False, *args, **kwargs):
        """Initialize the spider with a 'check' mode."""
        super().__init__(*args, **kwargs)
        self.check = check  # Flag to determine if it's a health check run

    def parse(self, response: Response, **kwargs: Any):
        if response.status == 200:
            self.log(f'Request was successful! Crawled so far: {self.crawled_count}/{self.max_results}')

            base_url = "https://www.properstar.com"
            property_links = response.css('div.item-data > a::attr(href)').getall()

            if not property_links:
                self.log("No properties found, possible selector issue!")
                return

            # In check mode, only process the first property and stop
            if self.check:
                self.log("Running health check mode: Making only one request.")
                test_url = base_url + property_links[0]
                yield scrapy.Request(test_url, callback=self.parse_property, meta={"check": True})
                return  # Stops further execution in check mode

            for link in property_links:
                if self.crawled_count >= self.max_results:
                    self.log("Reached max results, stopping spider.")
                    self.crawler.engine.close_spider(self, "Max results reached")
                    return

                full_url = base_url + link
                self.crawled_count += 1
                yield response.follow(full_url, self.parse_property)

            # Handle pagination
            next_page = response.css('ul > li.page-link.next > a::attr(href)').get()
            if next_page and self.crawled_count < self.max_results:
                next_page_url = base_url + next_page

                self.log(f"Next page URL: {next_page_url}")
                yield scrapy.Request(url=next_page_url, callback=self.parse)
            else:
                self.log("No more pages or max limit reached, stopping.")
        else:
            self.log(f"Request failed with status: {response.status}")

    def parse_property(self, response: Response):
        """Extract data for individual property pages."""
        current_city = 'Madrid'
        address = response.css('.address > span::text').get(default='N/A')
        if response.meta.get("check"):
            # Health check mode
            self.log("Running health check on property detail page...")

            # Perform basic checks for presence of essential selectors
            price = response.css('.listing-price-main > span::text').get()
            property_size = response.css(
                'div:nth-child(4) > div > div > span.property-value::text').get()
            property_type = response.css('ol > li.active.breadcrumb-item > a::text').get()

            missing_fields = []
            if not price:
                missing_fields.append("price")
            if not address:
                missing_fields.append("address")
            if not property_size:
                missing_fields.append("property_size")
            if not property_type:
                missing_fields.append("property_type")

            if missing_fields:
                self.log(f"[HEALTH CHECK] Missing fields: {', '.join(missing_fields)}")
            else:
                self.log("[HEALTH CHECK] All key fields present.")

            return  # Do NOT yield an item during health check

        loader = ItemLoader(item=PropertyItem(), response=response)

        # Extract data fields
        loader.add_css("price", '.listing-price-main > span::text')
        loader.add_value("city", current_city)
        loader.add_value('address', address)
        loader.add_css("property_size", 'div:nth-child(4) > div > div > span.property-value::text')
        loader.add_css("property_type", 'ol > li.active.breadcrumb-item > a::text')
        amenities = response.css(
            "#app section.listing-section.amenities-section div.feature-list div.feature-item div.feature-content span.property-value::text").getall()
        loader.add_value("amenities", amenities)
        loader.add_value("listing_url", response.url)

        yield loader.load_item()

# MAIN SPIDER

# from typing import Any
# import scrapy
# from scrapy.http import Response
# from scrapy.loader import ItemLoader
# from ..items import PropertyItem
#
#
# class MadridSpider(scrapy.Spider):
#     name = "madrid"
#     start_urls = ["https://www.properstar.com/spain/madrid/buy/apartment-house"]
#     crawled_count = 0  # Counter to track the number of scraped properties
#     max_results = 1200  # Stop when reaching this limit
#
#     def parse(self, response: Response, **kwargs: Any):
#         if response.status == 200:
#             self.log(f'Request was successful! Crawled so far: {self.crawled_count}/{self.max_results}')
#
#             base_url = "https://www.properstar.com"
#             property_links = response.css('div.item-data > a::attr(href)').getall()
#
#             for link in property_links:
#                 if self.crawled_count >= self.max_results:
#                     self.log("Reached max results, stopping spider.")
#                     self.crawler.engine.close_spider(self, "Max results reached")
#                     return
#
#                 full_url = base_url + link
#                 self.crawled_count += 1
#                 yield response.follow(full_url, self.parse_property)
#
#             # Handle pagination
#             next_page = response.css('ul > li.page-link.next > a::attr(href)').get()
#             if next_page and self.crawled_count < self.max_results:
#                 next_page_url = base_url + next_page
#
#                 self.log(f"Next page URL: {next_page_url}")
#                 yield scrapy.Request(url=next_page_url, callback=self.parse)
#             else:
#                 self.log("No more pages or max limit reached, stopping.")
#         else:
#             self.log(f"Request failed with status: {response.status}")
#
#     def parse_property(self, response: Response):
#         """Extract data for individual property pages."""
#         current_city = 'Madrid'
#         loader = ItemLoader(item=PropertyItem(), response=response)
#
#         # Extract data fields
#         loader.add_css("price", '.listing-price-main > span::text')
#         loader.add_value("city", current_city)
#         address = response.css('.address > span::text').get(default='N/A')
#         loader.add_value('address', address)
#         loader.add_css("property_size", 'div:nth-child(4) > div > div > span.property-value::text')
#         loader.add_css("property_type", 'ol > li.active.breadcrumb-item > a::text')
#         amenities = response.css(
#             "#app section.listing-section.amenities-section div.feature-list div.feature-item div.feature-content span.property-value::text").getall()
#         loader.add_value("amenities", amenities)
#         loader.add_value("listing_url", response.url)
#
#         yield loader.load_item()
