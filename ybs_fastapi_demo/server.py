"""
FastAPI 最小示例服务器
运行方式: python server.py
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn


# ============ 1. 定义请求/响应模型 ============

class QueryRequest(BaseModel):
    """请求体模型"""
    queries: List[str]              # 必填：查询列表
    topk: Optional[int] = 5         # 可选：返回数量，默认5
    return_scores: bool = False     # 可选：是否返回分数


class QueryResponse(BaseModel):
    """响应体模型"""
    results: List[dict]
    total: int


# ============ 2. 创建 FastAPI 应用 ============

app = FastAPI(
    title="检索服务 Demo",
    description="一个简单的 FastAPI 示例",
    version="1.0.0"
)


# ============ 3. 定义 API 端点 ============

@app.get("/")
def root():
    """根路径 - 欢迎信息"""
    return {"message": "Welcome to FastAPI Demo!", "docs": "/docs"}


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.post("/search", response_model=QueryResponse)
def search(request: QueryRequest):
    """
    搜索端点 - 模拟检索功能
    
    请求示例:
    {
        "queries": ["什么是Python?", "机器学习入门"],
        "topk": 3,
        "return_scores": true
    }
    """
    results = []
    
    for i, query in enumerate(request.queries):
        # 模拟检索结果
        query_results = []
        for j in range(request.topk):
            item = {
                "title": f"Document {j+1} for '{query}'",
                "content": f"This is the content of document {j+1} matching query: {query}",
            }
            if request.return_scores:
                item["score"] = round(1.0 - j * 0.1, 2)  # 模拟分数
            query_results.append(item)
        
        results.append({
            "query": query,
            "documents": query_results
        })
    
    return QueryResponse(results=results, total=len(results))


@app.get("/items/{item_id}")
def get_item(item_id: int, detail: bool = False):
    """
    路径参数示例
    
    - item_id: 从URL路径获取
    - detail: 从查询参数获取 (?detail=true)
    """
    response = {"item_id": item_id}
    if detail:
        response["detail"] = f"Detailed info for item {item_id}"
    return response


# ============ 4. 启动服务器 ============

if __name__ == "__main__":
    print("=" * 50)
    print("FastAPI Demo Server")
    print("=" * 50)
    print("API 文档: http://localhost:8000/docs")
    print("ReDoc 文档: http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

