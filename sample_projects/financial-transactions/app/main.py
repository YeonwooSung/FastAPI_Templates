import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

sys.path.append(".")
sys.path.append("..")

# custom modules
from app.api.transaction import router as transaction_router  # noqa: E402
from app.db import Base, engine  # noqa: E402


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="금융 트랜잭션 마이크로서비스",
    description="분산락과 Compare-and-Set 알고리즘 기반의 금융 트랜잭션 API",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록
app.include_router(transaction_router, tags=["transactions"])

@app.get("/health", tags=["health"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=6000, reload=True)
