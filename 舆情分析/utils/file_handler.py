from datetime import datetime

class FileHandler:
    @staticmethod
    def save_results(keyword, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_results_{keyword}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"搜索关键词: {keyword}\n")
            f.write(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for platform, content in results.items():
                f.write(f"\n=== {platform} ===\n")
                for item in content:
                    f.write(f"\n时间: {item['time']}\n")
                    f.write(f"标题: {item['title']}\n")
                    if platform == "哔哩哔哩":
                        f.write(f"作者: {item['author']}\n")
                        f.write(f"BV号: {item['bvid']}\n")
                        f.write(f"时长: {item['duration']}\n")
                        f.write(f"播放量: {item['view_count']}\n")
                    f.write(f"内容: {item['content']}\n")
                    
                    if item['comments']:
                        f.write("\n评论:\n")
                        for comment in item['comments']:
                            if platform == "哔哩哔哩":
                                f.write(f"  - {comment['time']} | {comment['author']} (👍{comment['likes']}): {comment['content']}\n")
                            else:
                                f.write(f"  - {comment['time']} | {comment['author']}: {comment['content']}\n")
                    
                    f.write("-" * 50 + "\n")