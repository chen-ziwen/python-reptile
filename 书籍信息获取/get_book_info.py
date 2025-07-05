import os
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# 目标网站：http://books.toscrape.com
# 目标：爬取所有书籍信息

class BookScraper(object):

    def __init__(self, page=50):
        self.keep_path = os.path.join(os.getcwd(), "book.txt")
        self.base_url = "http://books.toscrape.com/"
        self.delay = 1  # 每页抓取的间隔时间
        self.page = page  # 想要抓取的页数
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }

    def get_page_data(self, url):
        """ 安全获取页面数据 """
        try:
            # 分页延迟获取 避免风控
            time.sleep(self.delay)
            content = requests.get(url, headers=self.headers).text
            return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f"抓取页面失败：{url}-错误：{e}")
            return None

    def parse_book(self, article):
        """ 解析单页图书数据 """
        book_img = article.find("img", attrs={"class": "thumbnail"})
        book_title = article.select_one("h3 a")
        book_price = article.find("p", attrs={"class", "price_color"})

        return {
            "书名": book_title.string if book_title else "无标题",
            "封面": urljoin(self.base_url, book_img["src"]),
            "价格": book_price.string[2:] if book_price else "无价格"
        }

    def get_all_books(self):
        """ 获取所有分页的图书数据 """
        all_book = []
        # 默认第一页
        page_url = urljoin(self.base_url, "catalogue/page-1.html")
        page_count = 1

        while True:
            print(f"正在抓取第 {page_count} 页...")

            soup = self.get_page_data(page_url)

            if not soup:
                break

            # 获取一页中的全部图书
            articles = soup.find_all("article", {"class": "product_pod"})
            for article in articles:
                all_book.append(self.parse_book(article))

            # 查找下一页
            next_btn = soup.select_one("li.next > a")

            if not next_btn:
                break

            page_url = urljoin(page_url, next_btn['href'])
            page_count += 1

            # 防止无限执行
            if page_count > self.page:
                break

        return all_book

    def save_book(self, books):
        """ 格式化保存数据 """
        with open(self.keep_path, "w", encoding="utf-8") as f:
            for idx, book in enumerate(books):
                f.write(
                    f"第{idx + 1}条记录：\n"
                    f"书名：{book['书名']}\n"
                    f"封面：{book['封面']}\n"
                    f"价格：{book['价格']}\n"
                    f"{'-' * 50}\n"
                )
        print(f"总共抓取 {len(books)} 本书，已保存到 {self.keep_path}")


if __name__ == "__main__":
    # 实例化爬虫
    scraper = BookScraper(100)  # 实际网站只有 50 页
    # 获取全部的书
    books_data = scraper.get_all_books()
    # 将书本信息保存到 txt
    scraper.save_book(books_data)
