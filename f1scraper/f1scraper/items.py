# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GPItem(scrapy.Item):
    # race info    
    race = scrapy.Field()
    date = scrapy.Field()
    total_laps = scrapy.Field()
    race_winner = scrapy.Field()
    url = scrapy.Field()    


class RaceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    #driver info
    location = scrapy.Field()
    position = scrapy.Field()
    driver_number = scrapy.Field()
    driver_name = scrapy.Field()
    team = scrapy.Field()
    laps_done = scrapy.Field()
    time = scrapy.Field()
    speed = scrapy.Field()
    points = scrapy.Field()

