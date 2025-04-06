# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
from scrapy.exceptions import DropItem
import os
from dotenv import load_dotenv

load_dotenv()


class PostgresPipeline:
    def open_spider(self, spider):
        """Connect to the PostgreSQL database when the spider starts."""
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        self.cursor = self.connection.cursor()

        # Create table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS real_estate (
                id SERIAL PRIMARY KEY,
                price TEXT,
                city TEXT,
                address TEXT,
                property_size TEXT,
                property_type TEXT,
                amenities TEXT[],
                listing_url TEXT
            )
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        """Insert data into the database."""
        try:
            self.cursor.execute("""
                INSERT INTO real_estate (price, city, address, property_size, property_type, amenities, listing_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("price"),
                item.get("city"),
                item.get("address"),
                item.get("property_size"),
                item.get("property_type"),
                item.get("amenities"),
                item.get("listing_url")
            ))

            self.connection.commit()
        except psycopg2.Error as e:
            spider.logger.error(f"Error inserting into database: {e}")
            raise DropItem(f"Database error: {e}")

        return item

    def close_spider(self, spider):
        """Close database connection when spider finishes."""
        self.cursor.close()
        self.connection.close()


class RealEstateScraperPipeline:
    def process_item(self, item, spider):
        return item
