# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    title = scrapy.Field()          #标题
    create_date = scrapy.Field()    #创建日期
    tags = scrapy.Field()           #标签
    page_url = scrapy.Field()       #页面url
    cover_url = scrapy.Field()      #封面url
    content = scrapy.Field()        #文章内容
    thumb_up_num = scrapy.Field()   #点赞数
    comment_num = scrapy.Field()    #评论数
    fav_num = scrapy.Field()        #收藏数
