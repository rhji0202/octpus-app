# Cafe24 MCP Server Configuration
# 카페24 API MCP 서버 설정

import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Cafe24Config:
    """카페24 API 설정 클래스"""
    
    # API 기본 설정
    base_url: str = "https://coggiri200.cafe24api.com/api/v2/admin"
    api_version: str = os.getenv("CAFE24_API_VERSION", "")
    
    # OAuth 2.0 설정
    client_id: str = os.getenv("CAFE24_CLIENT_ID", "")
    client_secret: str = os.getenv("CAFE24_CLIENT_SECRET", "")
    access_token: str = "W5zoNiDwNtvvj2IOA3e9RA"
    mall_id: str = os.getenv("CAFE24_MALL_ID", "coggiri200")
    
    # API 제한 설정
    rate_limit_per_minute: int = 1000
    timeout_seconds: int = 30
    
    # 캐시 설정
    cache_ttl_seconds: int = 300  # 5분
    
    def get_api_url(self, endpoint: str) -> str:
        """API URL 생성"""
        base = self.base_url.format(mall_id=self.mall_id)
        return f"{base}/{endpoint.lstrip('/')}"
    
    def get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Cafe24-Api-Version": self.api_version
        }
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        required_fields = [
            self.client_id,
            self.client_secret,
            self.access_token,
            self.mall_id
        ]
        return all(field.strip() for field in required_fields)

# 전역 설정 인스턴스
cafe24_config = Cafe24Config()

# MCP 서버 설정
MCP_SERVER_CONFIG = {
    "name": "cafe24-mcp-server",
    "version": "1.0.0",
    "description": "Cafe24 API MCP Server for Mall Management",
    "capabilities": {
        "products": True,
        "orders": True,
        "customers": True,
        "categories": True,
        "inventory": True,
        "shipping": True,
        "payments": True,
        "coupons": True,
        "boards": True,
        "statistics": True
    }
}

# API 엔드포인트 매핑
API_ENDPOINTS = {
    # 상품 관리
    "products": {
        "list": "/products",
        "detail": "/products/{product_no}",
        "create": "/products",
        "update": "/products/{product_no}",
        "delete": "/products/{product_no}",
        "variants": "/products/{product_no}/variants",
        "options": "/products/{product_no}/options",
        "images": "/products/{product_no}/images"
    },
    
    # 주문 관리
    "orders": {
        "list": "/orders",
        "detail": "/orders/{order_id}",
        "update": "/orders/{order_id}",
        "cancel": "/orders/{order_id}/cancellation",
        "exchange": "/orders/{order_id}/exchange",
        "return": "/orders/{order_id}/return",
        "items": "/orders/{order_id}/items",
        "receivers": "/orders/{order_id}/receivers"
    },
    
    # 고객 관리
    "customers": {
        "list": "/customers",
        "detail": "/customers/{member_id}",
        "create": "/customers",
        "update": "/customers/{member_id}",
        "delete": "/customers/{member_id}",
        "groups": "/customergroups",
        "points": "/customers/{member_id}/points"
    },
    
    # 카테고리 관리
    "categories": {
        "list": "/categories",
        "detail": "/categories/{category_no}",
        "create": "/categories",
        "update": "/categories/{category_no}",
        "delete": "/categories/{category_no}"
    },
    
    # 재고 관리
    "inventory": {
        "list": "/products/{product_no}/inventory",
        "update": "/products/{product_no}/inventory",
        "history": "/products/{product_no}/inventory/history"
    },
    
    # 배송 관리
    "shipping": {
        "methods": "/shipping/setting",
        "zones": "/shipping/setting/zones",
        "carriers": "/carriers",
        "tracking": "/orders/{order_id}/shipments"
    },
    
    # 결제 관리
    "payments": {
        "methods": "/paymentmethods",
        "gateways": "/paymentgateway",
        "transactions": "/orders/{order_id}/transactions"
    },
    
    # 쿠폰 관리
    "coupons": {
        "list": "/coupons",
        "detail": "/coupons/{coupon_no}",
        "create": "/coupons",
        "update": "/coupons/{coupon_no}",
        "delete": "/coupons/{coupon_no}",
        "issue": "/coupons/{coupon_no}/issue"
    },
    
    # 게시판 관리
    "boards": {
        "list": "/boards",
        "articles": "/boards/{board_no}/articles",
        "article_detail": "/boards/{board_no}/articles/{article_no}",
        "comments": "/boards/{board_no}/articles/{article_no}/comments",
        "comments_detail": "/boards/{board_no}/articles/{article_no}/comments/{comment_no}"
    },
    
    # 통계
    "statistics": {
        "hourlysales": "/reports/hourlysales",
        "productsales": "/reports/productsales",
        "salesvolume": "/reports/salesvolume",
    },

    # 알림
    "notification": {
        "send": "/sms",
        "balance": "/sms/balance",
        "receivers": "/sms/receivers",
        "senders": "/sms/senders"
    }
}

# 에러 코드 매핑
ERROR_CODES = {
    400: "잘못된 요청",
    401: "인증 실패",
    403: "권한 없음",
    404: "리소스를 찾을 수 없음",
    409: "중복 요청",
    422: "유효하지 않은 파라미터",
    429: "요청 한도 초과",
    500: "서버 내부 오류",
    503: "서비스 이용 불가",
    504: "요청 시간 초과"
}