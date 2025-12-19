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
.
├── main.py              # SDK 版本主程式 (適合快速原型)
├── main_rest_api.py     # REST API 版本主程式 (支援背景執行)
├── output/              # 自動產生的研究報告 (.md)
├── logs/                # REST API 執行日誌 (.json)
├── squence_diagram/     # 系統運作流程圖
├── .env                 # API 金鑰與環境設定
└── pyproject.toml       # 專案依賴與配置
```

## 🔍 系統運作邏輯

如果您想深入了解 O3 Deep Research 與 Web Search 的完整互動流程，請參考：

📊 **Sequence Diagram（互動流程圖）**：
- 線上瀏覽：[o3-deep-research-web-search-sequence.md](squence_diagram/o3-deep-research-web-search-sequence.md)
- 離線觀看：下載 [o3-deep-research-web-search-sequence.html](squence_diagram/o3-deep-research-web-search-sequence.html) 並用瀏覽器開啟

Sequence Diagram 詳細說明了：
- 使用者、Python 應用程式、Azure OpenAI API 與 Bing Search 之間的互動流程
- 多步驟推理循環的完整過程
- Web Search 呼叫機制（search、open_page、find_in_page）
- 背景模式執行與狀態查詢機制
- Response 結構與引用標註處理
- 最佳實踐與成本控制建議

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- [UV](https://github.com/astral-sh/uv) 套件管理工具
- Azure OpenAI 服務帳號與 API Key

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/ownway22/o3-deep-research-with-bing-search
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

**Python SDK 版本**：
```bash
uv run python main.py
```

**REST API 版本**：
```bash
uv run python main_rest_api.py
```

## 🔄 Python SDK vs REST API 版本比較

本專案提供兩種實作方式，您可以根據需求選擇適合的版本：

### 版本差異對照表

| 特性 | SDK 版本 ([main.py](main.py)) | REST API 版本 ([main_rest_api.py](main_rest_api.py)) |
|-----|-------------------------------|--------------------------------------------------|
| **依賴套件** | `openai` SDK | `requests` |
| **API 呼叫方式** | `client.responses.create()` | `requests.post()` + JSON |
| **背景模式支援** | ❌ 不支援 | ✅ 支援 (適合長時間任務) |
| **狀態查詢** | ❌ 無 | ✅ 可查詢背景任務進度 |
| **超時控制** | SDK 預設值 | ⏱️ 30 分鐘可自訂 |
| **錯誤處理** | SDK 內建 | 手動實作（更細緻） |
| **學習曲線** | 簡單易用 | 需了解 REST API 規範 |
| **建議使用時機** | • 快速開始與原型開發<br>• 不需要背景模式執行<br>• 偏好簡潔的程式碼<br>• 研究時間在 5 分鐘以內 | • 需要長時間執行（> 5 分鐘）<br>• 需要背景模式與狀態追蹤<br>• 需要精細控制超時時間<br>• 部署到生產環境<br>• 與其他系統整合 |

### REST API 版本額外功能

1. **背景模式執行**
   - 適合長時間研究任務（超過 30 分鐘）
   - 避免 HTTP 連線超時問題
   - 可定期查詢任務進度

2. **狀態查詢機制**
   - 即時追蹤研究進度
   - 掌握任務執行狀態（進行中、已完成、失敗）
   - 適合建立監控儀表板

3. **自訂超時設定**
   - 預設 30 分鐘超時
   - 可根據需求調整
   - 更靈活的錯誤處理

## 💡 使用說明

### 基本操作流程（SDK 版本）

1. **啟動程式**：執行 `uv run python main.py`

2. **輸入研究主題**：根據提示輸入您要研究的主題
   ```
   請輸入研究主題: 研究微軟 Ignite 2025 在 AI Agent 相關技術的三大亮點
   ```

3. **審核研究計畫**：系統會先產生研究計畫與搜尋關鍵字
   - 輸入「確認」或「OK」：繼續執行 Deep Research
   - 輸入修改建議：系統會根據回饋調整計畫（例如：「請增加供應鏈風險分析」）
   - 輸入「取消」：放棄本次研究

4. **執行 Deep Research**：系統會進行 Web Search、資料分析並產生完整報告

5. **繼續或結束**：
   - 繼續輸入新主題進行下一輪研究
   - 輸入「離開」或「quit」結束程式並自動儲存所有結果

### 基本操作流程（REST API 版本）

1. **啟動程式**：執行 `uv run python main_rest_api.py`

2. **輸入研究主題**：根據提示輸入您要研究的主題
   ```
   請輸入研究主題: 研究微軟 Ignite 2025 在 AI Agent 相關技術的三大亮點
   ```

3. **選擇執行模式**：
   ```
   是否使用背景模式？（建議用於長時間研究任務）
   輸入 'y' 或 'yes' 使用背景模式，其他則為一般模式:
   ```
   - **一般模式**：同步等待結果（適合快速研究）
   - **背景模式**：非同步執行，系統會定期輪詢狀態（適合長時間研究）

4. **審核研究計畫**：系統會先產生研究計畫與搜尋關鍵字
   - 輸入「確認」或「OK」：繼續執行深度研究
   - 輸入修改建議：系統會根據回饋調整計畫
   - 輸入「取消」：放棄本次研究

5. **執行深度研究**：
   - **一般模式**：等待 API 回應（最多 30 分鐘）
   - **背景模式**：系統每 10 秒查詢一次狀態，直到完成

6. **查看結果與日誌**：
   - 研究結果會顯示在終端
   - 完整的 API 回應記錄在 `logs/session_YYYYMMDD_HHMMSS.json`
   - 可檢視所有 Web Search 查詢與來源連結

7. **繼續或結束**：
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

- **Azure OpenAI O3 Deep Research Model**：提供 Deep Research 與推理能力

**SDK 版本 (main.py)**：
```python
ResearchSession (類別)
├── __init__()              # 初始化 OpenAI Client
├── conduct_research()      # 執行完整研究流程
│   ├── 階段 1: 建立研究計畫（支援迭代修改）
│   └── 階段 2: 執行 Deep Research
├── log_raw_response()      # 記錄原始回應
├── inspect_web_search_queries()  # 檢查 Web Search
└── save_all_results()      # 儲存所有研究結果
```

**REST API 版本 (main_rest_api.py)**：
```python
ResearchSession (類別)
├── __init__()              # 初始化 API 連線資訊
├── create_response()       # 呼叫 REST API 建立研究
├── get_response_status()   # 查詢背景任務狀態
├── wait_for_completion()   # 等待背景任務完成
├── conduct_research()      # 執行完整研究流程
│   ├── 階段 1: 建立研究計畫（支援迭代修改）
│   └── 階段 2: 執行 Deep Research（支援背景模式）
├── extract_output_text()   # 從 JSON 提取文字輸出
├── log_raw_response()      # 記錄原始回應到 JSON
└── inspect_web_search_queries()  # 檢查 Web Search 查詢
```

## 📊 使用範例

### 範例一：微軟 Ignite 2025 AI Agent 技術研究

**輸入主題**：
```
研究微軟 Ignite 2025 在 AI Agent 相關技術的三大亮點
```

**輸出內容**：
- Azure AI Foundry 與 Agent 開發平台的重大更新
- Multi-Agent Orchestration 與協作框架
- Autonomous Agents 的企業級應用場景
- AI Agent 安全性與治理機制
- 與 GitHub Copilot 和 Microsoft 365 的整合
- 詳細的技術規格與實作案例引用

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

### 修改模型參數（SDK 版本）

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

### 修改 REST API 參數（REST API 版本）

編輯 `main_rest_api.py` 中的 `create_response()` 方法：

```python
payload = {
    "model": "o3-deep-research",
    "background": background,  # 背景模式開關
    "tools": [
        {"type": "web_search_preview"},
        {"type": "code_interpreter", "container": {"type": "auto"}}
    ],
    "input": input_text,
    # 可添加 max_tool_calls, webhook 等參數
}
```

### 調整超時設定（REST API 版本）

在 `create_response()` 方法中修改 timeout 參數：

```python
response = requests.post(
    self.base_url,
    headers=headers,
    json=payload,
    timeout=1800  # 30 分鐘超時（秒），可依需求調整
)
```

### 調整背景模式輪詢間隔（REST API 版本）

在 `wait_for_completion()` 方法中修改：

```python
# 等待一段時間後再次查詢
time.sleep(10)  # 預設 10 秒，可調整為 5-30 秒
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

## 🐛 疑難排解

### 常見問題

**Q1: 執行時出現 `ModuleNotFoundError: No module named 'openai'`**

A: 請確認已執行 `uv sync` 安裝相依套件，並使用 `uv run python main.py` 執行程式。

**Q2: API 呼叫失敗，出現 `Authentication Error`**

A: 請檢查 `.env` 檔案中的 `AZURE_OPENAI_API_KEY` 與 `AZURE_OPENAI_ENDPOINT` 是否正確。

**Q3: 研究執行時間過長**

A: O3 Deep Research 模型執行 Deep Research 需要較長時間（通常 1-5 分鐘）。
- **SDK 版本**：同步等待，最長等待時間取決於 SDK 預設值
- **REST API 版本**：
  - 一般模式：最長等待 30 分鐘
  - 背景模式：建議用於超過 5 分鐘的研究，可避免超時問題

**Q3-1: 如何選擇是否使用背景模式？**

A: 使用 REST API 版本時：
- 選擇「一般模式」：適合預期 5-10 分鐘內完成的研究
- 選擇「背景模式」：適合複雜主題、需要超過 10 分鐘的深度研究
- 背景模式會每 10 秒顯示當前狀態，方便追蹤進度

**Q4: 輸出檔案中文顯示為亂碼**

A: 確保使用支援 UTF-8 編碼的文字編輯器開啟 Markdown 檔案（如 VS Code、Notepad++）。

**Q5: REST API 版本和 SDK 版本可以共存嗎？**

A: 可以！兩個版本使用相同的 `.env` 配置和 `output/` 資料夾，但產生的檔案會有不同的標題標記。您可以根據需求選擇使用哪個版本。

**Q6: 如何查看 REST API 的詳細日誌？**

A: REST API 版本會在 `logs/` 資料夾中產生 JSON 格式的完整日誌，包含：
- 每個 API 請求的完整內容
- 每個 API 回應的完整 JSON
- 所有 Web Search 查詢記錄
- 時間戳記與階段標記

這些日誌可用於除錯和分析 API 呼叫細節。

## 📚 參考資源

### 官方文件

- [Web search with the Responses API - Microsoft Foundry | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/web-search?view=foundry-classic)
- [Deep research with the Responses API - Microsoft Foundry | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/deep-research?view=foundry-classic#best-practices)
- [Why we built the Responses API | OpenAI](https://developers.openai.com/blog/responses-api/)
- [Azure-Samples/deepresearch | Github](https://github.com/Azure-Samples/deepresearch/)

---

**最後更新**: 2025-11-22
