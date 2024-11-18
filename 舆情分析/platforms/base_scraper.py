import time
import random
from urllib.request import Request

class BaseScraper:
    def __init__(self, opener, headers):
        self.opener = opener
        self.base_headers = headers
        
    def _make_request(self, url, extra_headers=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
            **self.base_headers
        }
        
        if extra_headers:
            headers.update(extra_headers)
            
        # 随机延时0.5-2秒
        time.sleep(random.uniform(0.5, 2))
        
        request = Request(url, headers=headers)
        return self.opener.open(request)