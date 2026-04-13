# watcher_service.py - 知识库监听服务
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Environment, FileSystemLoader
import shutil
import logging

# 配置
CONFIG_PATH = Path(r"F:\雾月督政府\上层\config.json")

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

CONFIG["vault_path"] = Path(CONFIG["vault_path"])
CONFIG["inbox_path"] = Path(CONFIG["inbox_path"])
CONFIG["template_dir"] = Path(CONFIG["template_dir"])

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG["vault_path"] / "watcher.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ObsidianSyncAgent(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.vault = Path(config['vault_path'])
        self.inbox = Path(config['inbox_path'])
        self.template_env = Environment(
            loader=FileSystemLoader(str(config['template_dir']), encoding='utf-8')
        )
        logging.info(f"监听启动: {self.inbox}")

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix != '.json':
            return
        if path.parent != self.inbox:
            return

        logging.info(f"捕获: {path.name}")
        time.sleep(0.3)  # 等待文件完全写入
        self.process_instruction(path)

    def process_instruction(self, json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"读取失败: {e}")
            return

        command = data.get('command')
        payload = data.get('payload', {})

        try:
            if command == 'write_card':
                self.execute_write_card(payload)
            else:
                logging.warning(f"未知指令: {command}")
                return

            self.archive_file(json_path)

        except Exception as e:
            logging.error(f"执行失败: {e}")

    def execute_write_card(self, payload):
        target_file = self.vault / payload['target_file']
        content = payload['content']
        mode = payload.get('mode', 'append')

        try:
            template = self.template_env.get_template('standard_card.j2')
            rendered = template.render(**content)
        except Exception as e:
            logging.error(f"模板渲染失败: {e}")
            return

        try:
            write_mode = 'a' if mode == 'append' else 'w'
            with open(target_file, write_mode, encoding='utf-8', newline='\n') as f:
                if mode == 'append' and target_file.exists() and target_file.stat().st_size > 0:
                    f.write("\n\n---\n\n")
                f.write(rendered)
            logging.info(f"写入成功: {target_file.name}")
        except Exception as e:
            logging.error(f"写入失败: {e}")

    def archive_file(self, file_path):
        processed = self.inbox / 'processed'
        processed.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_name = f"{timestamp}_{file_path.name}"
        try:
            shutil.move(str(file_path), str(processed / new_name))
            logging.info(f"已归档: {new_name}")
        except Exception as e:
            logging.error(f"归档失败: {e}")

def main():
    logging.info("=" * 50)
    logging.info("知识库监听服务启动")
    logging.info("=" * 50)

    handler = ObsidianSyncAgent(CONFIG)
    observer = Observer()
    observer.schedule(handler, str(CONFIG["inbox_path"]), recursive=False)
    observer.start()

    logging.info(f"监听中: {CONFIG['inbox_path']}")
    logging.info("按 Ctrl+C 停止")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("停止监听")

    observer.join()
    logging.info("服务已退出")

if __name__ == "__main__":
    main()