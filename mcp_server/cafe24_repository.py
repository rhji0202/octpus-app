# Cafe24 MCP Server Repository
# 카페24 API MCP 서버 데이터 액세스 계층

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from cafe24_client import Cafe24APIClient, Cafe24APIError
from cafe24_config import API_ENDPOINTS

# Configure file handler for logging
file_handler = logging.FileHandler('cafe24_mcp.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Get logger instance and add file handler
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

class Cafe24Repository:
    """카페24 데이터 액세스 계층"""
    
    def __init__(self, client: Cafe24APIClient = None):
        self.client = client
    
    async def _get_client(self) -> Cafe24APIClient:
        """API 클라이언트 인스턴스 반환"""
        if not self.client:
            self.client = Cafe24APIClient()
            await self.client.__aenter__()
        return self.client
    
    # === 상품 관리 데이터 액세스 ===
    
    async def get_products(
        self,
        limit: int = 10,
        offset: int = 0,
        category_no: Optional[int] = None,
        product_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """상품 목록 조회 데이터 액세스"""
        client = await self._get_client()
        params = {"limit": limit, "offset": offset}
        if category_no:
            params["category_no"] = category_no
        if product_name:
            params["product_name"] = product_name
            
        return await client._make_request("GET", API_ENDPOINTS["products"]["list"], params=params)
    
    async def get_product(self, product_no: int) -> Dict[str, Any]:
        """상품 상세 조회 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["products"]["detail"].format(product_no=product_no)
        return await client._make_request("GET", endpoint)
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 생성 데이터 액세스"""
        client = await self._get_client()
        return await client._make_request("POST", API_ENDPOINTS["products"]["create"], data=product_data)
    
    async def update_product(self, product_no: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 수정 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["products"]["update"].format(product_no=product_no)
        return await client._make_request("PUT", endpoint, data=product_data)
    
    async def delete_product(self, product_no: int) -> Dict[str, Any]:
        """상품 삭제 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["products"]["delete"].format(product_no=product_no)
        return await client._make_request("DELETE", endpoint)
    
    # === 주문 관리 데이터 액세스 ===
    
    async def get_orders(
        self,
        limit: int = 10,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """주문 목록 조회 데이터 액세스"""
        client = await self._get_client()
        params = {"limit": limit, "offset": offset}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_status:
            params["order_status"] = order_status
        
        return await client._make_request("GET", API_ENDPOINTS["orders"]["list"], params=params)
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """주문 상세 조회 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["orders"]["detail"].format(order_id=order_id)
        return await client._make_request("GET", endpoint)
    
    async def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 수정 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["orders"]["update"].format(order_id=order_id)
        return await client._make_request("PUT", endpoint, data=order_data)
    
    # === 고객 관리 데이터 액세스 ===
    
    async def get_customers(
        self,
        limit: int = 10,
        offset: int = 0,
        member_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """고객 목록 조회 데이터 액세스"""
        client = await self._get_client()
        params = {"limit": limit, "offset": offset}
        if member_id:
            params["member_id"] = member_id
        if email:
            params["email"] = email
        
        return await client._make_request("GET", API_ENDPOINTS["customers"]["list"], params=params)
    
    async def get_customer(self, member_id: str) -> Dict[str, Any]:
        """고객 상세 조회 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["customers"]["detail"].format(member_id=member_id)
        return await client._make_request("GET", endpoint)
    
    # === 카테고리 관리 데이터 액세스 ===
    
    async def get_categories(self) -> Dict[str, Any]:
        """카테고리 목록 조회 데이터 액세스"""
        client = await self._get_client()
        return await client._make_request("GET", API_ENDPOINTS["categories"]["list"])
    
    async def get_category(self, category_no: int) -> Dict[str, Any]:
        """카테고리 상세 조회 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["categories"]["detail"].format(category_no=category_no)
        return await client._make_request("GET", endpoint)
    
    # === 재고 관리 데이터 액세스 ===
    
    async def get_inventory(self, product_no: int) -> Dict[str, Any]:
        """재고 조회 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["inventory"]["list"].format(product_no=product_no)
        return await client._make_request("GET", endpoint)
    
    async def update_inventory(self, product_no: int, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """재고 수정 데이터 액세스"""
        client = await self._get_client()
        endpoint = API_ENDPOINTS["inventory"]["update"].format(product_no=product_no)
        return await client._make_request("PUT", endpoint, data=inventory_data)
    
    # === 통계 데이터 액세스 ===
    
    async def get_sales_statistics(
        self,
        start_date: str,
        end_date: str,
        group_by: str = "date"
    ) -> Dict[str, Any]:
        """매출 통계 조회 데이터 액세스"""
        client = await self._get_client()
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "group_by": group_by
        }
        return await client._make_request("GET", API_ENDPOINTS["statistics"]["sales"], params=params)
    
    async def get_visitor_statistics(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """방문자 통계 조회 데이터 액세스"""
        client = await self._get_client()
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return await client._make_request("GET", API_ENDPOINTS["statistics"]["visitors"], params=params)
    
    # === 유틸리티 데이터 액세스 ===
    
    async def health_check(self) -> bool:
        """API 연결 상태 확인 데이터 액세스"""
        try:
            client = await self._get_client()
            # 간단한 카테고리 조회로 연결 상태 확인
            await client._make_request("GET", API_ENDPOINTS["categories"]["list"])
            return True
        except Cafe24APIError:
            return False
    
    def clear_cache(self) -> None:
        """캐시 초기화 데이터 액세스"""
        if self.client:
            self.client.clear_cache()
    
    async def close(self) -> None:
        """리소스 정리"""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None

# 전역 레포지토리 인스턴스
cafe24_repository = Cafe24Repository() 