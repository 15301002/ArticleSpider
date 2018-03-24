# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst
from ArticleSpider.settings import SQL_DATETIME_FORMAT


class JobBoleItemLoader(ItemLoader):
    # 默认ItemLoader只保留css选择器解析后的第一个元素
    default_output_processor = TakeFirst()


class ZhiHuQuestionItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def date_convert(date_str):
    # 日期转换
    try:
        return datetime.datetime.strptime(date_str, '%Y/%m/%d').date()
    except Exception:
        return datetime.datetime.now().date()


def get_num(num_str):
    # 正则表达式获取数字
    match_obj = re.match(".*?(\d+).*", num_str)
    if match_obj:
        return int(match_obj.group(1))
    else:
        return 0


def removes_comment_tags(tag):
    # 去除评论标签
    if "评论" in tag:
        return ''
    else:
        return tag.strip()


def return_value(value):
    return value


class JobBoleArticleItem(scrapy.Item):
    """
    伯乐在线blog.JobBole Item类
    """
    title = scrapy.Field()  # 标题
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )  # 创建日期
    tags = scrapy.Field(
        input_processor=MapCompose(removes_comment_tags),
        output_processor=Join(",")
    )  # 标签
    page_url = scrapy.Field()  # 页面url
    page_url_id = scrapy.Field()  # 页面urlID
    cover_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )  # 封面url
    cover_path = scrapy.Field()  # 封面保存路径
    content = scrapy.Field()  # 文章内容
    thumb_up_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )  # 点赞数
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )  # 评论数
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )  # 收藏数

    def get_insert_sql(self):
        inert_sql = '''
                    INSERT INTO article_jobbole(
                        page_url_id, page_url, title, create_date, cover_url, tags, content,
                        cover_path, thumb_up_num, comment_num, fav_num)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
        params = (self.page_url_id, self.page_url
                  , self.title, self.create_date
                  , self.cover_url[0], self.tags
                  , self.content, self.get("cover_path", "")
                  , self.get("thumb_up_num", 0), self.comment_num, self.fav_num)
        return inert_sql, params


class ZhiHuQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    topics = scrapy.Field(
        output_processor=Join(",")
    )
    answers_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    watch_num = scrapy.Field()
    click_num = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """INSERT INTO zhihu_question(question_id, title, content, watch_num
                        , click_num, comment_num, topics, answers_num, crawl_time)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY UPDATE title=VALUES(title)
                        , content=VALUES(content), click_num=VALUES(click_num)
                        , comment_num=VALUES(comment_num), answers_num=VALUES(answers_num)
                        , click_num=VALUES(click_num), click_num=VALUES(click_num)
                        , watch_num=VALUES(watch_num), crawl_update_time=VALUES(crawl_time)"""

        params = (self['question_id'], self['title'], self['content'], self['watch_num']
                  , self['click_num'], self['comment_num'], self['topics'], self['answers_num']
                  , datetime.datetime.now().strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params


class ZhiHuAnswerItem(scrapy.Item):
    answer_id = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    author_name = scrapy.Field()
    vote_up_count = scrapy.Field()
    comment_count = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """INSERT INTO zhihu_answer(answer_id, question_id, author_id
                        , author_name, vote_up_count, comment_count
                        , content, create_time, update_time, crawl_time)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE content=VALUES(content), comment_count=VALUES(comment_count)
                        , vote_up_count=VALUES(vote_up_count), crawl_update_time=VALUES(crawl_time)"""

        params = (self["answer_id"], self["question_id"], self["author_id"]
                  , self["author_name"], self["vote_up_count"], self["comment_count"], self["content"]
                  , datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
                  , datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
                  , datetime.datetime.now().strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params
