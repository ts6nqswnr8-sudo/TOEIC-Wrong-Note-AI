from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.api import router

app = FastAPI(title="TOEIC Wrong Note AI API")

# 프론트엔드 연동을 허가하기 위한 CORS 설정 구성
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실프로덕션 배포 시 구체적인 도메인 설정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
