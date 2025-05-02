import importlib
import pkgutil
from fastapi import APIRouter

router = APIRouter()

# 현재 패키지 (routers) 내 모든 모듈을 순회
for _, module_name, _ in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    
    # 각 모듈에 `router` 객체가 정의되어 있다면 등록
    if hasattr(module, "router"):
        router.include_router(module.router)
