# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import ArticleItem
import re


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        url_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for node in url_nodes:
            article_url = node.css('::attr("href")').extract_first("")
            cover_image_url = node.css('img::attr("src")').extract_first("")
            yield Request(url=parse.urljoin(response.url, article_url), meta={"cover_url": cover_image_url}, callback=self.parse_article_page)
        next_url = response.css('a.next.page-numbers::attr("href")').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_article_page(self, response):
        article_item = ArticleItem()

        article_item["page_url"] = response.url
        article_item["cover_url"] = response.meta.get("cover_url")
        article_item["title"] = response.css(".entry-header h1::text").extract_first("")
        tag_node = response.css(".entry-meta-hide-on-mobile")
        article_item["create_date"] = tag_node.css("::text").extract_first().strip().replace("·", "").strip()
        tag_list = tag_node.css(' a::text').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        article_item["tags"] = ",".join(tag_list)
        article_item["thumb_up_num"] = int(response.css('span.vote-post-up h10::text').extract_first())
        fav_num = response.css('span.bookmark-btn::text').extract_first()
        match_obj = re.match(".*?(\d+).*", fav_num)
        if match_obj:
            fav_num = int(match_obj.group(1))
        else:
            fav_num = 0
        article_item["fav_num"] = fav_num

        comment_num = response.css('a[href="#article-comment"] span::text').extract_first("")
        match_obj = re.match(".*?(\d+).*", comment_num)
        if match_obj:
            comment_num = int(match_obj.group(1))
        else:
            comment_num = 0
        article_item["comment_num"] = comment_num
        article_item["content"] = response.css('div.entry').extract_first()

        yield article_item