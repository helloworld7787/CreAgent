import json

# 读取最终摘要 - 应该读取 JSON 文件而非 .wandb 二进制文件
# 将路径改为 wandb-summary.json 文件
json_path = 'C:/Users/ybsss/Desktop/wandb/offline-run-xxx/files/wandb-summary.json'

with open(json_path, 'r', encoding='utf-8') as f:  # 添加 encoding='utf-8'
    summary = json.load(f)
    print(f"最终摘要: {summary}")
    if 'total_rewards' in summary:
        print(f"最终奖励: {summary['total_rewards']}")