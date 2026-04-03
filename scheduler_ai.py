# scheduler_ai.py
# AI版 ToT（Tree of Thoughts）会议安排工具
# 思路：
# 1. 先生成多个候选方案
# 2. 再让 DeepSeek 对这些方案进行分析
# 3. 最后让 DeepSeek 选出最优方案并说明原因

from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import os
import json


# =========================
# 1. 初始化 DeepSeek 客户端
# =========================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有读取到 DEEPSEEK_API_KEY，请检查 .env 文件")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


# =========================
# 2. 输入数据
# =========================

available_slots = [
    {"time": "周一 10:00-11:00", "people": ["Alice", "Bob"]},
    {"time": "周一 14:00-15:00", "people": ["Alice", "Bob", "Cindy"]},
    {"time": "周二 09:00-10:00", "people": ["Bob", "Cindy"]},
    {"time": "周三 15:00-16:00", "people": ["Alice", "Cindy"]},
]

rooms = [
    {"name": "小会议室", "capacity": 2},
    {"name": "中会议室", "capacity": 3},
    {"name": "大会议室", "capacity": 5},
]

required_people = 3


# =========================
# 3. 候选方案生成（ToT 第一步）
# =========================

def generate_candidates(slots: List[Dict[str, Any]], rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


# =========================
# 4. 基础规则评估（ToT 第二步的辅助）
# =========================

def evaluate_candidate(candidate: Dict[str, Any], required_people: int) -> Dict[str, Any]:
    joined_people = candidate["people"]
    joined_count = len(joined_people)
    capacity = candidate["capacity"]

    capacity_ok = capacity >= joined_count
    all_people_ok = joined_count >= required_people

    # 简单打分
    score = 0
    if capacity_ok:
        score += 50
    else:
        score -= 100

    score += joined_count * 10

    if all_people_ok:
        score += 100

    return {
        "time": candidate["time"],
        "room": candidate["room"],
        "joined_people": joined_people,
        "joined_count": joined_count,
        "capacity": capacity,
        "capacity_ok": capacity_ok,
        "all_people_ok": all_people_ok,
        "score": score
    }


def evaluate_candidates(candidates: List[Dict[str, Any]], required_people: int) -> List[Dict[str, Any]]:
    return [evaluate_candidate(c, required_people) for c in candidates]


# =========================
# 5. 让 AI 分析所有候选方案（ToT 第三步）
# =========================

def ask_ai_to_choose_best_plan(evaluated_candidates: List[Dict[str, Any]]) -> str:
    """
    把所有候选方案交给 DeepSeek，让它像“会议安排助手”一样进行分析，
    最后输出推荐方案和理由。
    """

    system_prompt = """
你是一个专业的会议安排助手。
你的任务是从多个候选会议方案中选出最优方案。

请遵循以下原则：
1. 优先选择能够满足全部参会人数要求的方案
2. 优先选择房间容量足够的方案
3. 在满足要求的前提下，尽量选择容量更匹配、时间更合理的方案
4. 回答时请先简要分析几个方案，再明确给出“推荐方案”
5. 请用中文回答，条理清晰
"""

    user_prompt = f"""
下面是多个候选会议方案（JSON 格式）：

{json.dumps(evaluated_candidates, ensure_ascii=False, indent=2)}

请你完成以下任务：
1. 分析这些方案的优缺点
2. 选出最优方案
3. 说明你为什么这样选

输出格式建议：
- 方案分析：
- 推荐方案：
- 推荐理由：
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# =========================
# 6. 主程序
# =========================

def main():
    print("=== 第一步：生成候选方案 ===")
    candidates = generate_candidates(available_slots, rooms)

    for i, c in enumerate(candidates, start=1):
        print(
            f"{i}. 时间: {c['time']}, 房间: {c['room']}, "
            f"容量: {c['capacity']}, 可参加人: {c['people']}"
        )

    print("\n=== 第二步：规则评估每个方案 ===")
    evaluated = evaluate_candidates(candidates, required_people)

    for i, e in enumerate(evaluated, start=1):
        print(
            f"{i}. 时间: {e['time']}, 房间: {e['room']}, "
            f"参加人数: {e['joined_count']}, "
            f"容量是否足够: {e['capacity_ok']}, "
            f"是否满足全部参会人数: {e['all_people_ok']}, "
            f"得分: {e['score']}"
        )

    print("\n=== 第三步：让 AI 进行 ToT 式分析与选择 ===")
    ai_result = ask_ai_to_choose_best_plan(evaluated)

    print("\n=== AI 最终推荐 ===")
    print(ai_result)


if __name__ == "__main__":
    main()