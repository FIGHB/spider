import requests
import re
import os
from loguru import logger

"""第二书包网单本书爬虫"""

url_prefix = 'https://m.diershubao.com'
# 设置一个变量，该变量为指定保存的路径,windows系统下的D盘，test目录
target_folder = 'C:\\Users\\msi-pc\\Documents\\novel\\'
# 判断D盘下是否存在test目录，如果不存在该目录，则创建test目录
class NovelSpider:
    """spider nover"""
    def __init__(self):
        # download tools
        self.session = requests.Session()
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)


    """外界调用此函数传入所需下载书籍的url即可下载"""
    def get_novel(self, pageUrl):
        while(pageUrl != ''):
            # 根据第一页内容，循环遍历各页
            content_index_html = self.download_html(pageUrl, encoding = 'gbk')
            pageUrl = ''
            self.get_novel_content(content_index_html)
            nextPageUrl = re.findall(r'<span class="right"><a href="(.*?)" class="onclick">下一页</a></span>', content_index_html)
            if(len(nextPageUrl) > 0):
                pageUrl = url_prefix + nextPageUrl[0]
                logger.info('下页目录索引:', pageUrl)

    # 下载小说内容，并保存
    def get_novel_content(self, index_html):
        # index_html = self.download_html(url, encoding = 'gbk')
        novel_chapter_infos = self.get_novel_chapter_infos(index_html)
        # 获取小说名称
        novel_name = self.get_novel_name(index_html)
        fb = open(target_folder + '%s.txt' %novel_name, mode = 'a')
        """循环下载章节"""
        for chapter_info in novel_chapter_infos:
            # 下载各章内容
            chapter_url = url_prefix + chapter_info[0]
            chapter_title = chapter_info[1]
            logger.info(chapter_title)
            fb.write('%s\n' %chapter_title)
            self.download_whole_chapter(chapter_url, fb)
        fb.close()

    def download_whole_chapter(self, pageUrl, fb):
        while(pageUrl != ''):
            # 下载本章各页内容内容
            chapterHtmlText = self.download_html(pageUrl, encoding = 'gbk')
            # 获取下一页url
            nextUrl = re.findall(r'<li><a href="(.*?)" class="p4">下一页</a></li>', chapterHtmlText)
            pageUrl = ''
            if(len(nextUrl) > 0):
                pageUrl = url_prefix + nextUrl[0]
            # 数据清洗
            chapter_content = '\n' + self.clean_chapter_content(chapterHtmlText)
            # 及时写入每页数据
            fb.write('%s\n'%chapter_content)

    # 清洗各章内容
    def clean_chapter_content(self, chapter_content):
        content = re.findall(r'<div id="novelcontent" class="novelcontent">\n\t\t\t(.*?)\t\t</div>', chapter_content, re.S)[0]
        content = content.replace('&nbsp', '')
        regexOne = re.compile('\(.*\)|\（.*）|<.*?>|<|>|;|；|\\ufffd')
        content = regexOne.sub('', content)
        content = content.replace('<br/>', '')
        # 替换 windows 下的换行符
        content = content.replace('\r\n', '')
        return content

    # 从 html文本中提取小说名字
    def get_novel_name(self, html):
        novel_name = re.findall(r'<title>(.*?)</title>', html)[0]
        return novel_name

    # 根据 url 下载对应资源并返回 html 文本
    def download_html(self, url, encoding):
        response = self.session.get(url)
        response.encoding = encoding
        html = response.text
        return html

    # 获取章节目录及各章 url 后缀
    def get_novel_chapter_infos(self, html):
        info = re.findall(r'<p class="p1">全部章节 .*? </p>(.*?)<div class="listpage">', html, re.S)[0]
        info = re.findall(r'<li><a href="(.*?)">(.*?)</a></li>', info)
        return info



"""实例化类对象"""
if __name__ == '__main__':
    novel_url = 'https://m.diershubao.com/0_1/'
    spider = NovelSpider() # 实例化对象
    spider.get_novel(novel_url)
