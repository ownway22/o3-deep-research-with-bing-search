# O3 Deep Research with Bing Search

使用 Azure OpenAI 的 O3 Deep Research 模型進行 Web Search 與分析的互動式應用程式。

## 📋 專案簡介

本專案提供一個互動式 Command Line Interface，讓使用者能夠透過 Azure OpenAI 的 O3 Deep Research 模型進行 Deep Research。系統整合 Bing Search 與 Code Interpreter，能夠針對使用者提出的研究主題進行全面性的資料收集、分析與報告產出。

### 主要功能

- 🔍 **智慧研究規劃**：自動產生研究計畫與搜尋關鍵字清單
- 🔄 **互動式調整**：支援使用者回饋並迭代修改研究計畫
- 🌐 **Web Search 整合**：透過 Bing Search Preview 功能取得最新資訊
- 💻 **Code Interpreter**：支援資料分析與視覺化
- 📝 **自動報告產出**：將研究結果儲存為結構化 Markdown 檔案
- 📊 **Session 管理**：記錄完整研究歷程，支援多輪研究

## 📁 專案結構

```
o3-deep-research-with-bing-search/
│
├── main.py                          # 主程式：互動式研究應用程式
├── pyproject.toml                   # Python 專案配置檔案
├── uv.lock                          # UV 套件管理鎖定檔案
├── .env                             # 環境變數配置（包含 Azure OpenAI 金鑰）
│
├── output/                          # 研究結果輸出資料夾
│   ├── o3-deep-research-session_*.md     # Session 研究報告
│   ├── o3-deep-research-result_*.md      # 單次研究結果
│   └── o3-deep-research-result_*_中文.md # 中文翻譯報告
│
├── .venv/                           # Python Virtual Environment（由 UV 建立）
│
└── o3_deep_research_with_bing_search.egg-info/  # 套件資訊（自動產生）
```

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- [UV](https://github.com/astral-sh/uv) 套件管理工具
- Azure OpenAI 服務帳號與 API Key

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone <repository-url>
   cd o3-deep-research-with-bing-search
   ```

2. **設定環境變數**
   
   編輯 `.env` 檔案，填入您的 Azure OpenAI 資訊：
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
   AZURE_OPENAI_API_KEY=your_api_key_here
   ```

3. **建立虛擬環境並安裝相依套件**
   ```bash
   uv sync
   ```

### 執行應用程式

```bash
uv run python main.py
```

## 💡 使用說明

### 基本操作流程

1. **啟動程式**：執行 `uv run python main.py`

2. **輸入研究主題**：根據提示輸入您要研究的主題
   ```
   請輸入研究主題: 分析 TSMC 在過去一年面臨的 IT 風險
   ```

3. **審核研究計畫**：系統會先產生研究計畫與搜尋關鍵字
   - 輸入「確認」或「OK」：繼續執行 Deep Research
   - 輸入修改建議：系統會根據回饋調整計畫（例如：「請增加供應鏈風險分析」）
   - 輸入「取消」：放棄本次研究

4. **執行 Deep Research**：系統會進行 Web Search、資料分析並產生完整報告

5. **繼續或結束**：
   - 繼續輸入新主題進行下一輪研究
   - 輸入「離開」或「quit」結束程式並自動儲存所有結果

### 輸出檔案格式

系統會在 `output/` 資料夾中產生研究報告：

- **Session 報告**：`o3-deep-research-session_YYYYMMDD_HHMMSS.md`
  - 包含本次執行的所有研究
  - 記錄每筆研究的計畫、結果與執行時間

- **單次研究報告**：`o3-deep-research-result_*.md`
  - 個別研究主題的詳細分析
  - 包含引用來源與 Timestamp

## 🛠️ 技術架構

### 核心技術

- **Azure OpenAI O3 Deep Research Model**：提供 Deep Research 與推理能力
- **Bing Search Preview**：取得最新網路資訊
- **Code Interpreter**：執行資料分析與視覺化任務

### 主要套件

| 套件 | 版本 | 用途 |
|------|------|------|
| `openai` | ≥1.0.0 | Azure OpenAI SDK |
| `python-dotenv` | ≥1.0.0 | 環境變數管理 |

### 程式架構

```python
ResearchSession (類別)
├── __init__()              # 初始化 OpenAI Client
├── conduct_research()      # 執行完整研究流程
│   ├── 階段 1: 建立研究計畫（支援迭代修改）
│   └── 階段 2: 執行 Deep Research
└── save_all_results()      # 儲存所有研究結果
```

## 📊 使用範例

### 範例一：科技公司 IT 風險分析

**輸入主題**：
```
分析 TSMC 在過去一年面臨的 IT 風險
```

**輸出內容**：
- State-Sponsored Cyber Espionage（國家級網路間諜威脅）
- Ransomware 與網路犯罪攻擊
- Third-Party & Supply Chain Vulnerabilities（供應鏈漏洞）
- Insider Threats 與 Trade Secret Leaks（內部威脅）
- Operational Disruptions（營運中斷）
- 詳細的事件案例與資料來源引用

### 範例二：市場趨勢研究

**輸入主題**：
```
分析 2025 年 AI 晶片市場發展趨勢與主要競爭者
```

**研究計畫調整**：
```
使用者回饋: 請增加針對中國市場的分析
系統回應: ✓ 已根據回饋調整研究計畫
```

## ⚙️ 進階設定

### 修改模型參數

編輯 `main.py` 中的 `client.responses.create()` 參數：

```python
response = self.client.responses.create(
    model="o3-deep-research",
    tools=[
        {"type": "web_search_preview"},
        {"type": "code_interpreter", "container": {"type": "auto"}}
    ],
    input=research_topic,
    # 可添加其他參數如 temperature, max_tokens 等
)
```

### 自訂輸出格式

修改 `save_all_results()` 方法中的 Markdown 格式：

```python
f.write(f"# O3 Deep Research Session Report\n\n")
# 根據需求調整標題、段落與格式
```

## 🔒 安全性注意事項

1. **保護 API Key**：
   - 絕對不要將 `.env` 檔案提交到 Version Control System
   - 建議將 `.env` 加入 `.gitignore`

2. **環境變數管理**：
   ```bash
   # .gitignore 範例
   .env
   .venv/
   *.egg-info/
   __pycache__/
   ```

3. **金鑰輪替**：定期更新 Azure OpenAI API Key

## 📝 專案配置檔案說明

### pyproject.toml

```toml
[project]
name = "o3-deep-research-with-bing-search"
version = "0.1.0"
description = "O3 Deep Research with Bing Search using Azure OpenAI"
authors = [
    {name = "Yu-Hong Lin", email = "your.email@example.com"}
]
requires-python = ">=3.8"
dependencies = [
    "openai>=1.0.0",
    "python-dotenv>=1.0.0",
]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

## 🐛 疑難排解

### 常見問題

**Q1: 執行時出現 `ModuleNotFoundError: No module named 'openai'`**

A: 請確認已執行 `uv sync` 安裝相依套件，並使用 `uv run python main.py` 執行程式。

**Q2: API 呼叫失敗，出現 `Authentication Error`**

A: 請檢查 `.env` 檔案中的 `AZURE_OPENAI_API_KEY` 與 `AZURE_OPENAI_ENDPOINT` 是否正確。

**Q3: 研究執行時間過長**

A: O3 Deep Research 模型執行 Deep Research 需要較長時間（通常 1-5 分鐘），請耐心等候。若超過 10 分鐘可能是網路問題，建議重新執行。

**Q4: 輸出檔案中文顯示為亂碼**

A: 確保使用支援 UTF-8 編碼的文字編輯器開啟 Markdown 檔案（如 VS Code、Notepad++）。

## 📚 參考資源

### 官方文件

- [Azure AI Foundry - Web Search 整合指南](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/web-search?view=foundry-classic)
- [Azure AI Foundry - Deep Research 最佳實踐](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/deep-research?view=foundry-classic#best-practices)
- [Why we built the Responses API | OpenAI](https://developers.openai.com/blog/responses-api/)

---

**最後更新**: 2025-11-22
