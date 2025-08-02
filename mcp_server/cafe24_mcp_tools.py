# Cafe24 MCP Server Implementation
# 카페24 API MCP 서버 메인 구현

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from cafe24_api_tools import cafe24_tools
from cafe24_config import MCP_SERVER_CONFIG

logger = logging.getLogger(__name__)

# MCP 서버 인스턴스 생성
mcp = FastMCP(MCP_SERVER_CONFIG["name"])

# 도구 정의 (FastMCP 방식)

@mcp.tool()
async def get_products_list(
    limit: int = 10,
    offset: int = 0,
    category_no: Optional[int] = None,
    product_name: Optional[str] = None
) -> str:
    """카페24 쇼핑몰의 상품 목록을 조회합니다.
    
    Args:
        limit: 조회할 상품 수 (기본값: 10, 최대: 100)
        offset: 시작 위치 (기본값: 0)
        
        category_no: 카테고리 번호 (선택사항)
        product_name: 상품명 검색어 (선택사항)
    """
    try:
        result = await cafe24_tools.get_products_list(
            limit=min(limit, 100),
            offset=max(offset, 0),
            category_no=category_no,
            product_name=product_name
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
@mcp.tool()
async def get_product_detail(product_no: int) -> str:
    """특정 상품의 상세 정보를 조회합니다.
    
    Args:
        product_no: 상품 번호
    """
    try:
        result = await cafe24_tools.get_product_detail(product_no=product_no)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
@mcp.tool()
async def create_product(product_data: Dict[str, Any]) -> str:
    """새로운 상품을 생성합니다.
    
    Args:
        product_data: 상품 생성 데이터 (product_name, price, category_no 필수)
    """
    try:
        result = await cafe24_tools.create_product(product_data=product_data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
@mcp.tool()
async def update_product(product_no: int, product_data: Dict[str, Any]) -> str:
    """기존 상품 정보를 수정합니다.
    
    Args:
        product_no: 상품 번호
        product_data: 수정할 상품 데이터
    """
    try:
        result = await cafe24_tools.update_product(product_no=product_no, product_data=product_data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_orders_list(
    limit: int = 10,
    offset: int = 0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_status: Optional[str] = None
) -> str:
    """주문 목록을 조회합니다.
    
    Args:
        limit: 조회할 주문 수 (기본값: 10, 최대: 100)
        offset: 시작 위치 (기본값: 0)
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        order_status: 주문 상태
    """
    try:
        result = await cafe24_tools.get_orders_list(
            limit=min(limit, 100),
            offset=max(offset, 0),
            start_date=start_date,
            end_date=end_date,
            order_status=order_status
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
@mcp.tool()
async def get_order_detail(order_id: str) -> str:
    """특정 주문의 상세 정보를 조회합니다.
    
    Args:
        order_id: 주문 ID
    """
    try:
        result = await cafe24_tools.get_order_detail(order_id=order_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def update_order_status(order_id: str, status_data: Dict[str, Any]) -> str:
    """주문 상태를 수정합니다.
    
    Args:
        order_id: 주문 ID
        status_data: 상태 수정 데이터
    """
    try:
        result = await cafe24_tools.update_order_status(order_id=order_id, status_data=status_data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_customers_list(
    limit: int = 10,
    offset: int = 0,
    member_id: Optional[str] = None,
    email: Optional[str] = None
) -> str:
    """고객 목록을 조회합니다.
    
    Args:
        limit: 조회할 고객 수 (기본값: 10, 최대: 100)
        offset: 시작 위치 (기본값: 0)
        member_id: 회원 ID 검색어 (선택사항)
        email: 이메일 검색어 (선택사항)
    """
    try:
        result = await cafe24_tools.get_customers_list(
            limit=min(limit, 100),
            offset=max(offset, 0),
            member_id=member_id,
            email=email
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
@mcp.tool()
async def get_customer_detail(member_id: str) -> str:
    """특정 고객의 상세 정보를 조회합니다.
    
    Args:
        member_id: 회원 ID
    """
    try:
        result = await cafe24_tools.get_customer_detail(member_id=member_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_categories_list() -> str:
    """카테고리 목록을 조회합니다."""
    try:
        result = await cafe24_tools.get_categories_list()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_category_detail(category_no: int) -> str:
    """특정 카테고리의 상세 정보를 조회합니다.
    
    Args:
        category_no: 카테고리 번호
    """
    try:
        result = await cafe24_tools.get_category_detail(category_no=category_no)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_inventory_status(product_no: int) -> str:
    """상품의 재고 현황을 조회합니다.
    
    Args:
        product_no: 상품 번호
    """
    try:
        result = await cafe24_tools.get_inventory_status(product_no=product_no)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def update_inventory(product_no: int, inventory_data: Dict[str, Any]) -> str:
    """상품의 재고를 수정합니다.
    
    Args:
        product_no: 상품 번호
        inventory_data: 재고 수정 데이터
    """
    try:
        result = await cafe24_tools.update_inventory(product_no=product_no, inventory_data=inventory_data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
@mcp.tool()
async def get_sales_statistics(start_date: str, end_date: str, group_by: str = "date") -> str:
    """매출 통계를 조회합니다.
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        group_by: 그룹화 기준 (date, month, year)
    """
    try:
        result = await cafe24_tools.get_sales_statistics(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_visitor_statistics(start_date: str, end_date: str) -> str:
    """방문자 통계를 조회합니다.
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
    """
    try:
        result = await cafe24_tools.get_visitor_statistics(
            start_date=start_date,
            end_date=end_date
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_dashboard_summary(date: Optional[str] = None) -> str:
    """대시보드 요약 정보를 조회합니다.
    
    Args:
        date: 조회 날짜 (YYYY-MM-DD 형식, 기본값: 오늘)
    """
    try:
        result = await cafe24_tools.get_dashboard_summary(date=date)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def health_check() -> str:
    """API 연결 상태를 확인합니다."""
    try:
        result = await cafe24_tools.health_check()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool()
async def clear_cache() -> str:
    """API 캐시를 초기화합니다."""
    try:
        result = await cafe24_tools.clear_cache()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_result = {
            "success": False,
            "error": {"code": 500, "message": str(e)}
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

# 리소스 정의 (FastMCP 방식)

@mcp.resource("cafe24://api/documentation")
async def get_api_documentation() -> str:
    """카페24 API 문서 및 사용 가이드"""
    documentation = """
# Cafe24 API Documentation

## 개요
이 MCP 서버는 카페24 쇼핑몰 관리를 위한 API 도구들을 제공합니다.

## 주요 기능
- 상품 관리 (조회, 생성, 수정)
- 주문 관리 (조회, 상태 변경)
- 고객 관리 (조회)
- 카테고리 관리 (조회)
- 재고 관리 (조회, 수정)
- 통계 조회 (매출, 방문자)
- 대시보드 요약

## 사용 방법
각 도구는 카페24 API와 연동되어 실시간 데이터를 제공합니다.
환경 변수 설정이 필요합니다.
    """
    return documentation

@mcp.resource("cafe24://config/settings")
async def get_server_config() -> str:
    """MCP 서버 설정 정보"""
    return json.dumps(MCP_SERVER_CONFIG, ensure_ascii=False, indent=2)

@mcp.resource("cafe24://status/health")
async def get_health_status() -> str:
    """서버 및 API 연결 상태"""
    try:
        health_result = await cafe24_tools.health_check()
        return json.dumps(health_result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_status = {
            "success": False,
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_status, ensure_ascii=False, indent=2)

# FastMCP는 데코레이터를 통해 자동으로 핸들러를 등록합니다

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 서버 실행
    mcp.run(transport='stdio')