# 无 Provider Items 功能说明

## 功能概述

此功能允许系统加载没有关联创作者（provider）的物品（items），这些物品将与创作者生产的内容一起参与推荐流程。

## 使用方法

### 1. 配置文件设置

在 `config/config.yaml` 中，已添加以下配置项：

```yaml
# path for items without providers (optional, can be empty string or null to skip)
no_provider_items_path: data/youtube/no_provider_items.json
```

- 如果想使用此功能，设置为有效的 JSON 文件路径
- 如果不使用，可以设置为空字符串 `""` 或 `null`，或者注释掉该行

### 2. 数据文件格式

无 provider items 的 JSON 文件格式如下：

```json
[
    {
        "name": "物品名称",
        "genre": "类别",
        "tags": ["标签1", "标签2", "标签3"],
        "description": "物品描述文本"
    },
    {
        "name": "另一个物品",
        "genre": "Entertainment",
        "tags": ["tag1", "tag2"],
        "description": "这是物品的详细描述"
    }
]
```

#### 字段说明：

- **name** (必填): 物品的标题/名称
- **genre** (必填): 物品的类别，必须是以下之一：
  - 'Film & Animation'
  - 'Autos & Vehicles'
  - 'Music'
  - 'Pets & Animals'
  - 'Sports'
  - 'Travel & Events'
  - 'Gaming'
  - 'People & Blogs'
  - 'Comedy'
  - 'Entertainment'
  - 'News & Politics'
  - 'Howto & Style'
  - 'Education'
  - 'Science & Technology'
  - 'Nonprofits & Activism'
- **tags** (可选): 标签列表，可以为空数组 `[]`
- **description** (必填): 物品的详细描述

### 3. 示例文件

系统已提供示例文件：`data/youtube/no_provider_items.json`

该文件包含 10 个不同类别的示例物品，可以直接使用或作为模板修改。

## 技术实现

### 核心修改

1. **Data 类** (`recommender/data/data.py`):
   - 添加 `no_provider_items` 集合来追踪无 provider 的物品
   - 新增 `load_no_provider_items()` 方法加载数据
   - 新增 `has_provider()` 方法检查物品是否有 provider

2. **Simulator 类** (`simulator/simulator.py`):
   - 在 `load_simulator()` 中自动加载无 provider items
   - 修改 `update_exposure_to_providers()` 和 `update_click_to_providers()` 方法，跳过无 provider 的物品

### 工作流程

1. **初始化阶段**：
   - 系统启动时，先加载 providers 及其物品
   - 然后加载无 provider items（如果配置了路径）
   - 所有物品统一存储在 `self.data.items` 中

2. **推荐阶段**：
   - 推荐系统同等对待有/无 provider 的物品
   - 用户可以浏览和点击所有物品

3. **反馈阶段**：
   - 有 provider 的物品：点击和曝光数据会反馈给对应创作者
   - 无 provider 的物品：不会尝试更新 provider 信息（自动跳过）

## 注意事项

1. **ID 分配**：无 provider items 的 ID 会从现有最大 item ID 之后开始分配
2. **初始化时间**：所有无 provider items 的 `upload_time` 设为 `-999`，表示系统初始化时就存在
3. **不参与反馈循环**：这些物品不会影响创作者的决策，因为它们没有关联的创作者
4. **推荐权重**：在推荐算法中，无 provider items 与有 provider items 享有相同的推荐权重

## 使用场景

此功能适用于：

- **测试场景**：测试推荐系统在混合内容源下的表现
- **冷启动**：为新系统提供初始内容
- **对照实验**：与创作者生成的内容进行对比
- **内容补充**：填补某些类别的内容空缺
- **基准内容**：提供稳定的基准内容用于评估

## 禁用此功能

如果不需要无 provider items，有以下几种方式：

1. 在 `config.yaml` 中设置为空：
   ```yaml
   no_provider_items_path: ""
   ```

2. 或设置为 null：
   ```yaml
   no_provider_items_path: null
   ```

3. 或注释掉该配置项

系统会自动跳过加载，不会报错。

## 常见问题

**Q: 无 provider items 会出现在推荐列表中吗？**
A: 是的，它们会和其他物品一起参与推荐。

**Q: 用户点击这些物品会发生什么？**
A: 系统会正常记录点击行为用于训练推荐模型，但不会将反馈发送给任何创作者。

**Q: 这些物品会影响创作者的收益吗？**
A: 不会直接影响。它们会占用一部分推荐位置，但不会直接改变创作者的点击数据。

**Q: 可以在运行过程中添加无 provider items 吗？**
A: 当前实现只在系统初始化时加载。如果需要动态添加，需要额外开发功能。

**Q: 无 provider items 的数量有限制吗？**
A: 没有硬性限制，但建议保持合理数量以避免影响系统性能。

