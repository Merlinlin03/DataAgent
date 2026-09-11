from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

# 创建查询的路由器
query_router = APIRouter()


# 注册搜索的路由
@query_router.post("/api/query")
async def search(query_schema: QuerySchema, service: QueryService=Depends(get_query_service)):

    return StreamingResponse(service.search(query_schema.query), media_type="text/event-stream")