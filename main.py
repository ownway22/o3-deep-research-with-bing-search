"""
O3 Deep Research with Bing Search - Interactive App
使用 Azure OpenAI 的 O3 深度研究模型進行網路搜尋與分析的互動式應用程式
"""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 載入 .env 檔案中的環境變數
load_dotenv()


class ResearchSession:
    """管理研究會話的類別"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT") + "/openai/v1/",
        )
        self.research_history = []
        self.session_start_time = datetime.now()
    
    def conduct_research(self, research_topic):
        """執行完整的研究流程"""
        start_time = datetime.now()
        
        print("\n" + "=" * 80)
        print("階段 1: 建立研究計畫")
        print("=" * 80)
        
        # 第一階段：建立研究計畫（支援迭代修改）
        plan_approved = False
        response = None
        response_id = None
        current_input = (
            f"請針對以下研究內容，列出詳細的研究計畫與搜尋關鍵字清單，不要執行實際的深度搜索。\n\n"
            f"研究內容：{research_topic}"
        )
        
        while not plan_approved:
            response = self.client.responses.create(
                model="o3-deep-research",
                tools=[
                    {"type": "web_search_preview"},
                    {"type": "code_interpreter", "container": {"type": "auto"}}
                ],
                input=current_input
            )
            
            # 顯示研究計畫
            print("\n研究計畫：")
            print("-" * 80)
            print(response.output_text)
            print("-" * 80)
            
            response_id = response.id
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
        print("正在執行深度研究，這可能需要幾分鐘時間...\n")
        
        research_start_time = datetime.now()
        
        # 第二階段：執行實際研究
        final_response = self.client.responses.create(
            model="o3-deep-research",
            tools=[
                {"type": "web_search_preview"},
                {"type": "code_interpreter", "container": {"type": "auto"}}
            ],
            input=research_topic,
            previous_response_id=response_id
        )
        
        research_end_time = datetime.now()
        research_duration = (research_end_time - research_start_time).total_seconds()
        total_duration = (research_end_time - start_time).total_seconds()
        
        # 顯示最終研究結果
        print("\n最終研究結果：")
        print("-" * 80)
        print(final_response.output_text)
        print("-" * 80)
        print(f"\n⏱️ 研究執行時間: {research_duration:.2f} 秒")
        print(f"⏱️ 總耗時（含計畫制定）: {total_duration:.2f} 秒")
        
        # 儲存到歷史記錄
        research_record = {
            "timestamp": datetime.now(),
            "topic": research_topic,
            "response_id": response_id,
            "plan": response.output_text,
            "result": final_response.output_text,
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
    print("歡迎使用 O3 Deep Research Interactive App")
    print("=" * 80)
    print("\n此應用程式可協助您使用 Azure OpenAI O3 模型進行深度研究。")
    print("\n指令說明：")
    print("  - 直接輸入研究主題來開始新的研究")
    print("  - 輸入「離開」或「quit」來結束程式並儲存所有研究結果")
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
            
            # 執行研究
            result = session.conduct_research(user_input)
            
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
    
    print("\n感謝使用 O3 Deep Research Interactive App！再見！\n")



if __name__ == "__main__":
    main()