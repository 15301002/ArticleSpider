# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst
import datetime
import re


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
    title = scrapy.Field()          # 标题
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )                               # 创建日期
    tags = scrapy.Field(
        input_processor=MapCompose(removes_comment_tags),
        output_processor=Join(",")
    )                               # 标签
    page_url = scrapy.Field()       # 页面url
    page_url_id = scrapy.Field()    # 页面urlID
    cover_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )                               # 封面url
    cover_path = scrapy.Field()     # 封面保存路径
    content = scrapy.Field()        # 文章内容
    thumb_up_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )                               # 点赞数
    comment_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )                               # 评论数
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )                               # 收藏数


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
