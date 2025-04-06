import unittest
from scrapy.http import HtmlResponse, Request
from real_estate_scraper.real_estate_scraper.spiders.london import LondonSpider


# ---------------------------
# Tests for the London Spider
# ---------------------------

class TestLondonSpider(unittest.TestCase):
    def setUp(self):
        """Initialize the spider before each test."""
        self.spider = LondonSpider()

    def test_parse(self):
        """Test that the spider extracts property links and follows them correctly."""
        html = '<html><body><a class="propertyCard-link" href="/property-1"></a></body></html>'
        request = Request(url="https://www.rightmove.co.uk/find?index=0")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse(response))

        # Check if the spider is generating a request for the correct absolute URL
        expected_url = "https://www.rightmove.co.uk/property-1"
        self.assertTrue(any(r.url == expected_url for r in result))

    def test_pagination(self):
        """Test if the spider correctly paginates to the next page."""
        html = '<html><body><a class="propertyCard-link" href="/property-1"></a></body></html>'
        request = Request(url="https://www.rightmove.co.uk/find?index=0")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse(response))

        # Debugging: Print all request URLs
        next_page_requests = [r.url for r in result if isinstance(r, Request)]
        print(f"Generated pagination requests: {next_page_requests}")

        # Check that the next page URL contains the correct index increment
        self.assertTrue(any("index=24" in r.url for r in result if isinstance(r, Request)))

    def test_handle_404(self):
        """Test that the spider gracefully handles 404 errors by returning no results."""
        request = Request(url="https://www.rightmove.co.uk/some-non-existent-page")
        response = HtmlResponse(url=request.url, request=request, status=404)

        result = list(self.spider.parse(response))

        # The spider should return an empty result list
        self.assertEqual(len(result), 0)

    def test_parse_property_with_missing_data(self):
        """Test if the spider correctly extracts property details and handles missing fields."""
        html = '''
        <html>
            <body>
                <div class="_1gfnqJ3Vtd1z40MlC0MzXu"><span>£500,000</span></div>
                <!-- Missing address -->
                <div id="info-reel">
                    <div>
                        <dd>
                            <span>
                                <p class="_1hV1kqpVceE9m-QrX_hWDN">1,200 sqft</p>
                            </span>
                        </dd>
                    </div>
                </div>
                <div>
                    <dd>
                        <span>
                            <p>House</p>
                        </span>
                    </dd>
                </div>
                <ul>
                    <li>Garden</li>
                    <li>Garage</li>
                </ul>
            </body>
        </html>
        '''
        request = Request(url="https://www.rightmove.co.uk/property-1")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse_property(response))

        # Expected output based on the spider's behavior
        expected_item = {
            "price": "£500,000",  # Keep as a string since the spider doesn't convert currency
            "city": "London",
            "address": "N/A",  # The spider should handle missing address fields
            "property_size": "1,200 sqft",  # Keeping the format consistent
            "property_type": "House",
            "amenities": ["Garden", "Garage"],
            "listing_url": "https://www.rightmove.co.uk/property-1",
        }

        # Compare field by field
        for key, value in expected_item.items():
            self.assertEqual(result[0].get(key), value)


if __name__ == "__main__":
    unittest.main()
