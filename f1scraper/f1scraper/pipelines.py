# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg
from f1scraper.items import RaceItem, GPItem

class F1ScraperPipeline:
    def process_item(self, item, spider):
        return item

class PostgreSQLPipeline:
    def open_spider(self, spider):
        self.conn = psycopg.connect(
            host = "localhost",
            dbname = "scrapy_db",
            user = "postgres",
            password = "root@postgres",
        )
        
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS grandPrix(
                grand_prix_id VARCHAR(25) NOT NULL PRIMARY KEY,
                grand_prix VARCHAR(25),
                date VARCHAR(55),
                total_laps INT DEFAULT 0,
                race_winner VARCHAR(55),      
                url TEXT                
            );
        """)


#                 race_id VARCHAR(55) NOT NULL PRIMARY KEY REFERENCES grandPrix(grand_prix_id),
        self.cur.execute(""" 
            CREATE TABLE IF NOT EXISTS races(
                race_id VARCHAR(25),
                position VARCHAR(55),
                driver_number INT,
                driver_name VARCHAR(55),
                team VARCHAR(55),
                laps_done INT DEFAULT 0,
                time VARCHAR(55),
                speed DECIMAL,
                points INT    
            );
        """)

        self.count = 0

        self.conn.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.count += 1
        formatted_id = f"GP{self.count:02d}" 

        try:
            if (isinstance(item, GPItem)):
                self.cur.execute("""
                    INSERT INTO grandPrix (grand_prix_id, grand_prix, date, total_laps, race_winner, url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    formatted_id,
                    item.get("race"),
                    item.get("date"),
                    item.get("total_laps"),
                    item.get("race_winner"),
                    item.get("url")
                ))

            elif (isinstance(item, RaceItem)):

                self.cur.execute("""
                    INSERT INTO races (race_id, position, driver_number, driver_name, team, laps_done, time, speed, points)
                    VALUES ((SELECT grand_prix_id FROM grandPrix gp WHERE gp.grand_prix = %s LIMIT 1), %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.get('location'),
                    item.get('position'),
                    item.get('driver_number'),
                    item.get('driver_name'),
                    item.get('team'),
                    item.get('laps_done'),
                    item.get('time'),
                    item.get('speed'),
                    item.get('points'),
                ))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"DATABASE ERROR: {str(e)} | ITEM: {item.get('property_id')}")

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
