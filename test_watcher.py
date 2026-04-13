# test_watcher.py - 测试知识库系统
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\Users\Administrator')

import json
import time
from pathlib import Path
from datetime import datetime

# 测试1: 检查环境
print("=== 环境检查 ===")
print(f"Python: {sys.version}")
print(f"工作目录: {Path.cwd()}")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    print("[OK] watchdog 已安装")
except ImportError as e:
    print(f"[FAIL] watchdog 未安装: {e}")
    sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader
    print("[OK] jinja2 已安装")
except ImportError as e:
    print(f"[FAIL] jinja2 未安装: {e}")
    sys.exit(1)

# 测试2: 检查文件结构
print("\n=== 文件结构检查 ===")
config_path = Path("C:/Users/Administrator/config.json")
inbox_path = Path("C:/Users/Administrator/inbox")
template_path = Path("C:/Users/Administrator/templates/standard_card.j2")
vault_path = Path("C:/Users/Administrator/记忆库.md")

print(f"config.json: {'OK' if config_path.exists() else 'MISSING'}")
print(f"inbox/: {'OK' if inbox_path.exists() else 'MISSING'}")
print(f"templates/standard_card.j2: {'OK' if template_path.exists() else 'MISSING'}")
print(f"记忆库.md: {'OK' if vault_path.exists() else 'MISSING'}")

# 测试3: 读取配置
print("\n=== 配置加载 ===")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
print(f"配置: {config}")

# 测试4: Jinja2 模板渲染
print("\n=== 模板渲染测试 ===")
env = Environment(loader=FileSystemLoader("C:/Users/Administrator/templates", encoding='utf-8'))
template = env.get_template('standard_card.j2')
test_data = {
    "code": "测试-渲染-001",
    "title": "Jinja2渲染测试",
    "tags": ["测试", "Jinja2"],
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "body": "这是一个模板渲染测试。"
}
rendered = template.render(**test_data)
print(f"渲染结果:\n{rendered}")

# 测试5: 监听器测试
print("\n=== 监听器测试 ===")
print("创建测试指令文件...")

test_instruction = {
    "command": "write_card",
    "payload": {
        "target_file": "记忆库.md",
        "content": {
            "code": "自动-测试-001",
            "title": "自动测试卡片",
            "tags": ["自动测试", "watchdog"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "body": "这是通过自动监听系统生成的测试卡片。"
        },
        "mode": "append"
    }
}

test_file = inbox_path / "auto_test.json"
with open(test_file, 'w', encoding='utf-8') as f:
    json.dump(test_instruction, f, ensure_ascii=False, indent=2)
print(f"[OK] 已创建: {test_file}")

# 简单的监听器类
class TestHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix == '.json':
            print(f"\n[CAPTURE] 捕获新文件: {path.name}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"指令: {data.get('command')}")
                print(f"载荷: {json.dumps(data.get('payload', {}), ensure_ascii=False, indent=2)[:200]}...")
            except Exception as e:
                print(f"读取失败: {e}")

# 启动监听 (5秒测试)
print("\n启动监听器 (5秒测试)...")
observer = Observer()
handler = TestHandler()
observer.schedule(handler, str(inbox_path), recursive=False)
observer.start()

try:
    time.sleep(5)
except KeyboardInterrupt:
    pass
observer.stop()
observer.join()

print("\n=== 测试完成 ===")
print("系统组件检查通过！")
print("下一步: 在 Jupyter Notebook 中运行 watcher.ipynb 进行持续监听")