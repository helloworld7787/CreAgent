from tqdm import tqdm
import time

# 示例1: 基本使用
for i in tqdm(range(100)):
    time.sleep(0.01)

# 示例2: 带描述和单位
for i in tqdm(range(10), desc="训练中", unit="epoch"):
    time.sleep(0.5)

# 示例3: 动态更新信息
pbar = tqdm(range(10), desc="训练")
for i in pbar:
    loss = 1.0 / (i + 1)
    pbar.set_postfix({'loss': f'{loss:.4f}'})
    time.sleep(0.5)

# 示例4: 手动更新
with tqdm(total=100, desc="下载") as pbar:
    for i in range(10):
        time.sleep(0.1)
        pbar.update(10)  # 每次更新10

# 示例5: 嵌套进度条
for i in tqdm(range(3), desc="外层", position=0):
    for j in tqdm(range(5), desc="内层", position=1, leave=False):
        time.sleep(0.5)