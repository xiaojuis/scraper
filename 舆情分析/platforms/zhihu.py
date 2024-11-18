import urllib.parse
import json
import gzip
import time
import hashlib
import hmac
from datetime import datetime
from .base_scraper import BaseScraper

class ZhihuScraper(BaseScraper):
    def __init__(self, opener, headers):
        super().__init__(opener, headers)
        self.d_c0 = None
        self._init_session()
        
    def _init_session(self):
        """初始化知乎session，获取必要的cookies"""
        try:
            # 首先访问首页获取初始cookies
            self._make_request('https://www.zhihu.com/')
            
            # 获取x-zse-96所需的d_c0
            for cookie in self.opener._cookies.values():
                for cookie_domain in cookie.values():
                    for cookie_name in cookie_domain.values():
                        if cookie_name.name == 'd_c0':
                            self.d_c0 = cookie_name.value
                            return
                        
            if not self.d_c0:
                print("Warning: d_c0 cookie not found")
                self.d_c0 = "default_dc0_value"  # 使用默认值
                
        except Exception as e:
            print(f"Error initializing Zhihu session: {e}")
            self.d_c0 = "default_dc0_value"  # 出错时使用默认值
    
    def _get_x_zse_96(self, url):
        """生成x-zse-96参数"""
        if not self.d_c0:
            self._init_session()
            
        x_zse_93 = "101_3_2.0"
        md5 = hashlib.md5()
        md5.update(f'{x_zse_93}+{self.d_c0}+{urllib.parse.urlparse(url).path}'.encode())
        hex_digest = md5.hexdigest()
        return "2.0_" + hex_digest
        
    def search(self, keyword):
        encoded_keyword = urllib.parse.quote(keyword)
        url = f'https://www.zhihu.com/api/v4/search_v3?t=general&q={encoded_keyword}&correction=1&offset=0&limit=20&filter_fields=&lc_idx=0&show_all_topics=0'
        
        try:
            x_zse_96 = self._get_x_zse_96(url)
            extra_headers = {
                'Host': 'www.zhihu.com',
                'Origin': 'https://www.zhihu.com',
                'Referer': f'https://www.zhihu.com/search?type=content&q={encoded_keyword}',
                'x-api-version': '3.0.91',
                'x-app-za': 'OS=Web',
                'x-zse-93': '101_3_2.0',
                'x-zse-96': x_zse_96,
                'x-requested-with': 'fetch'
            }
            
            response = self._make_request(url, extra_headers)
            data = response.read()
            
            if response.info().get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
                
            return self._process_search_results(json.loads(data.decode('utf-8')))
        except Exception as e:
            print(f"Error searching Zhihu: {e}")
            return []

    def get_comments(self, answer_id):
        url = f'https://www.zhihu.com/api/v4/answers/{answer_id}/root_comments?order=normal&limit=20&offset=0&status=open'
        try:
            x_zse_96 = self._get_x_zse_96(url)
            extra_headers = {
                'Host': 'www.zhihu.com',
                'Origin': 'https://www.zhihu.com',
                'Referer': f'https://www.zhihu.com/question/{answer_id}',
                'x-api-version': '3.0.91',
                'x-zse-93': '101_3_2.0',
                'x-zse-96': x_zse_96
            }
            
            response = self._make_request(url, extra_headers)
            data = response.read()
            
            if response.info().get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
                
            return self._process_comments(json.loads(data.decode('utf-8')))
        except Exception as e:
            print(f"Error fetching Zhihu comments: {e}")
            return []

    def _process_search_results(self, data):
        results = []
        for item in data.get('data', []):
            if item.get('type') == 'answer':
                object_data = item.get('object', {})
                answer_id = object_data.get('id', '')
                results.append({
                    'id': answer_id,
                    'time': datetime.fromtimestamp(object_data.get('created_time', 0)).strftime("%Y-%m-%d %H:%M:%S"),
                    'title': object_data.get('question', {}).get('title', ''),
                    'content': object_data.get('excerpt', ''),
                    'comments': self.get_comments(answer_id) if answer_id else []
                })
        return results

    def _process_comments(self, data):
        comments = []
        for comment in data.get('data', []):
            comments.append({
                'time': datetime.fromtimestamp(comment.get('created_time', 0)).strftime("%Y-%m-%d %H:%M:%S"),
                'content': comment.get('content', ''),
                'author': comment.get('author', {}).get('member', {}).get('name', '')
            })
        return comments