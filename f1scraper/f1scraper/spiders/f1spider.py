import scrapy
from f1scraper.items import RaceItem, GPItem

class F1spiderSpider(scrapy.Spider):
    name = "f1spider"
    allowed_domains = ["www.formula1.com"]
    start_urls = ["https://www.formula1.com/en/results/2021/races"]

    def start_requests(self):
        yield scrapy.Request(url="https://www.formula1.com/en/results/2021/races", callback=self.parse_race)

    # get race url and enter it
    def parse_race(self, response):
        table_rows = response.css("table tr")

        for item in range(1, len(table_rows)):
            gp_item = GPItem()      

            gp_item["race"] =           response.xpath(f'//*[@id="results-table"]/div/table/tbody/tr[{item}]/td[1]/a/text()').get()
            gp_item["date"] =           response.xpath(f'//*[@id="results-table"]/div/table/tbody/tr[{item}]/td[2]/text()').get()
            gp_item["total_laps"] =     response.xpath(f'//*[@id="results-table"]/div/table/tbody/tr[{item}]/td[5]/text()').get()
            gp_item["race_winner"] =    response.xpath(f'//*[@id="results-table"]/div/table/tbody/tr[{item}]/td[3]/span/span/span[2]/text()').get()
            gp_item["url"] = "https://www.formula1.com" + response.xpath(f'//*[@id="results-table"]/div/table/tbody/tr[{item}]/td[1]/a/@href').get()


            yield gp_item

            race_url = "https://www.formula1.com" + response.xpath(f'//*[@id="results-table"]/div/table/tbody/tr[{item}]/td[1]/a/@href').get()
            yield response.follow(url=race_url, callback=self.parse_drivers)


    # get race data
    def parse_drivers(self, response):
        table_rows = response.css("table tr")

        lap_link = response.xpath('//a[text()="Fastest Laps"]/@href').get()  
        lap_url = response.urljoin(lap_link)      

        for item in range(1, len(table_rows)):
            race_item = RaceItem()

            race_item["location"] =             response.xpath(f'//*[@id="content-dropdown"]/span/span/text()').get()
            race_item["position"] =             response.xpath(f'//*[@id="results-table"]/div[1]/table/tbody/tr[{item}]/td[1]/text()').get()
            race_item["driver_number"] =        response.xpath(f'//*[@id="results-table"]/div[1]/table/tbody/tr[{item}]/td[2]/text()').get()
            race_item["driver_name"] =          response.xpath(f'//*[@id="results-table"]/div[1]/table/tbody/tr[{item}]/td[3]/span/span/span[2]/text()').get()
            race_item["team"] =                 response.xpath(f'//*[@id="results-table"]/div[1]/table/tbody/tr[{item}]/td[4]/span/text()').get()
            race_item["laps_done"] =            response.xpath(f'//*[@id="results-table"]/div[1]/table/tbody/tr[{item}]/td[5]/text()').get()
            race_item["points"] =               response.xpath(f'//*[@id="results-table"]/div[1]/table/tbody/tr[{item}]/td[7]/text()').get()

            yield response.follow(lap_url, callback=self.parse_lap, meta={'item': race_item}, dont_filter=True)


    # get fastest lap & top speed
    def parse_lap(self, response):
        race_item = response.meta['item']

        driver_name = race_item["driver_name"]

        race_item["time"] = response.xpath(f"//tr[contains(., '{driver_name}')]/td[7]/text()").get()
        race_item["speed"] = response.xpath(f"//tr[contains(., '{driver_name}')]/td[8]/text()").get()

        yield race_item
