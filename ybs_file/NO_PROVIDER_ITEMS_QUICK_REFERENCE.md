# 无 Provider Items 评估 - 快速参考

## 🎯 核心指标

| 指标 | 位置 | 好/坏标准 |
|------|------|---------|
| **Overall CTR** | WandB / 日志 / 报告 | >0.30 好，<0.20 差 |
| **Total Clicks** | WandB / 报告 | 越多越好 |
| **Avg Clicks per Item** | WandB / 报告 | 与 provider 比较 |
| **Top 5 Items** | 日志（每10轮） | 查看哪些最受欢迎 |

---

## 📊 查看方式

### 1. WandB（实时）
```
打开 WandB → 搜索 "no_provider_" → 查看曲线
```

### 2. 日志（每10轮）
```
查看终端或 simulation.log
找 "No Provider Items Performance"
```

### 3. 报告文件（运行后）
```
saves/no_provider_items_report.json
```

---

## 🔍 快速评估

### 步骤 1：查看整体 CTR
```bash
# 在报告文件中
"overall_ctr": 0.3571  # 如果 > 0.30，说明质量不错
```

### 步骤 2：找出问题 Items
```python
# CTR < 0.15 且曝光 > 100 的 items 需要替换
for item in report['per_item_stats']:
    if item['exposures'] > 100 and item['ctr'] < 0.15:
        print(f"Replace: {item['name']}")
```

### 步骤 3：找出优质 Items
```python
# CTR > 0.40 的 items 值得增加类似内容
for item in report['per_item_stats']:
    if item['ctr'] > 0.40:
        print(f"Add similar to: {item['name']}, Genre: {item['genre']}")
```

---

## ⚡ 常用代码片段

### 加载报告
```python
import json
with open('saves/no_provider_items_report.json', 'r') as f:
    report = json.load(f)
```

### 查看摘要
```python
print(f"Total Items: {report['summary']['total_items']}")
print(f"Overall CTR: {report['summary']['overall_ctr']:.4f}")
print(f"Total Clicks: {report['summary']['total_clicks']}")
```

### 列出 Top 5
```python
top5 = report['per_item_stats'][:5]
for i, item in enumerate(top5, 1):
    print(f"{i}. {item['name']}: CTR={item['ctr']:.4f}")
```

### 列出 Bottom 5
```python
bottom5 = report['per_item_stats'][-5:]
for i, item in enumerate(bottom5, 1):
    print(f"{i}. {item['name']}: CTR={item['ctr']:.4f} ⚠️")
```

### 按类别统计
```python
from collections import defaultdict
genre_stats = defaultdict(lambda: {'clicks': 0, 'exposures': 0})
for item in report['per_item_stats']:
    genre_stats[item['genre']]['clicks'] += item['clicks']
    genre_stats[item['genre']]['exposures'] += item['exposures']

for genre, stats in genre_stats.items():
    ctr = stats['clicks'] / stats['exposures']
    print(f"{genre}: CTR={ctr:.4f}")
```

---

## 🚨 问题诊断

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| CTR < 0.20 | 内容质量差/不匹配 | 替换低 CTR items |
| 曝光不均 | 推荐算法偏好 | 检查 item 质量 |
| 总点击少 | Items 数量少/质量差 | 增加优质 items |
| CTR 下降 | 内容过时/用户疲劳 | 更新内容 |

---

## ✅ 优化检查清单

- [ ] 整体 CTR > 0.25？
- [ ] 没有 CTR < 0.10 的 items？
- [ ] Top 5 items 占比 < 50%？（避免过度集中）
- [ ] 各类别都有代表？
- [ ] 与 provider items 的 CTR 差距 < 20%？

---

## 📞 快速联系

**详细文档**：`NO_PROVIDER_ITEMS_EVALUATION_GUIDE.md`  
**配置文档**：`data/youtube/NO_PROVIDER_ITEMS_README.md`  
**修改总结**：`MODIFICATION_SUMMARY.md`

---

## 🎯 最佳实践

1. **每 10 轮**检查日志输出
2. **运行结束**分析报告文件
3. **每次实验**比较 CTR 变化
4. **定期替换** CTR < 0.20 的 items
5. **持续优化**，迭代改进

---

**记住**：CTR > 0.30 = 优秀，0.20-0.30 = 良好，< 0.20 = 需要优化！ 🎯

