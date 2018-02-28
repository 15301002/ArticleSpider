# -*- coding: utf-8 -*-
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.json_file = codecs.open('article.json', 'w', 'utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.json_file.write(lines)
        return item

    def spider_closed(self, spider):
        self.json_file.close()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DB"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset=settings["MYSQL_CHARSET"],
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_err, item, spider)

    def handle_err(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        inert_sql = '''
            INSERT INTO article_jobbole(
                page_url_id, page_url, title, create_date, cover_url, tags, content,
                cover_path, thumb_up_num, comment_num, fav_num)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(inert_sql, (item["page_url_id"], item["page_url"]
                                   , item["title"], item["create_date"]
                                   , item["cover_url"][0], item["tags"]
                                   , item["content"], item.get("cover_path", "")
                                   , item.get("thumb_up_num", 0), item["comment_num"], item["fav_num"]))


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "cover_url" in item:
            for ok, value in results:
                if ok:
                    item['cover_path'] = value.get("path", "")
                else:
                    item['cover_path'] = ""
        return item
