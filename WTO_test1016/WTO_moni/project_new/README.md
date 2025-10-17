# WTO模拟谈判系统 - 完整技术文档

> 一个功能完整的WTO模拟谈判平台，支持主席管理和与会国参与的双角色体验，包含完整的会议流程管理、投票表决、动议讨论和**AI驱动的共同宣言生成**等功能。

**系统接口地址**: http://127.0.0.1:5000  
**版本**: v3.0  
**最后更新**: 2024-10-14

---

## 📑 目录

- [系统特性](#系统特性)
- [快速开始](#快速开始)
- [完整工作流程](#完整工作流程)
- [核心功能详解](#核心功能详解)
  - [投票机制](#投票机制详解)
  - [PDF提取与宣言生成](#pdf提取与共同宣言生成)
  - [函数位置标注](#关键函数位置标注)
- [故障排查](#故障排查指南)
- [API接口](#api接口)
- [项目结构](#项目结构)
- [常见问题](#常见问题)

---

## 🌟 系统特性

### 核心功能
- ✅ **会议管理**: 支持多会期管理，可设置委员会名称和议程
- ✅ **国家管理**: 包含200+国家的数据库，支持国旗显示
- ✅ **文件上传**: 支持批量上传PDF、DOC、DOCX格式文件
- ✅ **点名签到**: 实时点名功能，支持批量操作和统计
- ✅ **动议发言**: 主席选择发言顺序，逐一显示正在发言的国家
- ✅ **智能投票**: 对文件进行投票表决，自动判断通过
- ✅ **PDF文本提取**: 使用PyPDF2自动提取PDF文本内容
- ✅ **AI生成宣言**: 调用科大讯飞星火API生成专业共同宣言
- ✅ **PDF导出**: 支持将共同宣言导出为PDF文档

### 技术亮点
- 🚀 **AI驱动**: 集成科大讯飞星火3.5大模型
- 📄 **PDF智能处理**: PyPDF2自动提取文本，支持批量处理
- 🔄 **三层容错**: AI失败→本地算法→模板生成
- 💾 **混合存储**: 文件系统存储PDF + MongoDB存储元数据
- 📊 **详细日志**: emoji日志输出，方便调试
- 🎨 **现代UI**: 响应式设计，支持移动端访问

---

## 🚀 快速开始

### 环境要求
- Python 3.7+
- MongoDB 4.0+
- 8GB+ RAM（用于PDF文本提取）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd project_new
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

主要依赖：
```txt
Flask==2.3.3
pymongo==4.5.0
PyPDF2==3.0.1          # PDF文本提取
python-docx==0.8.11    # Word文档提取
jieba==0.42.1          # 中文分词
scikit-learn==1.3.0    # 文本相似度分析
websocket-client==1.6.4 # 星火API通信
```

3. **启动MongoDB**
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

4. **启动应用**
```bash
python run.py
```

5. **访问系统**
- 系统主页: http://127.0.0.1:5000
- 主席控制台: http://127.0.0.1:5000/chairman-selection
- 与会国门户: http://127.0.0.1:5000/country-portal

---

## 📋 完整工作流程

### 标准流程图

```
1. 会议设置
   ↓
2. 点名签到 → 确定到场国家
   ↓
3. 文件上传 → 各国上传PDF文件
   ↓
4. 投票表决 → 判断文件是否通过
   ↓ 【关键】主席点击"完成投票"
   ↓
5. 保存通过文件 → passed_files集合
   ↓
6. 生成共同宣言
   ├─ 读取passed_files
   ├─ 提取PDF文本 (PyPDF2)
   ├─ 调用星火API
   └─ 生成宣言
   ↓
7. 编辑与导出 → 保存/分享/导出PDF
```

### 详细步骤

#### 1. 会议设置
- 设置委员会名称和议程
- 选择参与国家
- 生成会议ID（5位数字）

#### 2. 点名签到
- 确定到场国家
- 只有到场的国家才能参与后续流程
- 完成点名后自动跳转到文件上传页面

#### 3. 文件上传
与会国上传文件：
- 支持PDF、Word文档
- 文件大小限制：10MB
- 存储位置：`/app/static/uploads/`
- 数据库存储：**文件名字符串**（不是完整内容）

#### 4. 投票表决
- 每个国家对每个文件投票（同意/反对/弃权）
- 主席监控投票进度
- **🔥 关键步骤**：主席点击"完成投票"按钮

#### 5. 保存通过文件
**判断规则**：同意票 > 反对票

**自动保存到两个地方**：
- `passed_files` 集合（专门用于宣言生成）
- `submissions` 集合（标记 `vote_passed: true`）

#### 6. 生成共同宣言
- 从 `passed_files` 读取通过的文件名
- 从文件系统读取PDF文件
- 使用PyPDF2提取文本
- 调用星火API生成宣言
- 失败则回退到本地算法

#### 7. 编辑与导出
- 在线编辑宣言
- 导出为PDF
- 分享给各国

---

## 🎯 核心功能详解

### 投票机制详解

#### 投票流程

1. **各国投票**
   - 与会国访问投票页面
   - 对分配的文件投票（同意/反对/弃权）
   - 投票保存到 `file_vote_details` 集合

2. **主席监控**
   - 访问投票监控页面
   - 实时查看投票进度
   - 所有国家投票完成后，点击"完成投票"

3. **🔥 完成投票按钮的作用**

**前端位置**：`chairman_vote_monitoring.html` 第696行
```html
<button class="btn btn-success" onclick="completeVoting()" id="complete-btn">
    完成投票
</button>
```

**前端函数**：第1163-1205行
```javascript
async function completeVoting() {
    const response = await fetch('/api/finalize_file_voting', {
        method: 'POST',
        body: JSON.stringify({
            session_id: sessionId,
            vote_matrix: voteMatrix,  // 所有投票数据
            completed_at: new Date().toISOString()
        })
    });
}
```

**后端API**：`run.py` 第917-1087行
```python
@app.route('/api/finalize_file_voting', methods=['POST'])
def api_finalize_file_voting():
    # 1. 统计每个文件的投票结果
    for country_id, country_votes in vote_matrix.items():
        for file_id, vote_result in country_votes.items():
            file_results[file_id][vote_result] += 1
    
    # 2. 判断文件是否通过
    for file_id, results in file_results.items():
        is_passed = results['agree'] > results['disagree']  # 🔥 判断逻辑
        
        if is_passed:
            # 3. 从submissions获取文件信息
            submission = cols["submissions"].find_one({...})
            file_name = submission.get("file_name")  # 获取文件名
            
            # 4. 保存到passed_files集合
            passed_file_record = {
                "session_id": session_id,
                "file_id": file_id,
                "file_name": file_name,  # ⭐ 存储文件名字符串
                "country_id": country_id,
                "vote_agree": results['agree'],
                "vote_disagree": results['disagree'],
                "status": "passed"
            }
            cols["db"]["passed_files"].update_one(...)
            
            # 5. 更新submissions集合
            cols["submissions"].update_one({
                "session_id": session_id,
                "country_id": country_id
            }, {
                "$set": {"vote_passed": True, ...}
            })
```

#### 数据库存储

**file_vote_details 集合**（投票记录）：
```json
{
  "session_id": "00037",
  "country_id": "中国",
  "file_id": "file_001",
  "vote_result": "agree",
  "voted_at": "2024-10-14T16:00:00Z"
}
```

**passed_files 集合**（通过的文件）：
```json
{
  "session_id": "00037",
  "file_id": "file_001",
  "file_name": "20241014153045_中国提案.pdf",  // ⭐ 文件名字符串
  "original_name": "中国提案.pdf",
  "country_id": "中国",
  "vote_agree": 15,
  "vote_disagree": 3,
  "vote_abstain": 2,
  "passed_at": "2024-10-14T16:00:00Z",
  "status": "passed"
}
```

**submissions 集合**（更新后）：
```json
{
  "country_id": "中国",
  "file_name": "20241014153045_中国提案.pdf",
  "vote_passed": true,     // ⭐ 标记为通过
  "vote_status": "passed",
  "vote_agree_count": 15,
  "vote_disagree_count": 3
}
```

---

### PDF提取与共同宣言生成

#### 完整工作流程

```
1. 前端调用 /api/generate_declaration
   ↓
2. 从passed_files读取文件名 (run.py:4020-4023)
   ↓
3. 从文件系统读取PDF (/app/static/uploads/xxx.pdf)
   ↓
4. 提取PDF文本 extract_text_from_pdf() (run.py:4692-4703)
   ↓ 使用PyPDF2.PdfReader
5. 清理文本 clean_text() (run.py:4740-4750)
   ↓
6. 构建countries_data (run.py:4114-4120)
   [{country: "中国", content: "PDF文本内容..."}]
   ↓
7. 调用大模型 call_llm_for_declaration() (run.py:4183)
   ├─ call_xf_yun_api() (run.py:4525-4622) ← 科大讯飞星火API
   ├─ 失败 → generate_similarity_based_declaration() ← 本地算法
   └─ 再失败 → generate_fallback_declaration() ← 模板
   ↓
8. 保存到数据库 cols["db"]["declarations"].insert_one()
   ↓
9. 返回给前端 return jsonify({declaration: "..."})
```

#### PDF文件的存储方式

| 存储位置 | 存储内容 | 数据类型 |
|---------|---------|---------|
| **文件系统** (`/app/static/uploads/`) | PDF完整二进制内容 | 实际文件 |
| **MongoDB** (`passed_files`) | 文件名字符串 | String |

**示例**：
- 文件系统：`20241014153045_中国提案.pdf`（实际PDF文件）
- 数据库：`"file_name": "20241014153045_中国提案.pdf"`（字符串）

#### PDF文本提取

**核心函数**：`run.py` 第4692-4703行
```python
def extract_text_from_pdf(file_path):
    """从PDF文件中提取文本"""
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)  # 使用PyPDF2
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
```

**使用的库**：`PyPDF2==3.0.1`

#### 星火API调用

**配置**：`run.py` 第4531-4533行
```python
APPID = "c9bf2623"
APIKey = "14316b191bfd90e97397ac40d251dae4"
APISecret = "NTEwOTYzOTIhYjgjMjM5MjMwMzAwNTMz"
```

**API信息**：
- 端点：`wss://maas-api.cn-huabei-1.xf-yun.com/v1.1/chat`
- 模型：generalv3.5
- 温度：0.3
- 最大Token：2000

**提示词构建**：`run.py` 第4624-4648行
```python
def build_declaration_prompt(topic, countries_data):
    prompt = f"""你是一名WTO谈判专家与文本分析专家。
    请基于以下各国提交的文档，生成一份体现最大相似度与共识的共同宣言。
    
    【谈判主题】{topic}
    
    【各国提交内容】
    {各国PDF提取的文本内容}
    
    【生成要求】
    1) 先进行相似度分析
    2) 提取相似度高的关键语句
    3) 生成正式、专业、结构清晰的共同宣言
    4) 语言中文，800-1200字
    """
    return prompt
```

---

### 关键函数位置标注

#### 生成共同宣言主函数

**API入口**：`run.py` 第4009-4284行
```python
@app.route('/api/generate_declaration', methods=['POST'])
def generate_declaration():
    """生成共同宣言的API - 基于投票通过的文件和文本内容"""
```

#### 读取通过文件

**位置**：`run.py` 第4020-4023行
```python
passed_files = list(cols["db"]["passed_files"].find({
    "session_id": session_id,
    "status": "passed"
}))
```

#### 提取PDF文本

**主函数**：`run.py` 第4717-4738行
```python
def extract_text_from_file(file_path):
    """根据文件扩展名提取文本"""
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
```

**PDF提取**：`run.py` 第4692-4703行
```python
def extract_text_from_pdf(file_path):
    """从PDF文件中提取文本"""
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
```

**调用位置**：`run.py` 第4090行
```python
file_text = extract_text_from_file(file_path)
```

#### 调用大模型

**主函数**：`run.py` 第4480-4523行
```python
def call_llm_for_declaration(topic, countries_data):
    """调用外部AI API生成共同宣言"""
    try:
        return call_xf_yun_api(topic, countries_data)
    except:
        return generate_similarity_based_declaration(topic, countries_data)
```

**星火API**：`run.py` 第4525-4622行
```python
def call_xf_yun_api(topic, countries_data):
    """调用科大讯飞星火API"""
    # WebSocket通信
    ws_url = "wss://maas-api.cn-huabei-1.xf-yun.com/v1.1/chat"
```

**调用位置**：`run.py` 第4183行
```python
declaration_text = call_llm_for_declaration(topic, countries_data)
```

#### 返回结果

**位置**：`run.py` 第4273-4278行
```python
return jsonify({
    "success": True,
    "declaration": declaration_text,
    "participating_countries": [data["country"] for data in countries_data],
    "analysis_info": declaration_record["analysis_info"]
})
```

#### 快速查找表

| 功能 | 函数名 | 位置 | 说明 |
|------|--------|------|------|
| **API入口** | `generate_declaration()` | 4009-4284行 | 主函数 |
| **读取通过文件** | `passed_files.find()` | 4020-4023行 | 从数据库读取 |
| **提取PDF** | `extract_text_from_pdf()` | 4692-4703行 | PyPDF2提取 |
| **清理文本** | `clean_text()` | 4740-4750行 | 清理特殊字符 |
| **调用AI** | `call_llm_for_declaration()` | 4480-4523行 | AI主函数 |
| **星火API** | `call_xf_yun_api()` | 4525-4622行 | 科大讯飞API |
| **构建提示词** | `build_declaration_prompt()` | 4624-4648行 | 构建prompt |
| **返回结果** | `return jsonify()` | 4273-4278行 | 返回前端 |

---

## 🔧 故障排查指南

### 问题1：前端显示"没有通过投票的文件"

**症状**：
```
没有通过投票的文件，无法生成宣言
```

**原因**：
主席没有点击"完成投票"按钮，`passed_files` 集合为空

**解决方案**：

#### 方法1：使用补救API（推荐）

在浏览器控制台（F12）执行：
```javascript
fetch('/api/rebuild_passed_files', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        session_id: "00037"  // ⭐ 替换成您的会议ID
    })
})
.then(r => r.json())
.then(data => {
    console.log('结果:', data);
    if (data.code === 200) {
        alert('✅ 成功！通过 ' + data.data.passed_count + ' 个文件');
        location.reload();
    }
});
```

#### 方法2：主席点击"完成投票"按钮

1. 访问投票监控页面
2. 点击右下角绿色的"完成投票"按钮
3. 等待处理完成

#### 验证修复成功

在MongoDB中查询：
```javascript
db.passed_files.find({"session_id": "00037"})
```

应该有数据。

---

### 问题2：星火API认证失败（401 Unauthorized）

**日志显示**：
```
WebSocket错误: Handshake status 401 Unauthorized
星火API调用失败，将回退本地算法
```

**原因**：
API密钥过期或不正确

**影响**：
- ❌ 无法使用AI生成高质量宣言
- ✅ 系统自动回退到本地算法（jieba分词）
- ✅ 仍然能生成宣言，但质量可能不如AI

**解决方案**：

#### 方案1：更新星火API凭证

1. 登录科大讯飞开放平台：https://console.xfyun.cn/
2. 查看您的星火API凭证
3. 更新 `run.py` 第4531-4533行：
```python
APPID = "你的APPID"
APIKey = "你的APIKey"
APISecret = "你的APISecret"
```

#### 方案2：继续使用本地算法

不需要任何操作，系统已自动回退

---

### 问题3：数据库保存失败（`name 'db' is not defined`）

**日志显示**：
```
✅ 大模型返回宣言长度: 30617
生成共同宣言时出错: name 'db' is not defined
127.0.0.1 ... 500 -
```

**原因**：
代码Bug，已在v3.0版本修复

**解决方案**：
重启服务器即可，修复代码会自动生效

---

### 问题4：前端调用旧API

**症状**：
虽然文件通过，但生成宣言时不提取PDF文本

**原因**：
前端调用了旧版API `/api/generate_consensus_declaration`

**解决方案**：
已在 `chairman_declaration.html` 第766行修复：
```javascript
// 修复后
fetch(`/api/generate_declaration?session_id=${sessionId}`, {...})
```

---

### 诊断工具

#### MongoDB诊断脚本

```javascript
var sessionId = "YOUR_SESSION_ID";  // 替换成您的会议ID

print("=== 1. 检查投票详情 ===");
db.file_vote_details.find({"session_id": sessionId}).forEach(printjson);

print("\n=== 2. 检查passed_files集合 ===");
var passedFiles = db.passed_files.find({"session_id": sessionId}).toArray();
print("通过的文件数量: " + passedFiles.length);
passedFiles.forEach(printjson);

print("\n=== 3. 检查submissions集合 ===");
db.submissions.find({"session_id": sessionId}).forEach(printjson);

// 诊断结果
if (passedFiles.length === 0) {
    print("\n❌ passed_files集合为空！需要执行补救API或点击完成投票按钮");
} else {
    print("\n✅ passed_files集合有数据，投票完成流程正常");
}
```

---

## 🛠️ API接口

### 投票相关

#### 完成投票
```http
POST /api/finalize_file_voting
Content-Type: application/json

{
  "session_id": "00037",
  "vote_matrix": {
    "中国": {"file_001": "agree"},
    "美国": {"file_001": "agree"}
  },
  "completed_at": "2024-10-14T16:00:00Z"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "文件投票流程已完成",
  "data": {
    "file_results": {...},
    "passed_files": [...],
    "passed_count": 3
  }
}
```

#### 补救API（重建passed_files）
```http
POST /api/rebuild_passed_files
Content-Type: application/json

{
  "session_id": "00037"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "成功重建passed_files集合，共有3个文件通过",
  "data": {
    "passed_count": 3,
    "passed_files": [...]
  }
}
```

### 共同宣言相关

#### 生成共同宣言
```http
POST /api/generate_declaration?session_id=00037
Content-Type: application/json

{
  "generation_type": "ai"
}
```

**响应**：
```json
{
  "success": true,
  "declaration": "各国代表经过深入讨论...",
  "participating_countries": ["中国", "美国", "日本"],
  "analysis_info": {
    "total_countries": 3,
    "files_processed": 3,
    "manual_text_count": 0
  }
}
```

#### 获取通过的文件列表
```http
GET /api/get_passed_submissions?session_id=00037
```

**响应**：
```json
{
  "code": 200,
  "data": [
    {
      "country_id": "中国",
      "country_name": "中国",
      "file_name": "20241014153045_中国提案.pdf",
      "original_name": "中国提案.pdf",
      "vote_agree": 15,
      "vote_disagree": 3
    }
  ]
}
```

---

## 📁 项目结构

```
project_new/
├── app/
│   ├── static/
│   │   ├── flags/              # 200+国家国旗图片
│   │   ├── uploads/            # 🔥 PDF文件存储（实际文件）
│   │   ├── temp_uploads/       # 临时文件
│   │   ├── styles.css
│   │   └── script.js
│   ├── templates/
│   │   ├── chairman_vote_monitoring.html   # 投票监控（含完成投票按钮）
│   │   ├── chairman_declaration.html       # 共同宣言生成
│   │   ├── file_upload_submit.html         # 文件上传
│   │   └── ...
│   ├── models.py
│   └── routes.py
├── run.py                      # 🔥 主启动文件（所有API在这里）
├── requirements.txt            # Python依赖
├── README.md                   # 📖 本文档
└── 文档/
    ├── PDF_TO_DECLARATION_WORKFLOW.md
    ├── VOTING_MECHANISM_GUIDE.md
    ├── DECLARATION_FUNCTIONS_GUIDE.md
    ├── ERROR_ANALYSIS.md
    └── ...
```

### 关键文件说明

| 文件 | 行数 | 说明 |
|------|------|------|
| `run.py` | 5395 | **核心文件**，包含所有API |
| `chairman_vote_monitoring.html` | 1287 | 投票监控页面 |
| `chairman_declaration.html` | 1074 | 共同宣言页面 |
| `requirements.txt` | 29 | Python依赖 |

---

## 📊 数据库结构

### 核心集合

| 集合名 | 用途 | 关键字段 |
|--------|------|---------|
| `file_vote_details` | 投票记录 | country_id, file_id, vote_result |
| `passed_files` | 🔥 通过的文件 | file_name, status, vote_agree |
| `submissions` | 文件提交 | file_name, vote_passed |
| `declarations` | 共同宣言 | declaration, topic, status |
| `countries_lc` | 国家信息 | name, flag_url |
| `meeting_settings` | 会议设置 | committee_name, agenda |

### 数据流转

```
file_vote_details (投票记录)
    ↓ 主席点击"完成投票"
passed_files (通过的文件名) → 生成宣言时读取
    ↑ 同时更新
submissions (标记vote_passed=true)
```

---

## 🧪 测试与调试

### 启用调试模式

`run.py` 末尾：
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 查看详细日志

生成宣言时，服务器会输出：
```
============================================================
🚀 生成宣言API被调用，session_id: 00037
============================================================

📁 从passed_files集合找到通过的文件数量: 3

📝 开始处理passed_files中的 3 个文件...

🌍 处理国家: 中国
📄 文件名: 20241014153045_中国提案.pdf
📂 文件路径: E:\WTO_moni\project_new\app\static\uploads\20241014153045_中国提案.pdf
✅ 文件存在: True
📖 提取的原始文件文本长度: 1523
🧹 清理后的文件文本长度: 1450
✅ 已添加到countries_data: 中国

============================================================
🤖 准备调用大模型生成共同宣言
📌 主题: 国际贸易规则改革
🌍 参与国家数量: 3
   1. 中国 - 文本长度: 1450
   2. 美国 - 文本长度: 1380
   3. 日本 - 文本长度: 1290

🚀 开始调用大模型API...
✅ 大模型返回宣言长度: 856
============================================================

💾 宣言已保存到数据库

✅ 共同宣言生成成功！
   - 宣言长度: 856 字
   - 参与国家: 3 个
```

---

## ❓ 常见问题

### Q1: 投票数据存在，但生成宣言时提示没有文件？
**A**: 主席没有点击"完成投票"按钮。执行补救API或点击按钮。

### Q2: 星火API返回401错误？
**A**: API密钥过期。系统会自动回退到本地算法，不影响功能。

### Q3: PDF文本提取失败？
**A**: 检查文件是否为扫描版PDF（无文本层）。扫描版需要OCR才能提取。

### Q4: 生成的宣言质量不高？
**A**: 
- 如果使用本地算法（星火API失败），质量会降低
- 更新星火API凭证以使用AI生成

### Q5: 如何查看生成的宣言？
**A**: 
1. 前端文本框（主要方式）
2. MongoDB: `db.declarations.find().sort({generated_at:-1}).limit(1)`
3. 浏览器F12 → Network → 查看API响应

### Q6: MongoDB连接失败？
**A**: 
```bash
# 检查MongoDB是否启动
mongosh

# Windows启动MongoDB
net start MongoDB

# 检查端口27017是否被占用
netstat -an | findstr 27017
```

### Q7: 依赖包安装失败？
**A**: 
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Q8: 端口5000被占用？
**A**: 
修改 `run.py` 末尾：
```python
app.run(debug=True, port=5001)  # 改为其他端口
```

---

## 🔄 版本历史

### v3.0 (2024-10-14) - 当前版本
- ✅ **完整的PDF文本提取**：使用PyPDF2提取PDF内容
- ✅ **AI驱动宣言生成**：集成科大讯飞星火3.5
- ✅ **三层容错机制**：AI→本地算法→模板
- ✅ **优化投票流程**：自动保存通过文件到passed_files
- ✅ **补救API**：`/api/rebuild_passed_files`
- ✅ **详细日志输出**：emoji日志，方便调试
- ✅ **修复多个Bug**：数据库引用、API调用等

### v2.0 (2024-12)
- 文件上传管理功能
- 动议发言管理
- 投票表决功能
- 基础共同宣言生成

### v1.0
- 基础功能实现
- 点名签到
- 简单投票

---

## 📞 技术支持

### 文档索引
- `README.md` - 完整技术文档（本文档）
- `PDF_TO_DECLARATION_WORKFLOW.md` - PDF提取与宣言生成流程
- `VOTING_MECHANISM_GUIDE.md` - 投票机制详解
- `DECLARATION_FUNCTIONS_GUIDE.md` - 函数位置标注
- `ERROR_ANALYSIS.md` - 错误分析
- `TROUBLESHOOTING_VOTING.md` - 投票故障排查
- `DEPLOYMENT.md` - 部署指南

### 联系方式
如有问题，请：
1. 查看本README的故障排查部分
2. 查看对应的详细文档
3. 联系开发团队

---

## 📄 许可证

本项目采用 MIT 许可证。

---

**开发团队**: WTO模拟谈判系统开发组  
**最后更新**: 2024-10-14  
**版本**: v3.0  
**文档维护**: AI Assistant

---

## 🎓 附录

### 技术栈

**后端**：
- Flask 2.3.3
- PyMongo 4.5.0
- PyPDF2 3.0.1
- python-docx 0.8.11
- jieba 0.42.1
- scikit-learn 1.3.0

**前端**：
- 原生JavaScript
- CSS3
- HTML5

**数据库**：
- MongoDB 4.0+

**AI服务**：
- 科大讯飞星火3.5

### 性能优化建议

1. **PDF处理**：大文件（>5MB）提取较慢，建议限制文件大小
2. **AI调用**：星火API有90秒超时，大量文本可能超时
3. **MongoDB**：为常用查询字段建立索引
4. **缓存**：考虑缓存生成的宣言

### 安全建议

1. **API密钥**：不要将星火API密钥提交到版本控制
2. **文件上传**：限制文件类型和大小
3. **数据验证**：验证所有用户输入
4. **访问控制**：添加用户认证机制

---

**感谢使用WTO模拟谈判系统！** 🎉
