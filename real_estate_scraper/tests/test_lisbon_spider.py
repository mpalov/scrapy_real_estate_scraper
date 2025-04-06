import unittest
from scrapy.http import HtmlResponse, Request
from real_estate_scraper.real_estate_scraper.spiders.lisbon import LisbonSpider


class TestLisbonSpider(unittest.TestCase):
    def setUp(self):
        """Initialize the spider before each test."""
        self.spider = LisbonSpider()

    def test_parse(self):
        """Test that the spider extracts property links and follows them correctly."""
        html = '<html><body><div class="item-data"><a href="/property-1"></a></div></body></html>'
        request = Request(url="https://www.properstar.com/portugal/lisbon/buy/apartment-house")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse(response))

        expected_url = "https://www.properstar.com/property-1"
        self.assertTrue(any(r.url == expected_url for r in result))

    def test_pagination(self):
        """Test if the spider correctly paginates to the next page."""
        html = '<html><body><ul><li class="page-link next"><a href="/page-2"></a></li></ul></body></html>'
        request = Request(url="https://www.properstar.com/portugal/lisbon/buy/apartment-house")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse(response))
        next_page_requests = [r.url for r in result if isinstance(r, Request)]

        self.assertTrue(any("page-2" in r for r in next_page_requests))

    def test_handle_404(self):
        """Test that the spider gracefully handles 404 errors by returning no results."""
        request = Request(url="https://www.properstar.com/some-non-existent-page")
        response = HtmlResponse(url=request.url, request=request, status=404)

        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 0)

    def test_parse_property_with_missing_data(self):
        """Test if the spider correctly extracts property details and handles missing fields."""
        html = '''
        <html>
            <body>
                <div class="listing-price-main"><span>€600,000</span></div>
                <!-- Missing address -->
                <div>
                    <span class="property-value">100 sqm</span>
                </div>
                <div>
                    <ol>
                        <li class="active breadcrumb-item"><a>House</a></li>
                    </ol>
                </div>
                <section class="listing-section amenities-section">
                    <div class="feature-list">
                        <div class="feature-item">
                            <div class="feature-content">
                                <span class="property-value">Terrace</span>
                            </div>
                        </div>
                    </div>
                </section>
            </body>
        </html>
        '''
        request = Request(url="https://www.properstar.com/property-1")
        response = HtmlResponse(url=request.url, request=request, body=html, encoding='utf-8')

        result = list(self.spider.parse_property(response))

        expected_item = {
            "price": 600000.0,
            "city": "Lisbon",
            "address": "N/A",
            "property_size": 100.0,
            "property_type": "House",
            "amenities": ["Terrace"],
            "listing_url": "https://www.properstar.com/property-1",
        }

        for key, value in expected_item.items():
            self.assertEqual(result[0].get(key), value)


if __name__ == "__main__":
    unittest.main()
