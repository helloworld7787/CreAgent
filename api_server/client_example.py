"""
Simulator API 客户端调用示例

使用方式:
1. 先启动服务器（两种方式二选一）:
   
   方式1 - 从文件加载 no_provider_items:
   python -m api_server.simulator_server --config config/config.yaml --no-provider-items-path data/youtube/no_provider_items.json
   
   方式2 - 通过 HTTP 传入 no_provider_items:
   python -m api_server.simulator_server --config config/config.yaml

2. 运行此脚本: python -m api_server.client_example
"""

import requests
import json
from typing import List, Dict, Optional

BASE_URL = "http://localhost:8000"


def print_response(title: str, response):
    """格式化打印响应"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


class SimulatorClient:
    """Simulator API 客户端封装"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def load_items(self, items: List[Dict]) -> Dict:
        """
        加载无 Provider 的 Items
        
        注意: 仅当启动服务器时未指定 --no-provider-items-path 参数时使用
        
        参数:
            items: Item 列表，每个 item 包含 name, genre, tags, description
        """
        payload = {"items": items}
        response = requests.post(f"{self.base_url}/load_items", json=payload)
        response.raise_for_status()
        return response.json()
    
    def run_simulation(
        self, 
        items: Optional[List[Dict]] = None,
        rounds: Optional[int] = None,
        provider_decision_making: Optional[bool] = None
    ) -> Dict:
        """
        运行模拟
        
        参数:
            items: 可选的无 Provider Items 列表（仅当启动时未指定文件路径时使用）
            rounds: 可选的模拟轮数
            provider_decision_making: 是否启用 Provider 决策
        """
        payload = {}
        if items:
            payload["items"] = items
        if rounds:
            payload["rounds"] = rounds
        if provider_decision_making is not None:
            payload["provider_decision_making"] = provider_decision_making
        
        response = requests.post(f"{self.base_url}/run", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict:
        """获取当前模拟器状态"""
        response = requests.get(f"{self.base_url}/status")
        return response.json()
    
    def reset(self) -> Dict:
        """重置模拟器"""
        response = requests.post(f"{self.base_url}/reset")
        response.raise_for_status()
        return response.json()
    
    def save(self) -> Dict:
        """保存当前模拟器状态"""
        response = requests.post(f"{self.base_url}/save")
        response.raise_for_status()
        return response.json()


def demo_basic_usage():
    """基本使用示例"""
    client = SimulatorClient()
    
    print("\n" + "🚀" * 20)
    print("Simulator API 客户端测试")
    print("🚀" * 20)
    
    try:
        # 1. 健康检查
        health = client.health_check()
        print_response("健康检查", requests.get(f"{BASE_URL}/health"))
        
        if not health.get("simulator_initialized"):
            print("\n❌ 服务器未正确初始化!")
            return
        
        # 2. 查看状态
        print("\n>>> 查看当前状态...")
        status = client.get_status()
        print(f"✅ 模拟器状态:")
        print(f"   - 已初始化: {status['initialized']}")
        print(f"   - 当前轮次: {status['current_round']}")
        print(f"   - 总 Items: {status['total_items']}")
        print(f"   - No Provider Items: {status['no_provider_items_count']}")
        print(f"   - Items 来源: {status['no_provider_items_source']}")
        
        # 3. 如果是 HTTP 模式，加载测试数据
        if status['no_provider_items_source'] == 'http' and status['no_provider_items_count'] == 0:
            print("\n>>> 检测到 HTTP 模式，加载测试 Items...")
            test_items = [
                {
                    "name": "测试视频 1: AI 技术解析",
                    "genre": "Science & Technology",
                    "tags": ["AI", "技术", "教程"],
                    "description": "深入讲解人工智能的最新发展和应用场景"
                },
                {
                    "name": "测试视频 2: 轻松音乐合集",
                    "genre": "Music",
                    "tags": ["音乐", "放松", "钢琴"],
                    "description": "精选轻松愉快的背景音乐，适合工作学习"
                }
            ]
            result = client.load_items(test_items)
            print(f"✅ 加载成功: {result['message']}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器!")
        print("请先启动服务器:")
        print("  python -m api_server.simulator_server --config config/config.yaml")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_full_simulation():
    """完整模拟流程示例"""
    client = SimulatorClient()
    
    print("\n" + "🎮" * 20)
    print("完整模拟流程演示")
    print("🎮" * 20)
    
    try:
        # 检查服务状态
        health = client.health_check()
        if not health.get("simulator_initialized"):
            print("❌ 服务器未初始化!")
            return
        
        print(f"✅ 服务器已就绪")
        print(f"   No Provider Items 来源: {health['no_provider_items_source']}")
        print(f"   已加载 Items 数量: {health['no_provider_items_count']}")
        
        # 如果是 HTTP 模式且没有 items，先加载
        if health['no_provider_items_source'] == 'http' and health['no_provider_items_count'] == 0:
            test_items = [
                {
                    "name": "Breaking News: Tech Conference 2024",
                    "genre": "News & Politics",
                    "tags": ["news", "technology", "conference"],
                    "description": "Live coverage of the biggest tech conference of the year"
                },
                {
                    "name": "Learn Python in 10 Minutes",
                    "genre": "Education",
                    "tags": ["python", "programming", "tutorial"],
                    "description": "Quick introduction to Python programming for beginners"
                },
                {
                    "name": "Epic Gaming Highlights",
                    "genre": "Gaming",
                    "tags": ["gaming", "highlights", "esports"],
                    "description": "Best gaming moments from top streamers this week"
                }
            ]
            print("\n>>> 加载测试 Items...")
            client.load_items(test_items)
        
        # 运行模拟
        print("\n>>> 运行模拟 (5 轮)...")
        result = client.run_simulation(
            rounds=5,
            provider_decision_making=False  # 关闭 provider 决策加快速度
        )
        
        print(f"\n✅ 模拟完成!")
        print(f"   - 完成轮数: {result['rounds_completed']}")
        print(f"   - 总奖励: {result['total_reward']:.4f}")
        
        # 详细结果已包含在 /run 的返回值中
        if result.get('no_provider_items_result'):
            items_result = result['no_provider_items_result']
            summary = items_result['summary']
            
            print(f"\n📊 No Provider Items 性能汇总:")
            print(f"   - 总点击: {summary['total_clicks']}")
            print(f"   - 总曝光: {summary['total_exposures']}")
            print(f"   - 整体 CTR: {summary['overall_ctr']:.4f}")
            
            print(f"\n📈 各 Item 详细统计:")
            for item in items_result.get('detailed_items', [])[:5]:
                print(f"   - {item['name'][:35]}...")
                print(f"     点击: {item['clicks']}, 曝光: {item['exposures']}, CTR: {item['ctr']:.4f}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器!")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_http_mode():
    """
    HTTP 模式示例
    
    启动服务器时不指定文件路径:
    python -m api_server.simulator_server --config config/config.yaml
    """
    client = SimulatorClient()
    
    print("\n" + "🌐" * 20)
    print("HTTP 模式: 通过 API 传入 Items")
    print("🌐" * 20)
    
    test_items = [
        {
            "name": "HTTP 传入的测试视频",
            "genre": "Entertainment",
            "tags": ["test", "demo"],
            "description": "通过 HTTP 接口传入的测试内容"
        }
    ]
    
    try:
        # 检查状态
        status = client.get_status()
        print(f"\n当前状态:")
        print(f"   Items 来源: {status['no_provider_items_source']}")
        print(f"   已有 Items: {status['no_provider_items_count']}")
        
        if status['no_provider_items_source'] != 'http':
            print("\n⚠️  服务器以文件模式启动，Items 已从文件加载")
            print("   如需测试 HTTP 模式，请重启服务器时不指定 --no-provider-items-path")
            return
        
        # 通过 HTTP 加载 Items
        print("\n>>> 通过 /load_items 接口加载...")
        result = client.load_items(test_items)
        print(f"✅ {result['message']}")
        
        # 或者直接在运行时传入
        print("\n>>> 通过 /run 接口传入更多 Items 并运行...")
        more_items = [
            {
                "name": "运行时传入的视频",
                "genre": "Music",
                "tags": ["music"],
                "description": "在调用 /run 时传入的内容"
            }
        ]
        result = client.run_simulation(items=more_items, rounds=3)
        print(f"✅ 模拟完成! 总奖励: {result['total_reward']}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def demo_file_mode():
    """
    文件模式示例
    
    启动服务器时指定文件路径:
    python -m api_server.simulator_server --config config/config.yaml --no-provider-items-path data/youtube/no_provider_items.json
    """
    client = SimulatorClient()
    
    print("\n" + "📁" * 20)
    print("文件模式: 从文件加载 Items")
    print("📁" * 20)
    
    try:
        # 检查状态
        status = client.get_status()
        print(f"\n当前状态:")
        print(f"   Items 来源: {status['no_provider_items_source']}")
        print(f"   已有 Items: {status['no_provider_items_count']}")
        
        if status['no_provider_items_source'] != 'file':
            print("\n⚠️  服务器以 HTTP 模式启动，需要通过 API 传入 Items")
            print("   如需测试文件模式，请重启服务器并指定 --no-provider-items-path")
            return
        
        print(f"\n✅ 已从文件加载 {status['no_provider_items_count']} 个 Items")
        
        # 直接运行模拟
        print("\n>>> 直接运行模拟...")
        result = client.run_simulation(rounds=3)
        print(f"✅ 模拟完成! 总奖励: {result['total_reward']}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "full":
            demo_full_simulation()
        elif cmd == "http":
            demo_http_mode()
        elif cmd == "file":
            demo_file_mode()
        else:
            demo_basic_usage()
    else:
        demo_basic_usage()
        
        print("\n" + "-" * 60)
        print("💡 可用命令:")
        print("   python -m api_server.client_example        - 基本测试")
        print("   python -m api_server.client_example full   - 完整模拟示例")
        print("   python -m api_server.client_example http   - HTTP 模式示例")
        print("   python -m api_server.client_example file   - 文件模式示例")
        print("-" * 60)
        print("💡 启动服务器:")
        print("   文件模式: python -m api_server.simulator_server --no-provider-items-path data/youtube/no_provider_items.json")
        print("   HTTP模式: python -m api_server.simulator_server")
