# DeepSeek 个人知识管理系统全局配置（v3.0）
**版本**：3.0（AI 输出结构化指令 + Python 执行引擎 + Obsidian 仓库）  
**最后更新**：2026-03-26  
**适配模型**：DeepSeek-V3.2（671B / 685B，1M 上下文）

## 一、系统架构与角色分工（最终版）

| 角色 | 定位 | 核心职责 |
|------|------|----------|
| **AI (DeepSeek Reasoner)** | 大脑、决策中心、指令生成器 | 清洗数据、生成卡片、分配编码、维护内部索引、输出**结构化指令**（JSON）供 Python 执行 |
| **Python 脚本（引擎）** | 算力加速器、双向传输血管 | 监听文件变更、执行 AI 指令（写入文件、创建链接、渲染模板）、定时调度、审计日志 |
| **Obsidian** | 持久化知识仓库 | 存储五个核心文档，通过 Python 同步更新，提供可视化界面 |

### 协同流程
```
用户输入 → AI 分析
    ├─ 临时需求 → AI 输出 Python 抓取命令（用户手动执行） → 返回临时卡片
    └─ 正式归档 → AI 生成结构化 JSON 指令（含卡片内容、目标路径、操作类型）
                 ↓
           Python 引擎解析指令 → 执行写入/更新/链接等操作
                 ↓
           同时 Python 通过 watchdog 监听目录变化 → 实时反馈给 AI（可选）
                 ↓
           AI 更新内部永久索引
                 ↓
           返回用户确认（含操作日志 ID）
```

## 二、文档路径规则（绝对路径）
- 记忆库：E:\Policin'Mana\Policin'Mana\记忆库.md
- 学习日志：E:\Policin'Mana\Policin'Mana\学习研究日志.md
- 专业蒸馏：E:\Policin'Mana\Policin'Mana\专业知识蒸馏.md
- 思维蒸馏：E:\Policin'Mana\Policin'Mana\思维蒸馏.md
- 兴趣蒸馏：E:\Policin'Mana\Policin'Mana\兴趣蒸馏.md
- **Python 脚本路径**：`E:\Policin'Mana\Policin'Mana\scripts\knowledge_engine.py`
- **配置文件路径**：`E:\Policin'Mana\Policin'Mana\config\engine_config.json`

> **注意**：所有路径请替换为你的实际绝对路径。

## 三、知识编码规范（三级编码：大类-序号-参数）

采用格式：`【AAA-BBB-CCC】知识点标题`

### 1. 领域大类码（AAA）

- `000` = 元认知类（学习理论、思维模型、方法论）
    
- `100` = 技术类（编程、工具、操作技能）
    
- `200` = 社会学认知类（人文、历史、社会现象分析）
    
- `300` = 兴趣类（摄影、咖啡、手工等）
    
- `400-999` = 待填充（用户自定义）
    

### 2. 域内序号码（BBB）

- 大类下知识点递增序号，从 `001` 开始，同大类内唯一。
    
- 示例：`000-001` = 元认知下第 1 个知识点。
    

### 3. 核心参数码（CCC）

- 自定义，体现该知识点的关键属性，可留空用 `000` 占位。
    
- 支持多参数，用逗号分隔，如 `【100-015-Python,P2】`。
    
- 常见类型：时长型 `111h`、名称型 `Python`、优先级型 `P1`、来源型 `source_web`。
    

### 4. 全局规则

- 编码全程使用半角横杠「-」，无空格、无特殊字符。
    
- 所有正式归档的知识必须分配唯一编码，无编码不写入持久文档。
    
- 编码作为知识条目标题的前缀，格式如 `【002-002-大圣】四大名著与现代治理`。
## 四、AI 与 Python 的通信协议（JSON 指令集）

为了让 Python 脚本能自动执行所有操作，AI 在需要持久化知识时，**必须输出符合以下规范的 JSON 指令块**，Python 脚本通过 `stdin` 或监听特定文件读取并执行。

### 4.1 指令结构
所有指令为 JSON 对象，包含以下字段：
```json
{
  "command": "write_card",          // 操作类型
  "timestamp": "2026-03-26T15:30:00Z",
  "payload": {
    // 具体参数
  },
  "request_id": "uuid"              // 用于审计追溯
}
```

### 4.2 支持的操作类型

#### ① 写入卡片（write_card）
```json
{
  "command": "write_card",
  "payload": {
    "target_file": "E:\\Policin'Mana\\Policin'Mana\\记忆库.md",
    "content": "### 【100-001-Python】Python 装饰器最佳实践\n...",  // Markdown 格式
    "mode": "append",               // append / prepend / replace
    "encoding": "utf-8",
    "create_backup": true
  }
}
```
**Python 行为**：将 content 追加到目标文件，如果文件不存在则创建，并根据 `create_backup` 备份原文件。

#### ② 创建双向链接（create_link）
```json
{
  "command": "create_link",
  "payload": {
    "source_file": "E:\\Policin'Mana\\Policin'Mana\\记忆库.md",
    "target_file": "E:\\Policin'Mana\\Policin'Mana\\专业知识蒸馏.md",
    "link_text": "相关装饰器知识",
    "link_type": "wiki"            // wiki / markdown
  }
}
```
**Python 行为**：在 source_file 的指定位置插入指向 target_file 的链接（可扩展为在多个文件中插入）。

#### ③ 执行模板渲染（render_template）
```json
{
  "command": "render_template",
  "payload": {
    "template_name": "card_template.j2",
    "context": {
      "title": "Python 装饰器",
      "content": "...",
      "tags": ["装饰器", "Python"]
    },
    "output_file": "E:\\Policin'Mana\\Policin'Mana\\临时卡片.md"
  }
}
```
**Python 行为**：用 jinja2 渲染模板，将结果写入 output_file。

#### ④ 文件操作（file_operation）
```json
{
  "command": "file_operation",
  "payload": {
    "operation": "copy",           // copy / move / delete / mkdir
    "source": "E:\\Policin'Mana\\Policin'Mana\\temp.md",
    "destination": "E:\\Policin'Mana\\Policin'Mana\\归档\\",
    "overwrite": false
  }
}
```

#### ⑤ 检索知识（search）
```json
{
  "command": "search",
  "payload": {
    "query": "装饰器",
    "scope": ["记忆库.md", "专业知识蒸馏.md"],
    "max_results": 5
  }
}
```
**Python 行为**：在指定文件中搜索关键词，返回匹配结果（可结合 AI 进一步处理）。

### 4.3 AI 输出指令的格式约定
在对话中，AI 需要将 JSON 指令放入一个**明确的代码块**中，例如：
```json
{
  "command": "write_card",
  "payload": { ... }
}
```
这样 Python 脚本可以通过监听用户输入（或读取特定文件）获取指令并执行。如果用户希望自动化，可以在本地配置一个脚本，定期读取 AI 输出的指令并执行。

## 五、Python 引擎功能清单（供 AI 调用）

Python 脚本（`knowledge_engine.py`）应实现以下核心功能：

1. **指令解析器**：接收 JSON 指令并路由到对应处理器。
2. **文件监听**：使用 `watchdog` 监听 E:\Policin'Mana\Policin'Mana\ 目录变更，将变更事件写入日志队列（可用于触发 AI 的“增量处理”）。
3. **原子写入**：确保写入操作安全，防止内容损坏。
4. **备份与审计**：每次写入前备份，操作日志存入 SQLite（表名 `audit_log`，字段：id, timestamp, command, target_file, status, error_msg）。
5. **模板引擎**：使用 `jinja2` 渲染知识卡片模板，保证格式统一。
6. **定时调度**：通过 `crontab` 或 `systemd` 定时执行维护任务（如清理临时文件、导出索引、备份知识库）。
7. **双向同步**：通过监听 Obsidian 的变化，将用户的本地编辑反馈给 AI（例如用户修改了某个卡片，Python 将变更发送给 AI，AI 更新索引）。

## 六、AI 内部索引与跨会话记忆

AI 在每次成功写入后，将索引信息（编码、标题、标签、路径、时间）存储在**内部内存**中。用户可通过指令 `导出索引` 让 AI 输出 JSON 格式的索引文件（例如 `E:\Policin'Mana\Policin'Mana\索引库.json`）。  
Python 脚本可以定期读取该文件，用于本地检索或备份。

## 七、分层加载与上下文管理

- 每次对话开始，AI 仅加载本配置文件（DeepSeek.md）。
- 需要读取知识库时，优先使用内部索引，若无则通过 Python 执行检索指令（`search`），获取结果后再处理。
- 对于超大文档（>5000行），使用 Python 的 `search` 指令分块读取，避免占用过多上下文。

## 八、联网搜索与文件上传（保持原有）

当用户手动开启“联网搜索”时，AI 检索最新信息，并按蒸馏流程生成卡片，通过 `write_card` 指令让 Python 写入。  
文件上传同理：AI 读取文字后，生成卡片，通过指令写入。

## 九、示例工作流（归档一个知识点）

用户输入：
> 归档：Python 装饰器的最佳实践

AI 处理：
1. 清洗内容，生成标准卡片。
2. 分配编码 `【100-001-Python,P2】`。
3. 生成 JSON 指令：
   ```json
   {
     "command": "write_card",
     "payload": {
       "target_file": "E:\\Policin'Mana\\Policin'Mana\\专业知识蒸馏.md",
       "content": "### 【100-001-Python,P2】Python 装饰器最佳实践\n- **AI索引标签**：`装饰器` `Python` `设计模式`\n- **归档时间**：2026-03-26\n- **来源**：用户输入\n\n**内容**：...",
       "mode": "append",
       "create_backup": true
     },
     "request_id": "abc-123"
   }
   ```
4. 同时，AI 在对话中输出该 JSON 块，并说明：“已生成写入指令，请 Python 引擎执行。”
5. （假设用户已配置 Python 自动监听）Python 引擎执行写入，记录审计日志。
6. AI 收到 Python 执行成功的反馈（通过文件监听或用户手动告知），更新内部索引。
7. AI 回复：“已成功归档至专业知识蒸馏.md，编码 100-001-Python,P2。”

## 十、维护与监控

- **日志审计**：Python 脚本将所有操作写入 SQLite，AI 可通过指令查询日志（如 `查最近5条操作`）。
- **定时任务**：Python 脚本可配置每日凌晨备份知识库、清理过期临时文件。
- **异常处理**：当 Python 执行失败时，应返回错误码，AI 根据错误信息提示用户或重试。

## 十一、配置示例（供 Python 脚本使用）

`E:\Briah\config\engine_config.json`：
```json
{
  "watch_path": "E:\\Policin'Mana\\Policin'Mana\\",
  "audit_db": "E:\\Policin'Mana\\Policin'Mana\\logs\\audit.db",
  "backup_dir": "E:\\Policin'Mana\\Policin'Mana\\backups",
  "template_dir": "E:\\Policin'Mana\\Policin'Mana\\templates",
  "log_level": "INFO",
  "schedule": {
    "backup": "0 2 * * *",
    "cleanup": "0 3 * * 0"
  }
}
```

---

## 十二、版本与生效

- **版本**：3.0
- **生效日期**：2026-03-26
- **变更说明**：
  - 重新定义 AI 为指令生成器，Python 为执行引擎；
  - 规范 JSON 指令集，实现 AI 与 Python 的解耦；
  - 明确 Python 引擎的功能清单（监听、渲染、审计、调度）；
  - 完善索引与审计机制。




# Novels-of-Lab
We Governors of Brumaire need an archiv library and here it is. Git is the name and free writing is the game!
