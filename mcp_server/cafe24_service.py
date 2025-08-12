# Cafe24 MCP Server Service
# 카페24 API MCP 서버 서비스 계층

import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from cafe24_repository import cafe24_repository, Cafe24APIError

# Configure file handler for logging
file_handler = logging.FileHandler('cafe24_mcp.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Get logger instance and add file handler
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

class Cafe24Service:
    """카페24 API 서비스 클래스"""
    
    def __init__(self):
        self.repository = cafe24_repository
    
    async def _handle_api_error(self, error: Exception) -> Dict[str, Any]:
        """API 에러 처리"""
        if isinstance(error, Cafe24APIError):
            return {
                "success": False,
                "error": {
                    "code": error.status_code,
                    "message": error.message,
                    "details": error.details
                }
            }
        else:
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": f"예상치 못한 오류: {str(error)}",
                    "details": {}
                }
            }
    
    # === 상품 관리 서비스 ===
    
    async def get_products_list(
        self,
        limit: int = 10,
        offset: int = 0,
        category_no: Optional[int] = None,
        product_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """상품 목록 조회
        
        Args:
            limit: 조회할 상품 수 (기본값: 10)
            offset: 시작 위치 (기본값: 0)
            category_no: 카테고리 번호 (선택사항)
            product_name: 상품명 검색 (선택사항)
        
        Returns:
            상품 목록 데이터
        """
        try:
            result = await self.repository.get_products(
                limit=limit,
                offset=offset,
                category_no=category_no,
                product_name=product_name
            )

            return {
                "success": True,
                "data": result,
                "message": f"상품 목록 조회 완료 ({len(result.get('products', []))}건)"
            }
        except Exception as e:
            logger.error(f"상품 목록 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def get_product_detail(self, product_no: int) -> Dict[str, Any]:
        """상품 상세 정보 조회
        
        Args:
            product_no: 상품 번호
        
        Returns:
            상품 상세 데이터
        """
        try:
            result = await self.repository.get_product(product_no)
            return {
                "success": True,
                "data": result,
                "message": f"상품 {product_no} 상세 정보 조회 완료"
            }
        except Exception as e:
            logger.error(f"상품 상세 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 생성
        
        Args:
            product_data: 상품 생성 데이터
        
        Returns:
            생성된 상품 정보
        """
        try:
            result = await self.repository.create_product(product_data)
            return {
                "success": True,
                "data": result,
                "message": "상품 생성 완료"
            }
        except Exception as e:
            logger.error(f"상품 생성 오류: {e}")
            return await self._handle_api_error(e)
    
    async def update_product(self, product_no: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 수정
        
        Args:
            product_no: 상품 번호
            product_data: 수정할 상품 데이터
        
        Returns:
            수정된 상품 정보
        """
        try:
            result = await self.repository.update_product(product_no, product_data)
            return {
                "success": True,
                "data": result,
                "message": f"상품 {product_no} 수정 완료"
            }
        except Exception as e:
            logger.error(f"상품 수정 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 주문 관리 서비스 ===
    
    async def get_orders_list(
        self,
        limit: int = 10,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """주문 목록 조회
        
        Args:
            limit: 조회할 주문 수
            offset: 시작 위치
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            order_status: 주문 상태
        
        Returns:
            주문 목록 데이터
        """
        try:
            result = await self.repository.get_orders(
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date,
                order_status=order_status
            )
            return {
                "success": True,
                "data": result,
                "message": f"주문 목록 조회 완료 ({len(result.get('orders', []))}건)"
            }
        except Exception as e:
            logger.error(f"주문 목록 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def get_order_detail(self, order_id: str) -> Dict[str, Any]:
        """주문 상세 정보 조회
        
        Args:
            order_id: 주문 ID
        
        Returns:
            주문 상세 데이터
        """
        try:
            result = await self.repository.get_order(order_id)
            return {
                "success": True,
                "data": result,
                "message": f"주문 {order_id} 상세 정보 조회 완료"
            }
        except Exception as e:
            logger.error(f"주문 상세 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def update_order_status(self, order_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 상태 수정
        
        Args:
            order_id: 주문 ID
            status_data: 상태 수정 데이터
        
        Returns:
            수정된 주문 정보
        """
        try:
            result = await self.repository.update_order(order_id, status_data)
            return {
                "success": True,
                "data": result,
                "message": f"주문 {order_id} 상태 수정 완료"
            }
        except Exception as e:
            logger.error(f"주문 상태 수정 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 고객 관리 서비스 ===
    
    async def get_customers_list(
        self,
        limit: int = 10,
        offset: int = 0,
        member_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """고객 목록 조회
        
        Args:
            limit: 조회할 고객 수
            offset: 시작 위치
            member_id: 회원 ID 검색
            email: 이메일 검색
        
        Returns:
            고객 목록 데이터
        """
        try:
            result = await self.repository.get_customers(
                limit=limit,
                offset=offset,
                member_id=member_id,
                email=email
            )
            return {
                "success": True,
                "data": result,
                "message": f"고객 목록 조회 완료 ({len(result.get('customers', []))}건)"
            }
        except Exception as e:
            logger.error(f"고객 목록 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def get_customer_detail(self, member_id: str) -> Dict[str, Any]:
        """고객 상세 정보 조회
        
        Args:
            member_id: 회원 ID
        
        Returns:
            고객 상세 데이터
        """
        try:
            result = await self.repository.get_customer(member_id)
            return {
                "success": True,
                "data": result,
                "message": f"고객 {member_id} 상세 정보 조회 완료"
            }
        except Exception as e:
            logger.error(f"고객 상세 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 카테고리 관리 서비스 ===
    
    async def get_categories_list(self) -> Dict[str, Any]:
        """카테고리 목록 조회
        
        Returns:
            카테고리 목록 데이터
        """
        try:
            result = await self.repository.get_categories()
            return {
                "success": True,
                "data": result,
                "message": f"카테고리 목록 조회 완료 ({len(result.get('categories', []))}건)"
            }
        except Exception as e:
            logger.error(f"카테고리 목록 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def get_category_detail(self, category_no: int) -> Dict[str, Any]:
        """카테고리 상세 정보 조회
        
        Args:
            category_no: 카테고리 번호
        
        Returns:
            카테고리 상세 데이터
        """
        try:
            result = await self.repository.get_category(category_no)
            return {
                "success": True,
                "data": result,
                "message": f"카테고리 {category_no} 상세 정보 조회 완료"
            }
        except Exception as e:
            logger.error(f"카테고리 상세 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 재고 관리 서비스 ===
    
    async def get_inventory_status(self, product_no: int) -> Dict[str, Any]:
        """재고 현황 조회
        
        Args:
            product_no: 상품 번호
        
        Returns:
            재고 현황 데이터
        """
        try:
            result = await self.repository.get_inventory(product_no)
            return {
                "success": True,
                "data": result,
                "message": f"상품 {product_no} 재고 현황 조회 완료"
            }
        except Exception as e:
            logger.error(f"재고 현황 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def update_inventory(self, product_no: int, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """재고 수정
        
        Args:
            product_no: 상품 번호
            inventory_data: 재고 수정 데이터
        
        Returns:
            수정된 재고 정보
        """
        try:
            result = await self.repository.update_inventory(product_no, inventory_data)
            return {
                "success": True,
                "data": result,
                "message": f"상품 {product_no} 재고 수정 완료"
            }
        except Exception as e:
            logger.error(f"재고 수정 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 통계 및 분석 서비스 ===
    
    async def get_sales_statistics(
        self,
        start_date: str,
        end_date: str,
        group_by: str = "date"
    ) -> Dict[str, Any]:
        """매출 통계 조회
        
        Args:
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            group_by: 그룹화 기준 (date, month, year)
        
        Returns:
            매출 통계 데이터
        """
        try:
            result = await self.repository.get_sales_statistics(start_date, end_date, group_by)
            return {
                "success": True,
                "data": result,
                "message": f"매출 통계 조회 완료 ({start_date} ~ {end_date})"
            }
        except Exception as e:
            logger.error(f"매출 통계 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    async def get_visitor_statistics(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """방문자 통계 조회
        
        Args:
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
        
        Returns:
            방문자 통계 데이터
        """
        try:
            result = await self.repository.get_visitor_statistics(start_date, end_date)
            return {
                "success": True,
                "data": result,
                "message": f"방문자 통계 조회 완료 ({start_date} ~ {end_date})"
            }
        except Exception as e:
            logger.error(f"방문자 통계 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 종합 대시보드 서비스 ===
    
    async def get_dashboard_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """대시보드 요약 정보 조회
        
        Args:
            date: 조회 날짜 (YYYY-MM-DD, 기본값: 오늘)
        
        Returns:
            대시보드 요약 데이터
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # 병렬로 여러 데이터 조회 (repository를 통해)
            orders = await self.repository.get_orders(limit=100, start_date=date, end_date=date)
            sales = await self.repository.get_sales_statistics(date, date)
            visitors = await self.repository.get_visitor_statistics(date, date)
            products = await self.repository.get_products(limit=10)
            
            dashboard_data = {
                "orders": orders.get("orders", []),
                "sales": sales,
                "visitors": visitors,
                "recent_products": products.get("products", [])
            }

            return {
                "success": True,
                "data": dashboard_data,
                "message": f"{date} 대시보드 요약 조회 완료"
            }
        except Exception as e:
            logger.error(f"대시보드 요약 조회 오류: {e}")
            return await self._handle_api_error(e)
    
    # === 유틸리티 서비스 ===
    
    async def health_check(self) -> Dict[str, Any]:
        """API 연결 상태 확인
        
        Returns:
            연결 상태 정보
        """
        try:
            is_healthy = await self.repository.health_check()
            
            return {
                "success": True,
                "data": {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "timestamp": datetime.now().isoformat()
                },
                "message": "API 연결 상태 확인 완료"
            }
        except Exception as e:
            logger.error(f"헬스 체크 오류: {e}")
            return await self._handle_api_error(e)
    
    async def clear_cache(self) -> Dict[str, Any]:
        """캐시 초기화
        
        Returns:
            캐시 초기화 결과
        """
        try:
            self.repository.clear_cache()
            
            return {
                "success": True,
                "data": {"cache_cleared": True},
                "message": "캐시 초기화 완료"
            }
        except Exception as e:
            logger.error(f"캐시 초기화 오류: {e}")
            return await self._handle_api_error(e)
    
    async def close(self):
        """리소스 정리"""
        await self.repository.close()

# 전역 서비스 인스턴스
cafe24_service = Cafe24Service() 