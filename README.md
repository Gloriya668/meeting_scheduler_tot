Meeting Scheduler based on Tree of Thoughts (ToT)
📌 项目简介

本项目实现了一个基于 Tree of Thoughts（ToT，思维树）思想的会议安排工具。

系统通过“生成候选方案 → 评估方案 → 筛选方案 → AI选择最优方案”的流程，
自动完成会议安排。

项目结合了：

规则搜索（算法）
大语言模型（DeepSeek）

实现了一个简化版的 ToT 决策系统。

❓ 问题 1：哪些情况下适合使用 ToT？

ToT 适用于复杂、多路径、多约束的问题，例如：

数独
路径规划
会议安排

适用于：

解空间大（有很多可能方案）
需要比较多个方案
有多个约束条件
需要“生成 → 评估 → 选择”

🧠 问题 2：ToT 实现方法（代码说明）

本项目实现了一个简化版 ToT 流程：

1️⃣ 思维扩展（generate_candidates）

功能：

组合时间 × 会议室
生成多个候选方案

核心代码：

def generate_candidates(slots, rooms):
    candidates = []
    for slot in slots:
        for room in rooms:
            candidates.append({
                "time": slot["time"],
                "people": slot["people"],
                "room": room["name"],
                "capacity": room["capacity"]
            })
    return candidates

👉 对应 ToT：生成多个思维分支

2️⃣ 思维评估（evaluate_candidate）

功能：

给每个方案打分

判断是否满足人数和容量

def evaluate_candidate(candidate, required_people):
joined_count = len(candidate["people"])
capacity = candidate["capacity"]

  capacity_ok = capacity >= joined_count
  all_people_ok = joined_count >= required_people

  score = 0
  if capacity_ok:
      score += 50
  if all_people_ok:
      score += 100
  score += joined_count * 10

  return {
      "capacity_ok": capacity_ok,
      "all_people_ok": all_people_ok,
      "score": score
  }

👉 对应 ToT：评估分支

3️⃣ 思维筛选（Pruning）

功能：

删除不满足条件的方案

feasible = [
e for e in evaluated
if e["capacity_ok"] and e["all_people_ok"]
]

👉 对应 ToT：剪枝

4️⃣ 思维选择（AI选择）

功能：

让 DeepSeek 在可行方案中选择最优解

👉 对应 ToT：选择最优路径

🔁 总体流程
生成候选 → 评估 → 筛选 → AI选择
⚙️ 系统使用说明
1. 环境
Python 3.10+
2. 安装依赖
pip install openai python-dotenv
3. 配置 API Key

创建 .env 文件：

DEEPSEEK_API_KEY=你的API_KEY
4. 运行
python scheduler_ai.py
5. 输出

程序会输出：

候选方案
评分结果
可行方案
AI推荐方案
