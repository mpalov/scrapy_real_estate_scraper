# SPIDER AFTER THE HEALTH CHECK UPDATE

from typing import Any
import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader
from ..items import PropertyItem
import re


class RomeSpider(scrapy.Spider):
    name = "rome"
    start_urls = ["https://www.luxuryestate.com/italy/latium/rome/rome?sort=relevance&types=41%7C39%7C31%7C37"]

    crawled_count = 0  # Counter to track the number of scraped properties
    max_results = 1100  # Stop when reaching this limit

    def __init__(self, check=False, *args, **kwargs):
        """Initialize the spider with a 'check' mode."""
        super().__init__(*args, **kwargs)
        self.check = check  # Flag to determine if it's a health check run

    def parse(self, response: Response, **kwargs: Any):
        if response.status == 200:
            self.log(f'Request was successful! Crawled so far: {self.crawled_count}/{self.max_results}')

            property_links = response.css('.details_title a.js_clickable::attr(href)').getall()

            if not property_links:
                self.log("No properties found, possible selector issue!")
                return

            # In check mode, only process the first property and stop
            if self.check:
                self.log("Running health check mode: Making only one request.")
                test_url = property_links[0]
                yield scrapy.Request(test_url, callback=self.parse_property, meta={"check": True})
                return  # Stops further execution in check mode

            for link in property_links:
                yield response.follow(link, self.parse_property)

            # Handle pagination
            next_page = response.css('div.block-post.style-button a.next::attr(href)').get()

            if next_page and self.crawled_count < self.max_results:
                self.log(f"Next page URL: {next_page}")
                yield scrapy.Request(url=next_page, callback=self.parse)
            else:
                self.log("No more pages or max limit reached, stopping.")
        else:
            self.log(f"Request failed with status: {response.status}")

    def parse_property(self, response: Response):
        """Extract data for individual property pages."""
        current_city = 'Rome'
        address = response.css('div.general-features span.feat-label:contains("Address") + div.single-value::text').get(
            default='N/A')

        if response.meta.get("check"):
            # Health check mode
            self.log("Running health check on property detail page...")

            # Perform basic checks for presence of essential selectors
            price = response.css('div.prices.hidden-xs div.text-right.price.style-title1::text').get()
            property_size = response.css(
                'div.general-features span.feat-label:contains("Size") + div.single-value::text').get()

            missing_fields = []
            if not price:
                missing_fields.append("price")
            if not address:
                missing_fields.append("address")
            if not property_size:
                missing_fields.append("property_size")

            if missing_fields:
                self.log(f"[HEALTH CHECK] Missing fields: {', '.join(missing_fields)}")
            else:
                self.log("[HEALTH CHECK] All key fields present.")

            return  # Do NOT yield an item during health check

        loader = ItemLoader(item=PropertyItem(), response=response)

        # Extract data fields
        loader.add_css("price", 'div.prices.hidden-xs div.text-right.price.style-title1::text')
        loader.add_value("city", current_city)
        address = response.css('div.general-features span.feat-label:contains("Address") + div.single-value::text').get(
            default='N/A')
        loader.add_value('address', address)
        loader.add_css("property_size",
                       'div.general-features span.feat-label:contains("Size") + div.single-value::text')

        pattern = r'\/p\d+-([a-zA-Z]+)-for-sale'
        match = re.search(pattern, response.url)

        # Ensure match is found before accessing group(1)
        property_type = match.group(1) if match else "N/A"

        loader.add_value("property_type", property_type)
        # Extract exterior and interior amenities separately

        exterior_amenities = response.css(
            "div.general-features span.feat-label:contains('Exterior Amenities') + div.multiple-values b::text").getall()
        interior_amenities = response.css(
            "div.general-features span.feat-label:contains('Interior Amenities') + div.multiple-values b::text").getall()

        # Combine both lists into one
        all_amenities = exterior_amenities + interior_amenities

        # Add to ItemLoader
        loader.add_value("amenities", all_amenities)

        loader.add_value("listing_url", response.url)

        yield loader.load_item()

# MAIN SCRAPER

# from typing import Any
# import scrapy
# from scrapy.http import Response
# from scrapy.loader import ItemLoader
# from ..items import PropertyItem
# import re
#
#
# class RomeSpider(scrapy.Spider):
#     name = "rome"
#     start_urls = ["https://www.luxuryestate.com/italy/latium/rome/rome?sort=relevance&types=41%7C39%7C31%7C37"]
#
#     crawled_count = 0  # Counter to track the number of scraped properties
#     max_results = 1100  # Stop when reaching this limit
#
#     def parse(self, response: Response, **kwargs: Any):
#         if response.status == 200:
#             self.log(f'Request was successful! Crawled so far: {self.crawled_count}/{self.max_results}')
#
#             property_links = response.css('.details_title a.js_clickable::attr(href)').getall()
#
#             for link in property_links:
#                 yield response.follow(link, self.parse_property)
#
#             # Handle pagination
#             next_page = response.css('div.block-post.style-button a.next::attr(href)').get()
#
#             if next_page and self.crawled_count < self.max_results:
#                 self.log(f"Next page URL: {next_page}")
#                 yield scrapy.Request(url=next_page, callback=self.parse)
#             else:
#                 self.log("No more pages or max limit reached, stopping.")
#         else:
#             self.log(f"Request failed with status: {response.status}")
#
#     def parse_property(self, response: Response):
#         """Extract data for individual property pages."""
#         current_city = 'Rome'
#         loader = ItemLoader(item=PropertyItem(), response=response)
#
#         # Extract data fields
#         loader.add_css("price", 'div.prices.hidden-xs div.text-right.price.style-title1::text')
#         loader.add_value("city", current_city)
#         address = response.css('div.general-features span.feat-label:contains("Address") + div.single-value::text').get(default='N/A')
#         loader.add_value('address', address)
#         loader.add_css("property_size", 'div.general-features span.feat-label:contains("Size") + div.single-value::text')
#
#         pattern = r'\/p\d+-([a-zA-Z]+)-for-sale'
#         match = re.search(pattern, response.url)
#
#         # Ensure match is found before accessing group(1)
#         property_type = match.group(1) if match else "N/A"
#
#         loader.add_value("property_type", property_type)
#         # Extract exterior and interior amenities separately
#
#         exterior_amenities = response.css("div.general-features span.feat-label:contains('Exterior Amenities') + div.multiple-values b::text").getall()
#         interior_amenities = response.css("div.general-features span.feat-label:contains('Interior Amenities') + div.multiple-values b::text").getall()
#
#         # Combine both lists into one
#         all_amenities = exterior_amenities + interior_amenities
#
#         # Add to ItemLoader
#         loader.add_value("amenities", all_amenities)
#
#         loader.add_value("listing_url", response.url)
#
#         yield loader.load_item()
