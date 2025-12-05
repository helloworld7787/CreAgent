"""
FastAPI 客户端调用示例
运行方式: python client.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(title: str, response):
    """格式化打印响应"""
    print(f"\n{'='*50}")
    print(f"📌 {title}")
    print(f"{'='*50}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_root():
    """测试根路径"""
    response = requests.get(f"{BASE_URL}/")
    print_response("GET / - 根路径", response)


def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("GET /health - 健康检查", response)


def test_search_basic():
    """测试基本搜索"""
    payload = {
        "queries": ["什么是Python?", "机器学习入门"]
    }
    response = requests.post(
        f"{BASE_URL}/search",
        json=payload
    )
    print_response("POST /search - 基本搜索", response)


def test_search_with_options():
    """测试带选项的搜索"""
    payload = {
        "queries": ["深度学习"],
        "topk": 3,
        "return_scores": True
    }
    response = requests.post(
        f"{BASE_URL}/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print_response("POST /search - 带选项搜索", response)


def test_path_params():
    """测试路径参数"""
    # 不带查询参数
    response = requests.get(f"{BASE_URL}/items/42")
    print_response("GET /items/42 - 路径参数", response)
    
    # 带查询参数
    response = requests.get(f"{BASE_URL}/items/42?detail=true")
    print_response("GET /items/42?detail=true - 路径+查询参数", response)


def test_error_handling():
    """测试错误处理 - 发送无效数据"""
    # 发送错误类型的数据
    payload = {
        "queries": "这应该是列表而不是字符串"  # 故意发送错误类型
    }
    response = requests.post(
        f"{BASE_URL}/search",
        json=payload
    )
    print_response("POST /search - 错误数据（类型验证）", response)


def main():
    print("\n" + "🚀" * 20)
    print("FastAPI 客户端测试")
    print("🚀" * 20)
    print(f"\n服务器地址: {BASE_URL}")
    print("请确保服务器已启动 (python server.py)")
    
    try:
        # 运行所有测试
        test_root()
        test_health()
        test_search_basic()
        test_search_with_options()
        test_path_params()
        test_error_handling()
        
        print("\n" + "✅" * 20)
        print("所有测试完成!")
        print("✅" * 20 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器!")
        print("请先运行: python server.py")


if __name__ == "__main__":
    main()

