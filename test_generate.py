# 测试脚本
import sys
import json
sys.path.insert(0, r'F:\雾月督政府\上层')
from ai_knowledge_client_v2 import AIKnowledgeClient

client = AIKnowledgeClient()

# 读取 linuxdo.md
source = client.read_source_file('linuxdo.md')
print('源文件长度:', len(source) if source else '未找到')

# 生成卡片
topic = 'Linux.do 社区入门指南'
card = client.generate_card(topic, source[:5000])
print('生成结果:', json.dumps(card, ensure_ascii=False, indent=2)[:500])
print('---')
print('Code:', card.get('payload', {}).get('content', {}).get('code', 'N/A'))
print('Title:', card.get('payload', {}).get('content', {}).get('title', 'N/A'))

# 发送到 inbox
filepath = client.send_to_inbox(card)
print('已发送到:', filepath)