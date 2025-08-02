# Cafe24 API Client
# 카페24 API 클라이언트 구현

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional
import logging
from cafe24_config import cafe24_config, API_ENDPOINTS, ERROR_CODES

logger = logging.getLogger(__name__)

class Cafe24APIError(Exception):
    """카페24 API 에러 클래스"""
    
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{status_code}] {message}")

class RateLimiter:
    """API 요청 제한 관리"""
    
    def __init__(self, max_requests: int = 1000, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """요청 허용 여부 확인"""
        now = time.time()
        # 시간 윈도우 밖의 요청 제거
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                return await self.acquire()
        
        self.requests.append(now)
        return True

class Cafe24APIClient:
    """카페24 API 클라이언트"""
    
    def __init__(self):
        self.config = cafe24_config
        self.rate_limiter = RateLimiter(self.config.rate_limit_per_minute)
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Dict] = {}
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds),
            headers=self.config.get_headers()
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, method: str, url: str, params: Optional[Dict] = None) -> str:
        """캐시 키 생성"""
        key_parts = [method, url]
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        return "|".join(key_parts)
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """캐시 유효성 검사"""
        if not cache_entry:
            return False
        
        cached_time = cache_entry.get("timestamp", 0)
        return time.time() - cached_time < self.config.cache_ttl_seconds
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """API 요청 실행"""
        
        if not self.config.validate_config():
            raise Cafe24APIError(401, "API 설정이 유효하지 않습니다.")
        
        url = self.config.get_api_url(endpoint)
        
        # GET 요청에 대한 캐시 확인
        if method.upper() == "GET" and use_cache:
            cache_key = self._get_cache_key(method, url, params)
            cached_data = self._cache.get(cache_key)
            if cached_data and self._is_cache_valid(cached_data):
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data["data"]
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            ) as response:
                
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = ERROR_CODES.get(response.status, "알 수 없는 오류")
                    if "error" in response_data:
                        error_details = response_data["error"]
                        error_msg = error_details.get("message", error_msg)
                    
                    raise Cafe24APIError(
                        status_code=response.status,
                        message=error_msg,
                        details=response_data
                    )
                
                # 성공적인 GET 요청 결과 캐시
                if method.upper() == "GET" and use_cache:
                    cache_key = self._get_cache_key(method, url, params)
                    self._cache[cache_key] = {
                        "data": response_data,
                        "timestamp": time.time()
                    }
                
                return response_data
        
        except aiohttp.ClientError as e:
            raise Cafe24APIError(500, f"네트워크 오류: {str(e)}")
        except json.JSONDecodeError as e:
            raise Cafe24APIError(500, f"응답 파싱 오류: {str(e)}")
    
    # === 상품 관리 API ===
    
    async def get_products(
        self,
        limit: int = 10,
        offset: int = 0,
        category_no: Optional[int] = None,
        product_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """상품 목록 조회"""
        params = {"limit": limit, "offset": offset}
        if category_no:
            params["category_no"] = category_no
        if product_name:
            params["product_name"] = product_name
        
        return await self._make_request("GET", API_ENDPOINTS["products"]["list"], params=params)
    
    async def get_product(self, product_no: int) -> Dict[str, Any]:
        """상품 상세 조회"""
        endpoint = API_ENDPOINTS["products"]["detail"].format(product_no=product_no)
        return await self._make_request("GET", endpoint)
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 생성"""
        return await self._make_request("POST", API_ENDPOINTS["products"]["create"], data=product_data)
    
    async def update_product(self, product_no: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """상품 수정"""
        endpoint = API_ENDPOINTS["products"]["update"].format(product_no=product_no)
        return await self._make_request("PUT", endpoint, data=product_data)
    
    async def delete_product(self, product_no: int) -> Dict[str, Any]:
        """상품 삭제"""
        endpoint = API_ENDPOINTS["products"]["delete"].format(product_no=product_no)
        return await self._make_request("DELETE", endpoint)
    
    # === 주문 관리 API ===
    
    async def get_orders(
        self,
        limit: int = 10,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """주문 목록 조회"""
        params = {"limit": limit, "offset": offset}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_status:
            params["order_status"] = order_status
        
        return await self._make_request("GET", API_ENDPOINTS["orders"]["list"], params=params)
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """주문 상세 조회"""
        endpoint = API_ENDPOINTS["orders"]["detail"].format(order_id=order_id)
        return await self._make_request("GET", endpoint)
    
    async def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """주문 수정"""
        endpoint = API_ENDPOINTS["orders"]["update"].format(order_id=order_id)
        return await self._make_request("PUT", endpoint, data=order_data)
    
    # === 고객 관리 API ===
    
    async def get_customers(
        self,
        limit: int = 10,
        offset: int = 0,
        member_id: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """고객 목록 조회"""
        params = {"limit": limit, "offset": offset}
        if member_id:
            params["member_id"] = member_id
        if email:
            params["email"] = email
        
        return await self._make_request("GET", API_ENDPOINTS["customers"]["list"], params=params)
    
    async def get_customer(self, member_id: str) -> Dict[str, Any]:
        """고객 상세 조회"""
        endpoint = API_ENDPOINTS["customers"]["detail"].format(member_id=member_id)
        return await self._make_request("GET", endpoint)
    
    # === 카테고리 관리 API ===
    
    async def get_categories(self) -> Dict[str, Any]:
        """카테고리 목록 조회"""
        return await self._make_request("GET", API_ENDPOINTS["categories"]["list"])
    
    async def get_category(self, category_no: int) -> Dict[str, Any]:
        """카테고리 상세 조회"""
        endpoint = API_ENDPOINTS["categories"]["detail"].format(category_no=category_no)
        return await self._make_request("GET", endpoint)
    
    # === 재고 관리 API ===
    
    async def get_inventory(self, product_no: int) -> Dict[str, Any]:
        """재고 조회"""
        endpoint = API_ENDPOINTS["inventory"]["list"].format(product_no=product_no)
        return await self._make_request("GET", endpoint)
    
    async def update_inventory(self, product_no: int, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """재고 수정"""
        endpoint = API_ENDPOINTS["inventory"]["update"].format(product_no=product_no)
        return await self._make_request("PUT", endpoint, data=inventory_data)
    
    # === 통계 API ===
    
    async def get_sales_statistics(
        self,
        start_date: str,
        end_date: str,
        group_by: str = "date"
    ) -> Dict[str, Any]:
        """매출 통계 조회"""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "group_by": group_by
        }
        return await self._make_request("GET", API_ENDPOINTS["statistics"]["sales"], params=params)
    
    async def get_visitor_statistics(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """방문자 통계 조회"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return await self._make_request("GET", API_ENDPOINTS["statistics"]["visitors"], params=params)
    
    # === 유틸리티 메서드 ===
    
    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        logger.info("API cache cleared")
    
    async def health_check(self) -> bool:
        """API 연결 상태 확인"""
        try:
            await self.get_categories()
            return True
        except Cafe24APIError:
            return False