# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5
from ArticleSpider.items import ArticleItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 解析全部文章页面，获取文章url，然后交给parse_article_page处理
        2. 获取下一页url，交给scrapy下载，在进行重复回调
        :param response:
        :return:
        """
        url_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for node in url_nodes:
            article_url = node.css('::attr("href")').extract_first("")
            cover_image_url = node.css('img::attr("src")').extract_first("")
            yield Request(url=parse.urljoin(response.url, article_url), meta={"cover_url": cover_image_url}, callback=self.parse_article_page)

        next_url = response.css('a.next.page-numbers::attr("href")').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    @staticmethod
    def parse_article_page(response):
        """
        通过ItemLoader获取文章页面信息
        :param response:
        :return:
        """
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('thumb_up_num', 'span.vote-post-up h10::text')
        item_loader.add_css('fav_num', 'span.bookmark-btn::text')
        item_loader.add_css('comment_num', 'a[href="#article-comment"] span::text')
        item_loader.add_css('content', 'div.entry')
        item_loader.add_value('page_url', response.url)
        item_loader.add_value('page_url_id', get_md5(response.url))
        item_loader.add_value('cover_url', [response.meta.get("cover_url", "")])

        article_item = item_loader.load_item()

        yield article_item
