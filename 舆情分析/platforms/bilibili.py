import urllib.parse
import json
import gzip
import random
from datetime import datetime
from .base_scraper import BaseScraper

class BilibiliScraper(BaseScraper):
    def __init__(self, opener, headers):
        super().__init__(opener, headers)
        self._init_session()
        
    def _init_session(self):
        """初始化B站session，获取必要的cookies"""
        try:
            # 访问首页获取初始cookies
            self._make_request('https://www.bilibili.com/')
        except Exception as e:
            print(f"Error initializing Bilibili session: {e}")
    
    def search(self, keyword):
        encoded_keyword = urllib.parse.quote(keyword)
        # 使用更具体的搜索API
        url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={encoded_keyword}'
        
        try:
            # 生成随机的buvid3
            buvid3 = f"{''.join(random.choices('0123456789ABCDEF', k=32))}_{''.join(random.choices('0123456789', k=10))}"
            
            extra_headers = {
                'Host': 'api.bilibili.com',
                'Origin': 'https://search.bilibili.com',
                'Referer': f'https://search.bilibili.com/all?keyword={encoded_keyword}',
                'Cookie': f'buvid3={buvid3}; innersign=0'
            }
            
            response = self._make_request(url, extra_headers)
            data = response.read()
            
            if response.info().get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
                
            return self._process_search_results(json.loads(data.decode('utf-8')))
        except Exception as e:
            print(f"Error searching Bilibili: {e}")
            return []

    def get_comments(self, video_id):
        url = f'https://api.bilibili.com/x/v2/reply?type=1&oid={video_id}&sort=2&nohot=1'
        try:
            extra_headers = {
                'Host': 'api.bilibili.com',
                'Origin': 'https://www.bilibili.com',
                'Referer': f'https://www.bilibili.com/video/av{video_id}'
            }
            
            response = self._make_request(url, extra_headers)
            data = response.read()
            
            if response.info().get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
                
            return self._process_comments(json.loads(data.decode('utf-8')))
        except Exception as e:
            print(f"Error fetching Bilibili comments: {e}")
            return []

    def _process_search_results(self, data):
        results = []
        for item in data.get('data', {}).get('result', []):
            video_id = item.get('aid', '')  # 获取av号
            bvid = item.get('bvid', '')     # 获取bv号
            
            results.append({
                'id': video_id,
                'time': datetime.fromtimestamp(item.get('pubdate', 0)).strftime("%Y-%m-%d %H:%M:%S"),
                'title': item.get('title', ''),
                'content': item.get('description', ''),
                'author': item.get('author', ''),
                'bvid': bvid,
                'duration': item.get('duration', ''),
                'view_count': item.get('play', 0),
                'comments': self.get_comments(video_id) if video_id else []
            })
        return results

    def _process_comments(self, data):
        comments = []
        for reply in data.get('data', {}).get('replies', []):
            if reply:  # 确保评论数据存在
                comments.append({
                    'time': datetime.fromtimestamp(reply.get('ctime', 0)).strftime("%Y-%m-%d %H:%M:%S"),
                    'content': reply.get('content', {}).get('message', ''),
                    'author': reply.get('member', {}).get('uname', ''),
                    'likes': reply.get('like', 0)
                })
        return comments