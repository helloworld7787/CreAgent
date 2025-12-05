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


class SimulatorClient:
    """
    Simulator API 客户端封装
    
    提供对 Simulator 服务器的简洁调用接口。
    
    API 端点:
        - POST /load_items: 加载无 Provider 的 Items
        - POST /run: 运行模拟
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        参数:
            base_url: 服务器地址，默认 http://localhost:8000
        """
        self.base_url = base_url.rstrip('/')
    
    def load_items(self, items: List[Dict]) -> Dict:
        """
        加载无 Provider 的 Items
        
        注意: 
            - 仅当启动服务器时未指定 --no-provider-items-path 参数时使用
            - 如果启动时已从文件加载了 items，此接口会追加新的 items
        
        参数:
            items: Item 列表，每个 item 至少包含 description 字段
                   可选字段: name, genre, tags
                   
        示例:
            items = [
                {
                    "description": "这是一个关于AI技术的深度解析视频",  # 必填
                    "name": "AI技术解析",                              # 可选
                    "genre": "Science & Technology",                  # 可选，默认 Entertainment
                    "tags": ["AI", "技术"]                            # 可选，默认 []
                },
                {
                    "description": "轻松愉快的钢琴音乐合集"  # 只传 description 也可以
                }
            ]
        
        返回:
            {
                "success": True,
                "message": "成功加载 N 个无 Provider 的 Items",
                "loaded_count": N,
                "total_no_provider_items": M,
                "total_items": K,
                "source": "http" | "file+http"
            }
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
        
        加载逻辑:
            - 如果启动时指定了 --no-provider-items-path 从文件加载，可以直接运行
            - 如果启动时未指定路径，可以通过此接口的 items 参数传入
            - 也可以通过 items 参数追加更多 items
        
        参数:
            items: 可选的无 Provider Items 列表（仅当启动时未指定文件路径时使用）
            rounds: 可选的模拟轮数，不传则使用配置文件中的值
            provider_decision_making: 是否启用 Provider 决策，不传则使用配置
        
        返回:
            SimulationResult 结构:
            {
                "rounds_completed": int,
                "total_reward": float,
                "genre_distribution": {"genre1": count1, ...},
                "no_provider_items_result": {  # 当有 no_provider_items 时才有
                    "summary": {
                        "total_items": int,
                        "total_clicks": int,
                        "total_exposures": int,
                        "overall_ctr": float,
                        "avg_clicks_per_item": float,
                        "avg_exposures_per_item": float
                    },
                    "detailed_items": [
                        {
                            "item_id": int,
                            "name": str,
                            "genre": str,
                            "tags": List[str],
                            "description": str,
                            "clicks": int,
                            "exposures": int,
                            "ctr": float
                        },
                        ...
                    ],
                    "per_round_stats": {
                        "clicks": {round: count, ...},
                        "exposures": {round: count, ...}
                    }
                },
                "message": str
            }
        """
        payload = {}
        if items is not None:
            payload["items"] = items
        if rounds is not None:
            payload["rounds"] = rounds
        if provider_decision_making is not None:
            payload["provider_decision_making"] = provider_decision_making
        
        response = requests.post(f"{self.base_url}/run", json=payload if payload else None)
        response.raise_for_status()
        return response.json()


def print_section(title: str, char: str = "="):
    """打印分隔标题"""
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}")


def print_json(data: Dict, title: str = None):
    """格式化打印 JSON"""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def demo_basic_usage():
    """
    基本使用示例
    
    展示如何:
    1. 创建客户端
    2. 加载 Items（HTTP 模式）
    3. 运行模拟
    """
    client = SimulatorClient()
    
    print_section("基本使用示例", "🚀")
    
    try:
        # 准备测试数据 - 只有 description 是必填的
        test_items = [
            {
                "description": "深入讲解人工智能的最新发展和应用场景，包括机器学习、深度学习等核心技术",
                "name": "AI 技术深度解析",
                "genre": "Science & Technology",
                "tags": ["AI", "机器学习", "深度学习", "技术教程"]
            },
            {
                "description": "精选轻松愉快的钢琴音乐，适合工作学习时聆听",
                "name": "轻松钢琴音乐合集",
                "genre": "Music",
                "tags": ["音乐", "钢琴", "放松"]
            },
            {
                # 只传 description，其他字段使用默认值
                "description": "热门游戏精彩时刻集锦，记录最刺激的游戏瞬间"
            }
        ]
        
        # 1. 先尝试加载 Items
        print("\n📤 加载测试 Items...")
        try:
            result = client.load_items(test_items)
            print(f"✅ {result['message']}")
            print(f"   已加载 Items 总数: {result['total_no_provider_items']}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print("⚠️  模拟正在运行中，无法加载新 Items")
            else:
                raise
        
        # 2. 运行模拟 (3轮，关闭 provider 决策加快速度)
        print("\n🎮 运行模拟 (3 轮)...")
        result = client.run_simulation(
            rounds=3,
            provider_decision_making=False
        )
        
        print(f"\n✅ 模拟完成!")
        print(f"   完成轮数: {result['rounds_completed']}")
        print(f"   总奖励: {result['total_reward']:.4f}")
        
        # 3. 输出 no_provider_items 的性能
        if result.get('no_provider_items_result'):
            items_result = result['no_provider_items_result']
            summary = items_result['summary']
            
            print(f"\n📊 No Provider Items 性能汇总:")
            print(f"   总 Items: {summary['total_items']}")
            print(f"   总点击: {summary['total_clicks']}")
            print(f"   总曝光: {summary['total_exposures']}")
            print(f"   整体 CTR: {summary['overall_ctr']:.4f}")
            print(f"   平均每 Item 点击: {summary['avg_clicks_per_item']:.2f}")
            
            print(f"\n📈 各 Item 详细表现 (按点击数排序):")
            for i, item in enumerate(items_result.get('detailed_items', []), 1):
                name_display = item['name'][:30] + "..." if len(item['name']) > 30 else item['name']
                print(f"   {i}. {name_display}")
                print(f"      类别: {item['genre']} | 点击: {item['clicks']} | 曝光: {item['exposures']} | CTR: {item['ctr']:.4f}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器!")
        print("请先启动服务器:")
        print("  python -m api_server.simulator_server --config config/config.yaml")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_http_mode():
    """
    HTTP 模式详细示例
    
    适用场景: 启动服务器时不指定文件路径
    启动命令: python -m api_server.simulator_server --config config/config.yaml
    
    展示两种加载 Items 的方式:
    1. 通过 /load_items 单独加载
    2. 在调用 /run 时同时传入 items
    """
    client = SimulatorClient()
    
    print_section("HTTP 模式: 通过 API 动态传入 Items", "🌐")
    
    try:
        # 方式1: 先通过 /load_items 加载部分 items
        print("\n【方式1】通过 /load_items 接口加载...")
        
        batch1_items = [
            {
                "description": "Breaking news coverage of major tech announcements",
                "name": "Tech News Flash",
                "genre": "News & Politics",
                "tags": ["news", "technology", "breaking"]
            },
            {
                "description": "Step by step Python programming tutorial for beginners",
                "name": "Python Basics",
                "genre": "Education",
                "tags": ["python", "programming", "tutorial"]
            }
        ]
        
        result = client.load_items(batch1_items)
        print(f"✅ 加载结果: {result['message']}")
        print(f"   当前来源: {result['source']}")
        print(f"   总 no_provider_items: {result['total_no_provider_items']}")
        
        # 方式2: 在调用 /run 时同时传入更多 items
        print("\n【方式2】通过 /run 接口追加 Items 并运行...")
        
        batch2_items = [
            {
                "description": "Epic gaming moments compilation from top streamers",
                "name": "Gaming Highlights",
                "genre": "Gaming",
                "tags": ["gaming", "highlights", "esports"]
            },
            {
                "description": "Beautiful sunset timelapse from around the world",
                "name": "Sunset Timelapse",
                "genre": "Travel & Events",
                "tags": ["travel", "timelapse", "nature"]
            }
        ]
        
        result = client.run_simulation(
            items=batch2_items,
            rounds=5,
            provider_decision_making=False
        )
        
        print(f"\n✅ 模拟完成!")
        print_json(result.get('no_provider_items_result', {}).get('summary', {}), "性能汇总")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接服务器，请先启动:")
        print("  python -m api_server.simulator_server --config config/config.yaml")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_file_mode():
    """
    文件模式详细示例
    
    适用场景: 启动服务器时指定文件路径
    启动命令: python -m api_server.simulator_server --config config/config.yaml --no-provider-items-path data/youtube/no_provider_items.json
    
    Items 已从文件加载，可以直接运行模拟
    """
    client = SimulatorClient()
    
    print_section("文件模式: Items 已从文件预加载", "📁")
    
    try:
        # 文件模式下可以直接运行
        print("\n直接运行模拟 (Items 已从文件加载)...")
        
        result = client.run_simulation(
            rounds=5,
            provider_decision_making=False
        )
        
        print(f"\n✅ 模拟完成!")
        print(f"   完成轮数: {result['rounds_completed']}")
        print(f"   总奖励: {result['total_reward']:.4f}")
        print(f"   类别分布: {result['genre_distribution']}")
        
        # 详细结果
        if result.get('no_provider_items_result'):
            items_result = result['no_provider_items_result']
            
            print_json(items_result['summary'], "\n📊 性能汇总")
            
            print("\n📈 Top 5 Items:")
            for i, item in enumerate(items_result['detailed_items'][:5], 1):
                print(f"   {i}. [{item['genre']}] {item['name'][:40]}")
                print(f"      Clicks: {item['clicks']} | Exposures: {item['exposures']} | CTR: {item['ctr']:.4f}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接服务器，请先启动 (文件模式):")
        print("  python -m api_server.simulator_server --config config/config.yaml --no-provider-items-path data/youtube/no_provider_items.json")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_minimal_items():
    """
    最小化 Items 示例
    
    展示只传入必填字段 (description) 的用法
    """
    client = SimulatorClient()
    
    print_section("最小化 Items: 只传 description", "📝")
    
    try:
        # 只传 description，其他使用默认值
        minimal_items = [
            {"description": "An exciting action movie trailer with stunning visual effects"},
            {"description": "Relaxing ASMR sounds for better sleep and stress relief"},
            {"description": "Quick and easy cooking recipes for busy professionals"},
            {"description": "Fitness workout routine you can do at home without equipment"},
            {"description": "Beautiful acoustic guitar covers of popular songs"}
        ]
        
        print("\n📤 加载最小化 Items (只有 description)...")
        result = client.load_items(minimal_items)
        print(f"✅ {result['message']}")
        
        print("\n🎮 运行模拟...")
        result = client.run_simulation(rounds=3, provider_decision_making=False)
        
        print(f"\n✅ 完成! 总奖励: {result['total_reward']:.4f}")
        
        # 展示自动生成的 name
        if result.get('no_provider_items_result'):
            print("\n📋 Items 详情 (name 已自动生成):")
            for item in result['no_provider_items_result']['detailed_items']:
                print(f"   - Name: {item['name']}")
                print(f"     Genre: {item['genre']} | Clicks: {item['clicks']}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接服务器")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def demo_full_workflow():
    """
    完整工作流程示例
    
    演示一个典型的使用场景:
    1. 准备多种类型的内容
    2. 分批加载
    3. 运行多轮模拟
    4. 分析结果
    """
    client = SimulatorClient()
    
    print_section("完整工作流程演示", "🎯")
    
    try:
        # 第一批: 教育类内容
        print("\n📚 第一批: 加载教育类内容...")
        edu_items = [
            {
                "description": "Complete machine learning course covering fundamentals to advanced topics",
                "name": "ML Masterclass",
                "genre": "Education",
                "tags": ["machine learning", "AI", "course"]
            },
            {
                "description": "Web development bootcamp: HTML, CSS, JavaScript and React",
                "name": "Web Dev Bootcamp",
                "genre": "Education",
                "tags": ["web", "programming", "frontend"]
            }
        ]
        client.load_items(edu_items)
        print("✅ 教育类内容已加载")
        
        # 第二批: 娱乐类内容
        print("\n🎬 第二批: 加载娱乐类内容...")
        entertainment_items = [
            {
                "description": "Behind the scenes footage from Hollywood blockbuster",
                "name": "Movie Making Secrets",
                "genre": "Entertainment",
                "tags": ["movies", "behind scenes", "hollywood"]
            },
            {
                "description": "Stand-up comedy special featuring top comedians",
                "name": "Comedy Night",
                "genre": "Entertainment",
                "tags": ["comedy", "standup", "funny"]
            }
        ]
        client.load_items(entertainment_items)
        print("✅ 娱乐类内容已加载")
        
        # 第三批: 在运行时追加科技类内容
        print("\n🔬 第三批: 运行模拟时追加科技类内容...")
        tech_items = [
            {
                "description": "Latest smartphone comparison and review 2024",
                "name": "Phone Showdown 2024",
                "genre": "Science & Technology",
                "tags": ["tech", "smartphone", "review"]
            },
            {
                "description": "Electric vehicle technology explained: batteries and motors",
                "name": "EV Tech Deep Dive",
                "genre": "Science & Technology",
                "tags": ["EV", "technology", "automotive"]
            }
        ]
        
        # 运行模拟
        result = client.run_simulation(
            items=tech_items,
            rounds=10,
            provider_decision_making=False
        )
        
        # 分析结果
        print_section("模拟结果分析", "📊")
        
        print(f"\n🎮 模拟概况:")
        print(f"   完成轮数: {result['rounds_completed']}")
        print(f"   总奖励: {result['total_reward']:.4f}")
        
        if result.get('no_provider_items_result'):
            items_result = result['no_provider_items_result']
            summary = items_result['summary']
            
            print(f"\n📈 整体表现:")
            print(f"   总 Items 数: {summary['total_items']}")
            print(f"   总点击数: {summary['total_clicks']}")
            print(f"   总曝光数: {summary['total_exposures']}")
            print(f"   整体 CTR: {summary['overall_ctr']:.4%}")
            
            # 按类别分组统计
            genre_stats = {}
            for item in items_result['detailed_items']:
                genre = item['genre']
                if genre not in genre_stats:
                    genre_stats[genre] = {'clicks': 0, 'exposures': 0, 'count': 0}
                genre_stats[genre]['clicks'] += item['clicks']
                genre_stats[genre]['exposures'] += item['exposures']
                genre_stats[genre]['count'] += 1
            
            print(f"\n📊 按类别统计:")
            for genre, stats in sorted(genre_stats.items(), key=lambda x: x[1]['clicks'], reverse=True):
                ctr = stats['clicks'] / stats['exposures'] if stats['exposures'] > 0 else 0
                print(f"   [{genre}]")
                print(f"      Items: {stats['count']} | Clicks: {stats['clicks']} | Exposures: {stats['exposures']} | CTR: {ctr:.4%}")
            
            # 找出表现最好的内容
            best_item = items_result['detailed_items'][0]
            print(f"\n🏆 表现最佳:")
            print(f"   {best_item['name']}")
            print(f"   类别: {best_item['genre']}")
            print(f"   点击: {best_item['clicks']} | CTR: {best_item['ctr']:.4%}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接服务器")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def print_help():
    """打印帮助信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Simulator API 客户端使用说明                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  启动服务器:                                                 ║
║  ─────────────────────────────────────────────────────────   ║
║  HTTP模式 (通过API传入Items):                                ║
║    python -m api_server.simulator_server                     ║
║                                                              ║
║  文件模式 (从文件加载Items):                                 ║
║    python -m api_server.simulator_server \\                   ║
║      --no-provider-items-path data/youtube/no_provider.json  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  运行示例:                                                   ║
║  ─────────────────────────────────────────────────────────   ║
║  python -m api_server.client_example          基本示例       ║
║  python -m api_server.client_example http     HTTP模式       ║
║  python -m api_server.client_example file     文件模式       ║
║  python -m api_server.client_example minimal  最小Items      ║
║  python -m api_server.client_example full     完整流程       ║
║  python -m api_server.client_example help     显示帮助       ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  API 端点:                                                   ║
║  ─────────────────────────────────────────────────────────   ║
║  POST /load_items    加载 no_provider items                  ║
║  POST /run           运行模拟                                ║
║                                                              ║
║  Item 字段说明:                                              ║
║  ─────────────────────────────────────────────────────────   ║
║  description  (必填) Item 描述                               ║
║  name         (可选) Item 名称，默认自动生成                 ║
║  genre        (可选) Item 类别，默认 Entertainment           ║
║  tags         (可选) 标签列表，默认 []                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    import sys
    
    commands = {
        "basic": demo_basic_usage,
        "http": demo_http_mode,
        "file": demo_file_mode,
        "minimal": demo_minimal_items,
        "full": demo_full_workflow,
        "help": print_help
    }
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in commands:
            commands[cmd]()
        else:
            print(f"未知命令: {cmd}")
            print_help()
    else:
        # 默认运行基本示例
        demo_basic_usage()
        
        print("\n" + "─" * 60)
        print("💡 更多示例命令:")
        print("   python -m api_server.client_example http     HTTP模式示例")
        print("   python -m api_server.client_example file     文件模式示例")
        print("   python -m api_server.client_example minimal  最小Items示例")
        print("   python -m api_server.client_example full     完整流程演示")
        print("   python -m api_server.client_example help     显示帮助")
        print("─" * 60)
