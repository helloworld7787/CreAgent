"""
启动命令，比如：
  python -m api_server.simulator_server --config config/config.yaml
  python -m api_server.simulator_server --config config/config.yaml --no-provider-items-path data/youtube/no_provider_items.json
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from yacs.config import CfgNode

# 将项目根目录加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.simulator import Simulator
from utils import utils


# 利用BaseModel定义的数据结构-------------------------------------------------------------------------------

class NoProviderItem(BaseModel):
    """
    单个无 Provider 的 Item 数据结构
    
    只有 description 是必填的，其他字段可选：
    - name: 如果不传，自动生成 "Item_序号"
    - genre: 如果不传，默认为 "Entertainment"
    - tags: 如果不传，默认为空列表
    """
    description: str = Field(..., description="Item 描述（必填）")
    name: Optional[str] = Field(default=None, description="Item 名称（可选，不传则自动生成）")
    genre: Optional[str] = Field(default=None, description="Item 类别（可选，默认 Entertainment）")
    tags: List[str] = Field(default=[], description="标签列表（可选，默认空列表）")


class LoadItemsRequest(BaseModel):
    """加载 No Provider Items 请求"""
    items: List[NoProviderItem] = Field(..., description="无 Provider 的 Item 列表")


class RunSimulationRequest(BaseModel):
    """运行模拟请求"""
    items: Optional[List[NoProviderItem]] = Field(default=None, description="可选：无 Provider 的 Item 列表（仅当启动时未指定文件路径时使用）")
    rounds: Optional[int] = Field(default=None, description="模拟轮数，不传则使用配置文件中的值")
    provider_decision_making: Optional[bool] = Field(default=None, description="是否启用 Provider 决策")


class SimulationStatus(BaseModel):
    """模拟状态"""
    initialized: bool
    current_round: int
    total_rounds: int
    active_agents: int
    active_providers: int
    total_items: int
    no_provider_items_count: int
    no_provider_items_source: Optional[str] = Field(
        default=None, 
        description="no_provider_items 的加载来源: 'file', 'http', 'file+http', 或 None"
    )


class NoProviderItemDetail(BaseModel):
    """单个no Provider Item 的详细信息"""
    item_id: int
    name: str
    genre: str
    tags: List[str]
    description: str
    clicks: int
    exposures: int
    ctr: float


class NoProviderItemsResult(BaseModel):
    """no Provider Items 的完整结果"""
    summary: Dict[str, Any] = Field(..., description="汇总统计")
    detailed_items: List[NoProviderItemDetail] = Field(..., description="每个 item 的详细信息，按点击数排序")
    per_round_stats: Dict[str, Dict[int, int]] = Field(..., description="每轮的点击和曝光统计")


class SimulationResult(BaseModel):
    """模拟结果"""
    rounds_completed: int
    total_reward: float
    genre_distribution: Dict[str, int]
    no_provider_items_result: Optional[NoProviderItemsResult] = Field(
        default=None, 
        description="无 Provider Items 的详细结果"
    )
    message: str


# 全局变量--------------------------------------------------------------------------------

app = FastAPI(
    title="Simulator API",
    description="推荐系统模拟器 API 服务，支持动态加载无 Provider 的 Items 并运行模拟",
    version="1.0.0"
)

# 全局模拟器实例
simulator: Optional[Simulator] = None
config: Optional[CfgNode] = None
logger: Optional[logging.Logger] = None
is_running: bool = False

# 记录 no_provider_items 的加载来源
no_provider_items_source: Optional[str] = None  # "file" 或 "http" 或 "file+http" 或 None


# 初始化函数--------------------------------------------------------------------------------

def init_simulator(config_path: str, no_provider_items_path: Optional[str] = None):
    """
    初始化模拟器
    config_path: 配置文件路径
    no_provider_items_path: no provider items 的 json 文件路径
        如果传入有效路径：从文件加载 items；  如果为空或 None：需要通过 /load_items 或 /run 接口的 http 请求传入
    """
    global simulator, config, logger, no_provider_items_source

    
    # 加载配置
    config = CfgNode(new_allowed=True)
    config.merge_from_file(config_path)
    
    # 设置logger
    logger = utils.set_logger('simulator_server.log', datetime.now().strftime('%Y%m%d_%H%M%S'))
    logger.info(f"Initializing simulator with config: {config_path}")
    
    # 确定最终使用的 no_provider_items 路径
    # 优先级: 命令行参数 > config 配置 > HTTP 模式
    config_no_provider_path = config.get("no_provider_items_path", None)
    
    if no_provider_items_path and no_provider_items_path.strip():
        # 优先用命令行参数的路径
        final_no_provider_path = no_provider_items_path
        path_source = "命令行参数"
    # elif config_no_provider_path and str(config_no_provider_path).strip():
    #     # 其次用config里面的路径
    #     final_no_provider_path = config_no_provider_path
    #     path_source = "config 配置"
    else:
        # 如果都没指定就用HTTP传
        final_no_provider_path = None
        path_source = None
    
    # 临时清除配置中的 no_provider_items_path，防止 Simulator 里面那个加载的函数自动加载
    if "no_provider_items_path" in config:
        config["no_provider_items_path"] = None
    
    # 创建模拟器实例
    simulator = Simulator(config, logger)
    simulator.load_simulator()
    simulator.play()
    
    # 恢复配置
    if config_no_provider_path:
        config["no_provider_items_path"] = config_no_provider_path
    
    # 根据最终路径决定加载方式
    loaded_items_count = 0
    
    if final_no_provider_path:
        # 从文件加载
        if not os.path.exists(final_no_provider_path):
            raise FileNotFoundError(f"no_provider_items 文件不存在: {final_no_provider_path}")
        
        simulator.data.load_no_provider_items(final_no_provider_path)
        loaded_items_count = len(simulator.data.no_provider_items)
        no_provider_items_source = "file"
        logger.info(f"从{path_source}加载了 {loaded_items_count} 个 no-provider items: {final_no_provider_path}")
    else:
        # 等待 http 请求传入
        no_provider_items_source = "http"
        logger.info("未指定 no_provider_items 路径（命令行和config均未配置），需要通过 /load_items 或 /run 接口传入 items")
    
    logger.info("Simulator initialized successfully")
    
    return {
        "config_path": config_path,
        "agent_num": config["agent_num"],
        "provider_num": config["provider_agent_num"],
        "total_rounds": config["round"],
        "no_provider_items_source": no_provider_items_source,
        "no_provider_items_path": final_no_provider_path,
        "no_provider_items_count": loaded_items_count
    }


# 辅助函数--------------------------------------------------------------------------------

def load_no_provider_items_from_list(data_obj, items: List[NoProviderItem]):
    """
    从 Pydantic 模型列表加载 no_provider_items 到 Data 对象
    
    参数:
        data_obj: Data 对象实例
        items: NoProviderItem 列表
    
    注意: 
        - description 是必填字段
        - name 如果不传，自动生成 "Item_序号"
        - genre 如果不传，默认为 "Entertainment"
        - tags 如果不传，默认为空列表
    """
    # 获取当前最大的 item id
    if len(data_obj.items) > 0:
        current_max_id = max(data_obj.items.keys())
    else:
        current_max_id = 0
    
    item_cnt = current_max_id + 1
    loaded_count = 0
    
    for item in items:
        # 处理可能没传进来的字段，设置默认值
        item_name = item.name.strip() if item.name else f"Item_{item_cnt}"
        item_genre = item.genre.strip() if item.genre else "Entertainment"
        item_tags = item.tags if item.tags else []
        item_description = item.description.strip() if item.description else ""
        
        data_obj.items[item_cnt] = {
            "name": item_name,
            "provider_name": None,
            "provider_id": None,
            "genre": item_genre,
            "upload_time": -778,  # -778 标识 no provider items
            "tags": item_tags,
            "description": item_description,
            "inter_cnt": 0,
            "mention_cnt": 0,
        }
        data_obj.no_provider_items.add(item_cnt)
        item_cnt += 1
        loaded_count += 1
    
    return loaded_count


# 接口--------------------------------------------------------------------------------

@app.post("/load_items")
def load_no_provider_items_endpoint(request: LoadItemsRequest):
    """
    通过 http 请求加载no provider items
    
    注意: 
    - 仅当启动服务时未指定 --no-provider-items-path 参数时使用
    - 如果启动时已从文件加载了 items，此接口会追加新的 items
    """
    global no_provider_items_source
    
    if simulator is None:
        raise HTTPException(status_code=500, detail="模拟器未初始化，服务启动可能失败")
    
    if is_running:
        raise HTTPException(status_code=400, detail="模拟正在运行中，无法加载新的 Items")
    
    try:
        # 记录加载前的数量
        before_count = len(simulator.data.no_provider_items)
        
        loaded_count = load_no_provider_items_from_list(simulator.data, request.items)
        logger.info(f"Loaded {loaded_count} no-provider items via HTTP API")
        
        # 更新加载来源
        if no_provider_items_source == "http" or before_count == 0:
            no_provider_items_source = "http"
        else:
            no_provider_items_source = "file+http"  # 混合来源
        
        return {
            "success": True,
            "message": f"成功加载 {loaded_count} 个无 Provider 的 Items",
            "loaded_count": loaded_count,
            "total_no_provider_items": len(simulator.data.no_provider_items),
            "total_items": len(simulator.data.items),
            "source": no_provider_items_source
        }
        
    except Exception as e:
        logger.error(f"Failed to load items: {e}")
        raise HTTPException(status_code=500, detail=f"加载 Items 失败: {str(e)}")


@app.post("/run", response_model=SimulationResult)
def run_simulation(request: RunSimulationRequest = None):
    """
    运行模拟
    
    加载逻辑:
    - 如果启动时指定了 --no-provider-items-path从文件加载，就可以直接运行
    - 如果启动时未指定路径，可以通过此接口的 items 参数传入
    - 也可以通过 items 参数追加更多 items
    """
    global is_running, no_provider_items_source
    
    if simulator is None:
        raise HTTPException(status_code=500, detail="模拟器未初始化，服务启动可能失败")
    
    if is_running:
        raise HTTPException(status_code=400, detail="模拟已在运行中")
    
    try:
        is_running = True
        
        # 检查是否需要通过 HTTP 加载 items
        current_no_provider_count = len(simulator.data.no_provider_items)
        
        # 如果请求中包含 items，加载它们
        if request and request.items:
            loaded_count = load_no_provider_items_from_list(simulator.data, request.items)
            logger.info(f"Loaded {loaded_count} no-provider items via HTTP before simulation")
            
            # 更新加载来源
            if no_provider_items_source == "http" or current_no_provider_count == 0:
                no_provider_items_source = "http"
            else:
                no_provider_items_source = "file+http"
        
        # 如果既没有从文件加载，也没有通过 HTTP 传入，给出警告
        if len(simulator.data.no_provider_items) == 0:
            logger.warning("No provider items loaded. Running simulation without no-provider items.")
        
        # 确定运行轮数
        rounds = request.rounds if request and request.rounds else config["round"]
        
        # 确定是否启用 Provider 决策
        provider_decision = request.provider_decision_making if request and request.provider_decision_making is not None else config.get("provider_decision_making", True)
        
        logger.info(f"Starting simulation for {rounds} rounds")
        
        total_reward = 0.0
        
        # 运行模拟
        for step in range(rounds):
            simulator.update_round(step)
            
            if provider_decision:
                simulator.provider_round()
            
            reward = simulator.get_user_feedbacks()
            total_reward += reward if reward else 0
            
            logger.info(f"Round {step}/{rounds} completed, reward: {reward}")
        
        # 获取结果
        no_provider_items_result = None
        if len(simulator.data.no_provider_items) > 0:
            perf = simulator.get_no_provider_items_performance()
            stats = simulator.no_provider_item_stats
            
            # 构建每个 item 的详细信息
            detailed_items = []
            for item_id in simulator.data.no_provider_items:
                item_info = simulator.data.items[item_id]
                clicks = stats['clicks'].get(item_id, 0)
                exposures = stats['exposures'].get(item_id, 0)
                ctr = clicks / exposures if exposures > 0 else 0
                
                detailed_items.append(NoProviderItemDetail(
                    item_id=item_id,
                    name=item_info['name'],
                    genre=item_info['genre'],
                    tags=item_info['tags'],
                    description=item_info['description'],
                    clicks=clicks,
                    exposures=exposures,
                    ctr=ctr
                ))
            
            # 按点击数排序
            detailed_items.sort(key=lambda x: x.clicks, reverse=True)
            
            no_provider_items_result = NoProviderItemsResult(
                summary={
                    "total_items": perf['num_items'],
                    "total_clicks": perf['total_clicks'],
                    "total_exposures": perf['total_exposures'],
                    "overall_ctr": perf['overall_ctr'],
                    "avg_clicks_per_item": perf['avg_clicks_per_item'],
                    "avg_exposures_per_item": perf['avg_exposures_per_item']
                },
                detailed_items=detailed_items,
                per_round_stats={
                    "clicks": stats['round_clicks'],
                    "exposures": stats['round_exposures']
                }
            )
        
        genre_distribution = simulator.get_genre_item_count()
        
        logger.info(f"Simulation completed. Total reward: {total_reward}")
        
        is_running = False
        
        return SimulationResult(
            rounds_completed=rounds,
            total_reward=total_reward,
            genre_distribution=genre_distribution,
            no_provider_items_result=no_provider_items_result,
            message="模拟完成"
        )
        
    except Exception as e:
        is_running = False
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"模拟运行失败: {str(e)}")



# main--------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simulator FastAPI Server")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--no-provider-items-path", type=str, default=None, help="无 Provider Items 的 JSON 文件路径。如果不指定，则需要通过 /load_items 或 /run 接口传入")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务器监听地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器监听端口")
    
    args = parser.parse_args()

    
    # 启动时就初始化模拟器，默认就先启动模拟器
    print("\n初始化模拟器ing...")
    try:
        init_info = init_simulator(config_path=args.config,no_provider_items_path=args.no_provider_items_path)
        print(" 模拟器初始化成功")
        print(f"no provider items 来源: {init_info['no_provider_items_source']}")
        if init_info['no_provider_items_source'] == 'file':
            print(f" 已加载 items 数量: {init_info['no_provider_items_count']}")
        else:
            print(f" 需要通过 /load_items 或 /run 接口传入 items")
        print("=" * 60)
    except Exception as e:
        print(f" 初始化失败: {e}")
        sys.exit(1)
    
    # 启动服务器
    uvicorn.run(app, host=args.host, port=args.port)
