"""
O3 Deep Research with Bing Search - REST API Version
使用 Azure OpenAI REST API 的 O3 深度研究模型進行網路搜尋與分析的互動式應用程式
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

# 載入 .env 檔案中的環境變數
load_dotenv()


class ResearchSession:
    """管理研究會話的類別 (REST API 版本)"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.base_url = f"{self.endpoint}/openai/v1/responses"
        self.research_history = []
        self.session_start_time = datetime.now()
        
        # 初始化 Logging 機制
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.session_log_file = self.log_dir / f"session_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}.json"
        self.logs = []
        print(f"📝 本次會話的原始回應將記錄於: {self.session_log_file}")

    def log_raw_response(self, stage, user_input, response_data):
        """記錄原始 Response 到 JSON 檔案"""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "stage": stage,
                "input_preview": user_input[:500] + "..." if len(user_input) > 500 else user_input,
                "response": response_data
            }
            
            self.logs.append(entry)
            
            # 寫入檔案 (覆寫模式以保持 JSON 格式正確，且排版易讀)
            with open(self.session_log_file, "w", encoding="utf-8") as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ 寫入日誌時發生錯誤: {e}")
    
    def inspect_web_search_queries(self, response_data, stage_name):
        """檢查並顯示 Response 中的 Web Search Query 與 Sources"""
        print(f"\n🔍 [{stage_name}] 檢查 Web Search Query:")
        found_search = False
        
        output = response_data.get('output', [])
        for item in output:
            # 檢查是否為 web_search_call
            if item.get('type') == 'web_search_call':
                action = item.get('action', {})
                action_type = action.get('type', '')
                
                if action_type == 'search':
                    query = action.get('query', 'N/A')
                    print(f"  - [Search] 關鍵字: {query}")
                    
                    # 顯示來源連結
                    sources = action.get('sources', [])
                    if sources:
                        print(f"    來源連結 ({len(sources)}):")
                        for source in sources:
                            url = source.get('url', 'N/A')
                            print(f"      - {url}")
                    found_search = True
                    
                elif action_type == 'open_page':
                    url = action.get('url', 'N/A')
                    print(f"  - [Open Page] URL: {url}")
                    found_search = True
                    
                elif action_type == 'find':
                    pattern = action.get('pattern', 'N/A')
                    url = action.get('url', 'N/A')
                    print(f"  - [Find] Pattern: {pattern} (in {url})")
                    found_search = True
        
        if not found_search:
            print("  (此回應中未發現 Web Search 呼叫)")
        print("-" * 40)

    def extract_output_text(self, response_data):
        """從 Response 中提取文字輸出"""
        output = response_data.get('output', [])
        text_parts = []
        
        for item in output:
            if item.get('type') == 'message':
                content = item.get('content', [])
                for content_item in content:
                    if content_item.get('type') == 'output_text':
                        text_parts.append(content_item.get('text', ''))
        
        return '\n'.join(text_parts)

    def create_response(self, input_text, previous_response_id=None, background=False):
        """呼叫 Azure OpenAI REST API 建立研究回應"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "o3-deep-research",
            "background": background,
            "tools": [
                {"type": "web_search_preview"},
                {"type": "code_interpreter", "container": {"type": "auto"}}
            ],
            "input": input_text
        }
        
        if previous_response_id:
            payload["previous_response_id"] = previous_response_id
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=1800  # 30 分鐘超時
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception("請求超時（30 分鐘）。建議使用 background=True 模式進行更長時間的研究。")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 請求失敗: {str(e)}")

    def get_response_status(self, response_id):
        """查詢背景任務的狀態 (如果使用 background 模式)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        url = f"{self.base_url}/{response_id}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"查詢狀態失敗: {str(e)}")

    def wait_for_completion(self, response_id, max_wait_seconds=600):
        """等待背景任務完成"""
        start_time = time.time()
        print(f"\n⏳ 等待研究任務完成 (Response ID: {response_id})...")
        
        while time.time() - start_time < max_wait_seconds:
            status_response = self.get_response_status(response_id)
            status = status_response.get('status', 'unknown')
            
            print(f"  當前狀態: {status}")
            
            if status == 'completed':
                print("✓ 研究任務已完成！")
                return status_response
            elif status == 'failed':
                error_msg = status_response.get('error', {}).get('message', '未知錯誤')
                raise Exception(f"研究任務失敗: {error_msg}")
            
            # 等待一段時間後再次查詢
            time.sleep(10)
        
        raise Exception(f"等待超時 ({max_wait_seconds} 秒)")

    def conduct_research(self, research_topic, use_background_mode=False):
        """執行完整的研究流程"""
        start_time = datetime.now()
        
        print("\n" + "=" * 80)
        print("階段 1: 建立研究計畫")
        print("=" * 80)
        
        # 第一階段：建立研究計畫（支援迭代修改）
        plan_approved = False
        response_data = None
        response_id = None
        current_input = (
            f"請針對以下研究內容，列出詳細的研究計畫與搜尋關鍵字清單，不要執行實際的深度搜索。\n\n"
            f"研究內容：{research_topic}"
        )
        
        while not plan_approved:
            response_data = self.create_response(current_input, background=False)
            
            # 記錄原始回應
            self.log_raw_response("Stage 1: Plan Creation", current_input, response_data)
            
            # 檢查並顯示 Web Search Query
            self.inspect_web_search_queries(response_data, "階段 1: 建立研究計畫")

            # 提取並顯示研究計畫
            output_text = self.extract_output_text(response_data)
            print("\n研究計畫：")
            print("-" * 80)
            print(output_text)
            print("-" * 80)
            
            response_id = response_data.get('id')
            print(f"\nResponse ID: {response_id}")
            
            # 等待使用者回饋
            print("\n" + "=" * 80)
            print("請檢視以上研究計畫與搜尋關鍵字")
            print("選項：")
            print("  - 輸入「確認」或「OK」以繼續執行深度研究")
            print("  - 輸入修改建議（例如：請增加供應鏈風險分析）")
            print("  - 輸入「取消」以放棄本次研究")
            print("=" * 80)
            user_input = input("\n您的回饋: ").strip()
            
            if user_input.lower() in ["取消", "cancel"]:
                print("\n已取消研究執行。")
                return None
            elif user_input.lower() in ["確認", "ok", "okay", "yes"]:
                plan_approved = True
                print("\n✓ 研究計畫已確認！")
            else:
                # 使用者提供修改建議
                print(f"\n正在根據您的回饋調整研究計畫：「{user_input}」")
                current_input = (
                    f"請根據以下使用者回饋，修改研究計畫與搜尋關鍵字：\n\n"
                    f"原始研究內容：{research_topic}\n\n"
                    f"使用者回饋：{user_input}\n\n"
                    f"請提供修改後的研究計畫與搜尋關鍵字清單，不要執行實際的深度搜索。"
                )
        
        print("\n階段 2: 執行深度研究")
        print("=" * 80)
        
        if use_background_mode:
            print("使用背景模式執行研究（適合長時間任務）...")
        else:
            print("正在執行深度研究，這可能需要幾分鐘時間...\n")
        
        research_start_time = datetime.now()
        
        # 第二階段：執行實際研究
        final_response = self.create_response(
            research_topic,
            previous_response_id=response_id,
            background=use_background_mode
        )
        
        # 如果使用背景模式，需要等待完成
        if use_background_mode:
            final_response_id = final_response.get('id')
            final_response = self.wait_for_completion(final_response_id)
        
        # 記錄原始回應
        self.log_raw_response("Stage 2: Deep Research", research_topic, final_response)
        
        # 檢查並顯示 Web Search Query
        self.inspect_web_search_queries(final_response, "階段 2: 執行深度研究")

        research_end_time = datetime.now()
        research_duration = (research_end_time - research_start_time).total_seconds()
        total_duration = (research_end_time - start_time).total_seconds()
        
        # 提取並顯示最終研究結果
        final_output_text = self.extract_output_text(final_response)
        print("\n最終研究結果：")
        print("-" * 80)
        print(final_output_text)
        print("-" * 80)
        print(f"\n⏱️ 研究執行時間: {research_duration:.2f} 秒")
        print(f"⏱️ 總耗時（含計畫制定）: {total_duration:.2f} 秒")
        
        # 儲存到歷史記錄
        research_record = {
            "timestamp": datetime.now(),
            "topic": research_topic,
            "response_id": response_id,
            "plan": output_text,
            "result": final_output_text,
            "research_duration_seconds": research_duration,
            "total_duration_seconds": total_duration
        }
        self.research_history.append(research_record)
        
        return research_record
    
    def save_all_results(self):
        """儲存所有研究結果到 Markdown 檔案"""
        if not self.research_history:
            print("\n目前沒有任何研究記錄需要儲存。")
            return None
        
        # 建立 output 資料夾
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # 生成時間戳記
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"o3-deep-research-session_{timestamp}.md"
        
        # 寫入所有研究結果
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# O3 Deep Research Session Report\n\n")
            f.write(f"**Session Start:** {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Session End:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Researches:** {len(self.research_history)}\n\n")
            f.write("=" * 80 + "\n\n")
            
            for idx, record in enumerate(self.research_history, 1):
                f.write(f"## 研究 #{idx}\n\n")
                f.write(f"**時間:** {record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Response ID:** {record['response_id']}\n\n")
                f.write(f"**研究主題:**\n```\n{record['topic']}\n```\n\n")
                
                # 顯示時間資訊
                research_time = record.get('research_duration_seconds', 0)
                total_time = record.get('total_duration_seconds', 0)
                f.write(f"**研究執行時間:** {research_time:.2f} 秒\n\n")
                f.write(f"**總耗時（含計畫制定）:** {total_time:.2f} 秒\n\n")
                
                f.write("---\n\n")
                f.write("### 研究計畫與搜尋關鍵字\n\n")
                f.write(record['plan'])
                f.write("\n\n---\n\n")
                f.write("### 研究結果\n\n")
                f.write(record['result'])
                f.write("\n\n" + "=" * 80 + "\n\n")
        
        return output_file


def print_welcome():
    """顯示歡迎訊息"""
    print("\n" + "=" * 80)
    print("歡迎使用 O3 Deep Research Interactive App (REST API 版本)")
    print("=" * 80)
    print("\n此應用程式使用 Azure OpenAI REST API 進行深度研究。")
    print("\n指令說明：")
    print("  - 直接輸入研究主題來開始新的研究")
    print("  - 輸入「離開」或「quit」來結束程式並儲存所有研究結果")
    print("\n技術特點：")
    print("  - 使用 REST API 而非 SDK")
    print("  - 支援背景模式（適合長時間任務）")
    print("  - 完整的錯誤處理與狀態追蹤")
    print("\n" + "=" * 80 + "\n")


def main():
    """主程式"""
    print_welcome()
    
    # 建立研究會話
    session = ResearchSession()
    
    # 主要互動迴圈
    while True:
        try:
            # 取得使用者輸入
            user_input = input("\n請輸入研究主題（或輸入「離開」/「quit」結束）: ").strip()
            
            # 檢查是否要離開
            if user_input.lower() in ["離開", "quit", "exit", "q"]:
                print("\n正在儲存研究結果並結束程式...")
                break
            
            # 檢查是否為空輸入
            if not user_input:
                print("⚠️ 請輸入有效的研究主題。")
                continue
            
            # 詢問是否使用背景模式
            print("\n是否使用背景模式？（建議用於長時間研究任務）")
            bg_mode_input = input("輸入 'y' 或 'yes' 使用背景模式，其他則為一般模式: ").strip().lower()
            use_background = bg_mode_input in ['y', 'yes']
            
            # 執行研究
            result = session.conduct_research(user_input, use_background_mode=use_background)
            
            if result:
                print(f"\n✓ 研究完成！已加入到會話記錄中。")
                print(f"目前共有 {len(session.research_history)} 筆研究記錄。")
        
        except KeyboardInterrupt:
            print("\n\n偵測到中斷信號，正在儲存研究結果並結束程式...")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {str(e)}")
            print("您可以繼續輸入新的研究主題，或輸入「離開」結束程式。")
    
    # 儲存所有研究結果
    output_file = session.save_all_results()
    
    if output_file:
        print(f"\n✓ 所有研究結果已儲存至: {output_file}")
        print(f"總共完成 {len(session.research_history)} 筆研究。")
    
    print("\n感謝使用 O3 Deep Research Interactive App (REST API 版本)！再見！\n")


if __name__ == "__main__":
    main()
