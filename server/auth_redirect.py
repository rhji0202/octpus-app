from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn
import httpx
import os
import secrets
import base64
import hashlib
from urllib.parse import urlencode, quote
from typing import Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cafe24 OAuth Server", description="Cafe24 OAuth 인증 서버")

# Cafe24 OAuth 설정
CLIENT_ID = os.getenv("CAFE24_CLIENT_ID")
CLIENT_SECRET = os.getenv("CAFE24_CLIENT_SECRET")
REDIRECT_URI = os.getenv("CAFE24_REDIRECT_URI", "https://temple-deposits-viii-meeting.trycloudflare.com/oauth/callback")
MALL_ID = os.getenv("CAFE24_MALL_ID")
SCOPE = os.getenv("CAFE24_SCOPE", "mall.read_application,mall.read_product,mall.read_category")

@app.get("/")
async def root():
    """
    Cafe24 OAuth 인증 시작 엔드포인트
    사용자를 Cafe24 인증 페이지로 리디렉션
    """
    if not all([CLIENT_ID, MALL_ID]):
        raise HTTPException(status_code=500, detail="Missing OAuth configuration")
    
    # CSRF 방지를 위한 state 파라미터 생성
    state = secrets.token_urlsafe(32)
    
    # OAuth 인증 URL 파라미터 구성
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }

    # Cafe24 OAuth 인증 URL 구성
    auth_url = f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize?{urlencode(auth_params)}"
    
    logger.info(f"Redirecting to Cafe24 OAuth: {auth_url}")
    
    return RedirectResponse(url=auth_url)

@app.get("/oauth/authorize")
async def oauth_authorize(request: Request, use_pkce: bool = False):
    """
    Cafe24 OAuth 인증 시작 엔드포인트
    사용자를 Cafe24 인증 페이지로 리디렉션
    """
    if not all([CLIENT_ID, MALL_ID]):
        raise HTTPException(status_code=500, detail="Missing OAuth configuration")
    
    # CSRF 방지를 위한 state 파라미터 생성
    state = secrets.token_urlsafe(32)
    
    # OAuth 인증 URL 파라미터 구성
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }

    # Cafe24 OAuth 인증 URL 구성
    auth_url = f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize?{urlencode(auth_params)}"
    
    logger.info(f"Redirecting to Cafe24 OAuth: {auth_url}")
    
    return RedirectResponse(url=auth_url)

@app.get("/oauth/callback")
async def oauth_callback(
    request: Request, 
    code: Optional[str] = None, 
    state: Optional[str] = None, 
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """
    Cafe24 OAuth redirect callback endpoint
    인증 코드를 받아서 액세스 토큰으로 교환
    """
    # 에러 처리
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        return JSONResponse(
            status_code=400,
            content={
                "error": error,
                "error_description": error_description,
                "message": "OAuth 인증이 실패했습니다."
            }
        )
    
    if not code:
        return JSONResponse(
            status_code=400,
            content={"error": "authorization_code_missing", "message": "인증 코드가 없습니다."}
        )
    
    # 필수 환경변수 확인
    if not all([CLIENT_ID, CLIENT_SECRET, MALL_ID]):
        return JSONResponse(
            status_code=500,
            content={"error": "server_configuration_error", "message": "서버 설정이 올바르지 않습니다."}
        )
    
    try:
        # 토큰 교환 요청 데이터 구성
        token_data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code
        }
        
        # Cafe24 토큰 엔드포인트 호출
        token_url = f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/token"
        
        # Basic 인증 헤더 생성 (client_id:client_secret을 Base64 인코딩)
        auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                token_url,
                data=token_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth_b64}",
                    "User-Agent": "Cafe24-OAuth-Client/1.0"
                }
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                # 토큰 정보 로깅 (보안상 실제 토큰 값은 로깅하지 않음)
                logger.info(f"Successfully obtained access token for mall: {MALL_ID}")
                
                # 성공 응답
                return {
                    "success": True,
                    "message": "OAuth 인증이 성공적으로 완료되었습니다.",
                    "token_info": {
                        "access_token": token_response.get("access_token"),
                        "refresh_token": token_response.get("refresh_token"),
                        "expires_in": token_response.get("expires_in"),
                        "token_type": token_response.get("token_type", "Bearer"),
                        "scopes": token_response.get("scopes")
                    },
                    "mall_info": {
                        "mall_id": MALL_ID,
                        "client_id": CLIENT_ID
                    },
                    "state": state
                }
            else:
                # 토큰 교환 실패
                error_detail = response.text
                logger.error(f"Token exchange failed: {response.status_code} - {error_detail}")
                
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "token_exchange_failed",
                        "message": "액세스 토큰 교환에 실패했습니다.",
                        "details": {
                            "status_code": response.status_code,
                            "error_response": error_detail
                        }
                    }
                )
                
    except httpx.TimeoutException:
        logger.error("Token exchange request timed out")
        return JSONResponse(
            status_code=408,
            content={"error": "request_timeout", "message": "요청 시간이 초과되었습니다."}
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "message": f"서버 내부 오류: {str(e)}"}
        )

@app.get("/oauth/token-info")
async def token_info(access_token: str):
    """
    액세스 토큰 정보 조회
    """
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token is required")
    
    try:
        # Cafe24 API를 통해 토큰 정보 조회
        info_url = f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/tokeninfo"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                info_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Token info request failed: {response.text}"
                )
                
    except Exception as e:
        logger.error(f"Token info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    서버 상태 확인
    """
    return {
        "status": "healthy",
        "service": "Cafe24 OAuth Server",
        "config_status": {
            "client_id_configured": bool(CLIENT_ID),
            "client_secret_configured": bool(CLIENT_SECRET),
            "mall_id_configured": bool(MALL_ID),
            "redirect_uri": REDIRECT_URI
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=5000,
        log_level="info",
        reload=True
    )
