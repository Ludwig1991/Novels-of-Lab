# test_full_flow.py - 完整流程测试
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Environment, FileSystemLoader
import shutil

# 配置
CONFIG = {
    "vault_path": Path("C:/Users/Administrator"),
    "inbox_path": Path("C:/Users/Administrator/inbox"),
    "template_dir": Path("C:/Users/Administrator/templates")
}

class ObsidianSyncAgent(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.obsidian_vault = config['vault_path']
        self.inbox_path = config['inbox_path']
        self.template_env = Environment(
            loader=FileSystemLoader(str(config['template_dir']), encoding='utf-8')
        )
        print(f"[INIT] 监听目录: {self.inbox_path}")
        print(f"[INIT] 目标库: {self.obsidian_vault}")

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix == '.json' and path.parent == self.inbox_path:
            print(f"\n[CAPTURE] 捕获新指令: {path.name}")
            # 延迟一下让文件完全写入
            time.sleep(0.5)
            self.process_instruction(path)

    def process_instruction(self, json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] 读取失败: {e}")
            return

        command = data.get('command')
        payload = data.get('payload', {})

        try:
            if command == 'write_card':
                self.execute_write_card(payload)
            else:
                print(f"[WARN] 未知指令: {command}")
                return
            self.archive_file(json_path)
        except Exception as e:
            print(f"[ERROR] 执行失败: {e}")

    def execute_write_card(self, payload):
        target_file = self.obsidian_vault / payload['target_file']
        content_data = payload['content']
        mode = payload.get('mode', 'append')

        # 渲染模板
        try:
            template = self.template_env.get_template('standard_card.j2')
            rendered_content = template.render(**content_data)
        except Exception as e:
            print(f"[ERROR] 模板渲染失败: {e}")
            return

        # 写入文件
        write_mode = 'a' if mode == 'append' else 'w'
        try:
            with open(target_file, write_mode, encoding='utf-8', newline='\n') as f:
                if mode == 'append' and target_file.exists() and target_file.stat().st_size > 0:
                    f.write("\n\n---\n\n")
                f.write(rendered_content)
            print(f"[OK] 写入成功: {target_file}")
            print(f"[OK] 内容预览:\n{rendered_content[:300]}...")
        except Exception as e:
            print(f"[ERROR] 写入失败: {e}")

    def archive_file(self, file_path):
        processed_dir = self.inbox_path / 'processed'
        processed_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_name = f"{timestamp}_{file_path.name}"
        try:
            shutil.move(str(file_path), str(processed_dir / new_name))
            print(f"[OK] 已归档: {new_name}")
        except Exception as e:
            print(f"[ERROR] 归档失败: {e}")

def main():
    print("=== 知识库系统完整测试 ===\n")

    # 启动监听器
    print("启动监听器...\n")
    handler = ObsidianSyncAgent(CONFIG)
    observer = Observer()
    observer.schedule(handler, str(CONFIG['inbox_path']), recursive=False)
    observer.start()

    # 延迟创建测试指令（监听器启动后）
    def create_test_file():
        time.sleep(1)  # 等待监听器完全启动

        test_instruction = {
            "command": "write_card",
            "payload": {
                "target_file": "记忆库.md",
                "content": {
                    "code": "自动-测试-001",
                    "title": "知识库自动写入测试",
                    "tags": ["自动化", "watchdog", "测试"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "body": "这是通过 Watchdog + Jinja2 自动监听写入的测试卡片。系统运行正常！"
                },
                "mode": "append"
            }
        }

        test_file = CONFIG['inbox_path'] / "write_test_final.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_instruction, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 创建测试指令: {test_file}")

    # 在后台线程创建文件
    creator = threading.Thread(target=create_test_file)
    creator.start()

    # 等待处理
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        pass

    observer.stop()
    observer.join()

    print("\n=== 测试完成 ===")
    print("检查记忆库.md 确认卡片已写入")

if __name__ == "__main__":
    main()