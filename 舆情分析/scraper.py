import urllib.request
from http.cookiejar import CookieJar
import random
from platforms.bilibili import BilibiliScraper
from platforms.zhihu import ZhihuScraper
from utils.file_handler import FileHandler

class SocialMediaScraper:
    def __init__(self):
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.opener._cookies = self.cookie_jar  # 添加这行来修复cookie访问问题
        
        # 随机生成一个User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        self.headers = {
            'User-Agent': random.choice(user_agents)
        }
        
        # Initialize platform scrapers
        self.bilibili = BilibiliScraper(self.opener, self.headers)
        self.zhihu = ZhihuScraper(self.opener, self.headers)
        self.file_handler = FileHandler()

    def search_all_platforms(self, keyword):
        results = {
            "哔哩哔哩": self.bilibili.search(keyword),
            "知乎": self.zhihu.search(keyword)
        }
        
        self.file_handler.save_results(keyword, results)
        print(f"搜索完成，结果已保存到文件中。")

def main():
    keyword = input("请输入搜索关键词: ")
    scraper = SocialMediaScraper()
    scraper.search_all_platforms(keyword)

if __name__ == "__main__":
    main()