import unittest
import psycopg2
from real_estate_scraper.real_estate_scraper.pipelines import PostgresPipeline
from real_estate_scraper.real_estate_scraper.items import (
    PropertyItem, clean_price, clean_sqft, clean_address
)
from unittest.mock import MagicMock, patch


# ---------------------------
# Tests for Data Cleaning Functions
# ---------------------------
class TestDataCleaningFunctions(unittest.TestCase):
    def test_clean_price(self):
        self.assertEqual(clean_price("£500,000"), 585000.0)  # Assuming GBP to EUR conversion
        self.assertEqual(clean_price("$450,000"), 450000.0)
        self.assertEqual(clean_price("Not Available"), "N/A")
        self.assertEqual(clean_price(None), "N/A")  # Test None input
        self.assertEqual(clean_price("500000"), 500000.0)  # Test without currency symbol

    def test_clean_sqft(self):
        self.assertEqual(clean_sqft("1,200 sqft"), 1200.0)
        self.assertEqual(clean_sqft("Not listed"), "N/A")
        self.assertEqual(clean_sqft(None), "N/A")  # Test None input
        self.assertEqual(clean_sqft("1200 sq ft"), 1200.0)  # Test different format
        self.assertEqual(clean_sqft("1200"), 1200.0)  # Test without unit

    def test_clean_address(self):
        self.assertEqual(clean_address(" 123 Baker Street \n"), "123 Baker Street")
        self.assertEqual(clean_address(None), "N/A")
        self.assertEqual(clean_address(""), "N/A")  # Test empty string
        self.assertEqual(clean_address(" Apt. 4B, 221B Baker Street "),
                         "Apt. 4B, 221B Baker Street")  # Test with apartment number


# ---------------------------
# Tests for Property Item Processing
# ---------------------------
class TestPropertyItem(unittest.TestCase):
    def test_item_processing(self):
        item = PropertyItem()
        item["price"] = clean_price("£400,000")
        item["city"] = "London"
        item["address"] = clean_address(" 221B Baker Street ")
        item["property_size"] = clean_sqft("1,500 sqft")
        item["property_type"] = "House"
        item["amenities"] = ["Garden", "Garage"]
        item["listing_url"] = "http://example.com"

        self.assertEqual(item["price"], 468000.0)  # Check processed price
        self.assertEqual(item["address"], "221B Baker Street")
        self.assertEqual(item["property_size"], 1500.0)


# ---------------------------
# Tests for the Postgres Pipeline
# ---------------------------
class TestPostgresPipeline(unittest.TestCase):
    @patch("psycopg2.connect")
    def test_database_insertion(self, mock_connect):
        mock_cursor = MagicMock()
        # The pipeline creates the table and then executes the INSERT query,
        # so expect 2 calls to execute.
        mock_connect.return_value.cursor.return_value = mock_cursor
        pipeline = PostgresPipeline()
        pipeline.open_spider(None)

        item = PropertyItem(
            price="500000", city="London", address="123 Street", property_size="1200 sqft",
            property_type="House", amenities=["Garden"], listing_url="http://example.com"
        )
        pipeline.process_item(item, None)

        calls = mock_cursor.execute.call_args_list
        # Expecting 2 calls: one for table creation, one for insertion
        self.assertEqual(len(calls), 2)
        # Verify that the second call is the INSERT statement
        self.assertIn("INSERT INTO real_estate", calls[1][0][0])
        pipeline.close_spider(None)

    @patch("psycopg2.connect")
    def test_database_error_handling(self, mock_connect):
        mock_connect.side_effect = psycopg2.OperationalError("Database connection failed")
        with self.assertRaises(psycopg2.OperationalError):
            pipeline = PostgresPipeline()
            pipeline.open_spider(None)


if __name__ == "__main__":
    unittest.main()
