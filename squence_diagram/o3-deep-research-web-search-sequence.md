# O3-Deep-Research with Web Search - Sequence Diagram

本文檔展示使用者呼叫 o3-deep-research 模型並啟用 web search 功能後的完整互動流程。

## 系統架構說明

O3-Deep-Research 是一個進階研究模型，能夠：
- 執行多步驟推理 (multi-step reasoning)
- 進行網頁搜尋 (web search)
- 瀏覽和分析數百個來源
- 生成具有引用的綜合報告

當啟用 Web Search 時，模型會透過 Grounding with Bing Search 取得即時資訊並提供內嵌引用。

## 完整互動流程圖

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Python as Python 應用程式
    participant API as Azure OpenAI<br/>Responses API
    participant Model as o3-deep-research<br/>Model
    participant WebSearch as Web Search Tool<br/>(Bing Grounding)
    participant Webhook as Webhook Endpoint<br/>(Optional)

    %% 階段 1: 請求初始化
    Note over User,Webhook: 階段 1: 請求初始化與配置
    User->>Python: 提交研究查詢
    
    Python->>API: POST /openai/v1/responses
    Note right of API: 請求參數:<br/>- model: "o3-deep-research"<br/>- background: true<br/>- tools: [web_search_preview]<br/>- webhook: (可選)<br/>- max_tool_calls: (可選)
    
    API->>Model: 初始化深度研究任務
    API-->>Python: 返回 202 Accepted<br/>(background mode)
    Python-->>User: 顯示「研究進行中」狀態

    %% 階段 2: 多步驟研究執行
    Note over Model,WebSearch: 階段 2: 多步驟推理與資料收集
    
    loop 多步驟推理循環
        Model->>Model: 分析查詢，規劃搜尋策略
        
        %% Web Search 呼叫
        Model->>WebSearch: 執行 web_search_call<br/>action: "search"<br/>query: "優化的搜尋查詢"
        Note right of WebSearch: 可選參數:<br/>- user_location.country<br/>- sources (限定域名)
        
        WebSearch->>WebSearch: 透過 Bing Grounding<br/>執行網頁搜尋
        WebSearch-->>Model: 返回搜尋結果<br/>(URL, title, snippets)
        
        %% Deep Research 特有: 開啟頁面
        Model->>WebSearch: (Deep Research)<br/>action: "open_page"<br/>開啟特定頁面
        WebSearch-->>Model: 返回頁面內容
        
        Model->>WebSearch: (Deep Research)<br/>action: "find_in_page"<br/>在頁面中搜尋特定資訊
        WebSearch-->>Model: 返回匹配的內容片段
        
        Model->>Model: 綜合分析所有來源<br/>判斷是否需要更多資訊
        
        alt 需要更多資訊
            Note over Model: 繼續下一輪搜尋
        else 資訊充足
            Note over Model: 結束搜尋，準備生成報告
        end
    end

    %% 階段 3: 生成最終報告
    Note over Model,API: 階段 3: 報告生成與引用標註
    
    Model->>Model: 綜合所有收集的資訊<br/>生成結構化報告<br/>加入內嵌引用 (inline citations)
    
    Model->>API: 返回完整 response
    Note right of API: Response 結構:<br/>- web_search_call (多個)<br/>- message (final answer)

    %% 階段 4: 結果傳遞
    Note over API,User: 階段 4: 結果傳遞
    
    opt 使用 Webhook
        API->>Webhook: POST completion event
        Webhook->>Python: 觸發完成處理
    end
    
    alt 輪詢模式
        Python->>API: GET /responses/{id}
        API-->>Python: 返回狀態和結果
    end
    
    API-->>Python: 返回完整 response object
    Note right of Python: output array 包含:<br/>1. web_search_call 記錄<br/>2. message with annotations
    
    Python->>Python: 解析 response:<br/>- 提取 output_text<br/>- 處理 url_citation annotations<br/>- 格式化引用連結
    
    Python-->>User: 顯示研究報告<br/>包含內嵌引用和來源連結

    %% 額外: 錯誤處理
    Note over User,Webhook: 錯誤處理與安全措施
    
    opt 工具呼叫驗證
        Model->>API: 提交工具呼叫參數
        API->>API: Schema/Regex 驗證<br/>檢查 URL 和參數
        alt 驗證失敗
            API-->>Model: 拒絕呼叫
        else 驗證通過
            API->>WebSearch: 轉發請求
        end
    end
    
    opt 記錄與審計
        API->>API: 記錄所有工具呼叫<br/>和模型輸出
        Note right of API: 用於安全審計和<br/>成本追蹤
    end
```

## Response 結構詳解

### 1. Web Search Call 記錄

```json
{
    "id": "ws_xxx",
    "type": "web_search_call",
    "status": "completed",
    "action": {
        "type": "search",
        "query": "優化後的搜尋查詢",
        "sources": ["domain1.com", "domain2.com"]
    }
}
```

**Action Types:**
- `search`: 執行網頁搜尋（會產生費用）
- `open_page`: (Deep Research) 開啟特定頁面
- `find_in_page`: (Deep Research) 在頁面中搜尋

### 2. Final Message with Citations

```json
{
    "id": "msg_xxx",
    "type": "message",
    "status": "completed",
    "role": "assistant",
    "content": [
        {
            "type": "output_text",
            "text": "研究結果內容...",
            "annotations": [
                {
                    "type": "url_citation",
                    "start_index": 100,
                    "end_index": 250,
                    "url": "https://example.com/article",
                    "title": "文章標題"
                }
            ]
        }
    ]
}
```

## 最佳實踐

### 1. 執行模式
- ✅ **使用 `background: true`** 避免超時
- ✅ **配置 webhook** 接收完成通知
- ✅ **增加 timeout 設定**（若不使用 background mode）

### 2. 成本與延遲控制
- 使用 `max_tool_calls` 限制工具呼叫次數
- 每次 `search` action 會產生 Bing Grounding 費用
- `open_page` 和 `find_in_page` 不產生額外搜尋費用

### 3. 安全措施
- 記錄並審查所有工具呼叫
- 使用 schema 或 regex 驗證工具參數
- 在開啟或分享前驗證連結

### 5. 地理位置控制
```json
{
    "tools": [{
        "type": "web_search_preview",
        "user_location": {
            "type": "approximate",
            "country": "TW"  // ISO 3166-1 country code
        }
    }]
}
```

## 使用場景

### 適合使用 O3-Deep-Research 的情境：
- 📚 法律或科學研究
- 📊 市場與競爭分析
- 📈 基於大量內部或公開資料的報告
- 🔍 需要綜合數百個來源的深度調查
- 📝 需要完整引用的學術或商業報告

### 執行時間考量：
- **Quick Web Search**: 秒級回應
- **Agentic Search**: 分鐘級（適合複雜工作流程）
- **Deep Research**: 數分鐘（適合背景執行的完整調查）

## 技術規格

### 支援的模型
- Web Search (無推理): `gpt-4.1`, `gpt-5` 等
- Agentic Search: 推理模型（reasoning models）
- Deep Research: `o3-deep-research`

### API 端點
- **Base URL**: `https://{resource-name}.openai.azure.com/openai/v1/`
- **Endpoint**: `/responses`
- **Method**: POST

### 認證方式
- Entra ID (Azure AD): `Authorization: Bearer $TOKEN`
- API Key: `api-key: $KEY`

### 費用說明
- 每次 **search** action 產生 Bing Grounding 費用
- 參考 [Grounding with Bing 價格](https://www.microsoft.com/bing/apis/grounding-pricing)
- 模型使用費用依據 Azure OpenAI 標準定價

## 管理功能

Azure 管理員可在訂用帳戶層級管理 Web Search 功能：

### 停用 Web Search
```bash
az feature register --name OpenAI.BlockedTools.web_search \
  --namespace Microsoft.CognitiveServices \
  --subscription "<subscription-id>"
```

### 啟用 Web Search
```bash
az feature unregister --name OpenAI.BlockedTools.web_search \
  --namespace Microsoft.CognitiveServices \
  --subscription "<subscription-id>"
```

## 資料隱私與合規性

⚠️ **重要提醒：**
- 傳送至 Grounding with Bing Search 的資料會流出客戶的合規性和地理邊界
- Microsoft 資料保護增補條款 (DPA) **不適用**於 Bing Search 的資料
- 服務受 [Grounding with Bing 使用條款](https://www.microsoft.com/bing/apis/grounding-legal-enterprise) 與 [Microsoft 隱私權聲明](https://go.microsoft.com/fwlink/?LinkId=521839) 管轄

---

## 參考資源

- [Deep Research 官方文件](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/deep-research)
- [Web Search 官方文件](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/web-search)
- [Grounding with Bing 價格](https://www.microsoft.com/bing/apis/grounding-pricing)
- [Azure OpenAI Responses API](https://learn.microsoft.com/azure/ai-services/openai/reference)
