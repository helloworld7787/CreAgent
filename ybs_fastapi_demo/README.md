# FastAPI Demo

一个简单的 FastAPI 示例项目，包含服务器和客户端。

## 文件结构

```
fastapi_demo/
├── server.py    # FastAPI 服务器
├── client.py    # 客户端调用示例
└── README.md    # 说明文档
```

## 安装依赖

```bash
pip install fastapi uvicorn requests
```

## 运行方式

### 1. 启动服务器

```bash
cd fastapi_demo
python server.py
```

服务器将在 http://localhost:8000 启动

### 2. 查看 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 运行客户端测试

打开新终端:

```bash
cd fastapi_demo
python client.py
```

## API 端点说明

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 欢迎信息 |
| GET | `/health` | 健康检查 |
| POST | `/search` | 搜索接口 |
| GET | `/items/{item_id}` | 路径参数示例 |

## 搜索接口示例

**请求:**

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["什么是Python?"],
    "topk": 3,
    "return_scores": true
  }'
```

**响应:**

```json
{
  "results": [
    {
      "query": "什么是Python?",
      "documents": [
        {"title": "Document 1...", "content": "...", "score": 1.0},
        {"title": "Document 2...", "content": "...", "score": 0.9},
        {"title": "Document 3...", "content": "...", "score": 0.8}
      ]
    }
  ],
  "total": 1
}
```

