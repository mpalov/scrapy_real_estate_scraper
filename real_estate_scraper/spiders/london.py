from typing import Any
import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader
from ..items import PropertyItem


class LondonSpider(scrapy.Spider):
    name = 'london'
    start_urls = [
        'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&index=0&propertyTypes=detached%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='
    ]

    def __init__(self, check=False, *args, **kwargs):
        """Initialize the spider with a 'check' mode."""
        super().__init__(*args, **kwargs)
        self.check = check  # Flag to determine if it's a health check run

    def parse(self, response: Response, **kwargs: Any):
        if response.status == 200:
            self.log('Request was successful!')

            base_url = 'https://www.rightmove.co.uk'
            property_links = response.css('a.propertyCard-link::attr(href)').getall()

            if not property_links:
                self.log("No properties found, possible selector issue!")
                return

            # In check mode, only process the first property and stop
            if self.check:
                self.log("Running health check mode: Making only one request.")
                test_url = base_url + property_links[0]
                yield scrapy.Request(test_url, callback=self.parse_property, meta={"check": True})
                return  # Stops further execution in check mode

            # Get the current index and calculate the page number
            current_index = int(response.url.split("index=")[1].split("&")[0])
            current_page = (current_index // 24) + 1  # Calculate page number based on index

            # If there are property links, continue parsing
            if property_links:
                for link in property_links:
                    full_url = base_url + link
                    yield response.follow(full_url, self.parse_property, meta={"page": current_page})

                # Pagination: Update the index for the next page
                next_index = current_index + 24
                next_page_url = response.url.replace(f'index={current_index}', f'index={next_index}')
                self.log(f"Next page URL: {next_page_url}")

                # Continue to the next page if there are property links on the next page
                yield scrapy.Request(next_page_url, callback=self.parse)
            else:
                self.log("No properties found, stopping the spider.")
        else:
            self.log(f"Request failed with status: {response.status}")

    def parse_property(self, response: Response):
        """Extract data for individual property pages."""
        current_city = 'London'
        address = response.css('div._1KCWj_-6e8-7_oJv_prX0H > div > h1::text').get()

        if response.meta.get("check"):
            # Health check mode
            self.log("Running health check on property detail page...")

            # Perform basic checks for presence of essential selectors
            price = response.css('div._1gfnqJ3Vtd1z40MlC0MzXu span::text').get()
            property_size = response.css(
                '#info-reel > div:nth-child(4) > dd > span > p._1hV1kqpVceE9m-QrX_hWDN::text').get()
            property_type = response.css('div:nth-child(1) > dd > span > p::text').get()

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

        # Normal scraping mode
        loader = ItemLoader(item=PropertyItem(), response=response)
        loader.add_css("price", 'div._1gfnqJ3Vtd1z40MlC0MzXu span::text')
        loader.add_value("city", current_city)
        loader.add_value("address", address)
        loader.add_css("property_size", '#info-reel > div:nth-child(4) > dd > span > p._1hV1kqpVceE9m-QrX_hWDN::text')
        loader.add_css("property_type", 'div:nth-child(1) > dd > span > p::text')
        amenities = response.css(
            "#main > div > div.WJG_W7faYk84nW-6sCBVi > div > article[data-testid='primary-layout'] > ul > li::text").getall()
        loader.add_value("amenities", amenities)
        loader.add_value("listing_url", response.url)

        yield loader.load_item()
