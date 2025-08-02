#!/usr/bin/env python3
"""
Cafe24 OAuth Server 실행 스크립트

사용법:
    python run_oauth_server.py
    python run_oauth_server.py --port 5000
    python run_oauth_server.py --host 0.0.0.0 --port 5000
"""

import argparse
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from auth_redirect import app

def main():
    parser = argparse.ArgumentParser(description="Cafe24 OAuth Server")
    parser.add_argument(
        "--host", 
        default=os.getenv("OAUTH_SERVER_HOST", "0.0.0.0"),
        help="Host to bind the server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=int(os.getenv("OAUTH_SERVER_PORT", 5000)),
        help="Port to bind the server (default: 5000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        default=os.getenv("DEVELOPMENT_MODE", "false").lower() == "true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    # 환경변수 확인
    required_env_vars = ["CAFE24_CLIENT_ID", "CAFE24_CLIENT_SECRET"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("   .env 파일을 확인해주세요.")
        sys.exit(1)
    
    # 선택적 환경변수 확인 및 경고
    optional_vars = {
        "CAFE24_MALL_ID": "쇼핑몰 ID",
        "CAFE24_REDIRECT_URI": "리디렉션 URI"
    }
    
    for var, description in optional_vars.items():
        if not os.getenv(var):
            print(f"⚠️  {description}({var})가 설정되지 않았습니다.")
    
    print(f"🚀 Cafe24 OAuth Server 시작 중...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {args.reload}")
    print(f"   Log Level: {args.log_level}")
    print(f"")
    print(f"📋 사용 가능한 엔드포인트:")
    print(f"   - 홈: http://{args.host}:{args.port}/")
    print(f"   - 인증 시작: http://{args.host}:{args.port}/oauth/authorize")
    print(f"   - 콜백: http://{args.host}:{args.port}/oauth/callback")
    print(f"   - 토큰 정보: http://{args.host}:{args.port}/oauth/token-info")
    print(f"   - 헬스체크: http://{args.host}:{args.port}/health")
    print(f"")
    
    try:
        uvicorn.run(
            "auth_redirect:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다.")
    except Exception as e:
        print(f"❌ 서버 시작 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()