import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics_agent import AnalyticsAssistant
analytics_assistant = AnalyticsAssistant()

def save_graph_visualization():
    """그래프 시각화를 PNG 파일로 저장"""
    try:
        # 그래프 시각화 데이터 가져오기
        graph_png = analytics_assistant.get_graph_visualization()
        
        if graph_png:
            # PNG 파일로 저장
            with open("workflow_graph.png", "wb") as f:
                f.write(graph_png)
            print("✅ 그래프가 'workflow_graph.png' 파일로 저장되었습니다!")
        else:
            print("❌ 그래프 생성에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_mall_assistant():
    """쇼핑몰 AI 비서 테스트"""

    print("🤖 쇼핑몰 AI 비서 테스트 시작\n")

        
    response = analytics_assistant.process_query("상품 목록을 조회해줘")
    print(f"AI 비서: {response}")
    print("=" * 50)

if __name__ == "__main__":
    # 그래프 시각화 저장
    save_graph_visualization()
    
    # 테스트 실행
    test_mall_assistant()
    