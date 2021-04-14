from scrapy.http import Request
from urllib import parse
from scrapy_redis.spiders import RedisSpider


class CnblogsSpider(RedisSpider):
    name = 'cnblogs'
    allowed_domains = ["https://www.cnblogs.com/"]
    redis_key = 'cnblogs:start_urls'

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url, dont_filter=False)

    """
    如果是要使用布隆过滤器，那就要dont_filter=False,就是要过滤！！！才会使用布隆过滤器，
    这里是重载了这个方法make_request_from_data，使用第一个url的dont_filter=False,但我们不应该第一个url就设置了过滤
    因为第一个过滤那就没有后面的url了，所以只有从第2个url才设置过滤
    """
    def make_request_from_data(self, data):
        req = super().make_request_from_data(data)
        req.dont_filter = False
        return req

    def parse(self, response):

        """
        1. 获取文章列表中的文章url并交给scrapy下载并进行解析
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse


        :param response:
        :return:
        """
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        post_nodes = response.css('.post-item .post-item-text') # 是id就用#,是class就用.,这是获取页面的所有链接
        for post_node in post_nodes:  # 一个一个解析出来
            image_url = post_node.css('.post-item-text .post-item-summary img::attr(src)').extract_first("")  # 解析出图片url
            post_url = post_node.css('.post-item-text a::attr(href)').extract_first("")  # 解析出文章的url
            # dont_filter=True翻译过来是不要过滤掉，这样在调试到scheduler中的pop的时候，就还没过滤掉
            # 如果是要使用布隆过滤器，那就要dont_filter=False,就是要过滤！！！才会使用布隆过滤器，
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail, dont_filter=False)


        # 提取下一页并交给scrapy进行下载
        # next_url = response.css('div.pager a:last-child::text').extract_first("")
        # if next_url == ">":
        #     next_url = response.css('div.pager a:last-child::attr(href)').extract_first("")
        #     # dont_filter=True翻译过来是不要过滤掉，这样在调试到scheduler中的pop的时候，就还没过滤掉
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        pass


