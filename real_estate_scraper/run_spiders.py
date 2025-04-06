from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import defer

process = CrawlerProcess(get_project_settings())


@defer.inlineCallbacks
def crawl():
    yield process.crawl("london")  # Runs first spider
    yield process.crawl("paris")  # Runs second spider after first is done
    yield process.crawl("madrid")  # Continues sequentially
    yield process.crawl("rome")
    yield process.crawl("lisbon")
    process.stop()  # Stops Scrapy when all spiders are done


crawl()
process.start()
