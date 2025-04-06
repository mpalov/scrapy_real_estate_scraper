import unittest
from scrapy.http import HtmlResponse, Request
from real_estate_scraper.real_estate_scraper.spiders.rome import RomeSpider


class TestRomeSpider(unittest.TestCase):
    def setUp(self):
        """Initialize the spider before each test."""
        self.spider = RomeSpider()

    def test_parse(self):
        """Test that the spider extracts property links and follows them correctly."""
        html = '<html><body><div class="details_title"><a class="js_clickable" href="/property-1"></a></div></body></html>'
        request = Request(url="https://www.luxuryestate.com/italy/latium/rome/rome")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse(response))

        expected_url = "https://www.luxuryestate.com/property-1"
        self.assertTrue(any(r.url == expected_url for r in result))

    def test_handle_404(self):
        """Test that the spider gracefully handles 404 errors by returning no results."""
        request = Request(url="https://www.luxuryestate.com/non-existent-page")
        response = HtmlResponse(url=request.url, request=request, status=404)

        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 0)

    def test_parse_property_with_missing_data(self):
        """Test if the spider correctly extracts property details and handles missing fields."""
        html = '''
        <html>
            <body>
                <div class="prices hidden-xs"><div class="text-right price style-title1">€850,000</div></div>
                <div class="general-features">
                    <span class="feat-label">Size</span>
                    <div class="single-value">120 sqm</div>
                </div>
                <div>
                    <div class="general-features">
                        <span class="feat-label">Exterior Amenities</span>
                        <div class="multiple-values"><b>Garden</b></div>
                    </div>
                </div>
            </body>
        </html>
        '''
        request = Request(url="https://www.luxuryestate.com/property-1")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse_property(response))

        expected_item = {
            "price": 850000.0,
            "city": "Rome",
            "address": "N/A",  # Address missing, so it should be "N/A"
            "property_size": 120.0,
            "property_type": "N/A",  # Regex might not match, so it should default to "N/A"
            "amenities": ["Garden"],
            "listing_url": "https://www.luxuryestate.com/property-1",
        }

        for key, value in expected_item.items():
            self.assertEqual(result[0].get(key), value)

    def test_parse_multiple_properties(self):
        """Test if the spider correctly extracts multiple property links from a page."""
        html = '''
        <html>
            <body>
                <div class="details_title"><a class="js_clickable" href="/property-1"></a></div>
                <div class="details_title"><a class="js_clickable" href="/property-2"></a></div>
            </body>
        </html>
        '''
        request = Request(url="https://www.luxuryestate.com/italy/latium/rome/rome")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse(response))

        expected_urls = ["https://www.luxuryestate.com/property-1", "https://www.luxuryestate.com/property-2"]
        extracted_urls = [r.url for r in result]

        for expected_url in expected_urls:
            self.assertIn(expected_url, extracted_urls)


if __name__ == "__main__":
    unittest.main()
