import requests
import os
import random
from datetime import datetime

def get_daily_problem():
    url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query {
          activeDailyCodingChallengeQuestion {
            date
            link
            question {
              title
              difficulty
              topicTags { name }
            }
          }
        }
        """
    }
    res = requests.post(url, json=query, headers={"Content-Type": "application/json"})
    return res.json()["data"]["activeDailyCodingChallengeQuestion"]

def get_random_problem(difficulty):
    url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query problemsetQuestionList($filters: QuestionListFilterInput) {
          problemsetQuestionList: questionList(
            categorySlug: ""
            limit: 1000
            skip: 0
            filters: $filters
          ) {
            questions: data {
              title
              titleSlug
              difficulty
              topicTags { name }
              isPaidOnly
            }
          }
        }
        """,
        "variables": {
            "filters": {"difficulty": difficulty}
        }
    }
    res = requests.post(url, json=query, headers={"Content-Type": "application/json"})
    questions = res.json()["data"]["problemsetQuestionList"]["questions"]
    free_questions = [q for q in questions if not q["isPaidOnly"]]
    return random.choice(free_questions)

def send_to_discord(webhook_url, title, link, difficulty, tags, date=None):
    difficulty_color = {"Easy": 0x00b8a3, "Medium": 0xffc01e, "Hard": 0xff375f}
    color = difficulty_color.get(difficulty, 0xffffff)
    tag_str = ", ".join(t["name"] for t in tags) or "N/A"

    if date:
        label = f"📅 LeetCode 每日一題 — {date}"
    else:
        difficulty_label = {"EASY": "Easy", "MEDIUM": "Medium", "HARD": "Hard"}
        label = f"🎲 LeetCode 隨機題目 — {difficulty_label.get(difficulty, difficulty)}"

    payload = {
        "embeds": [{
            "title": label,
            "description": f"### [{title}]({link})",
            "color": color,
            "fields": [
                {"name": "難度", "value": difficulty, "inline": True},
                {"name": "標籤", "value": tag_str, "inline": True},
            ],
            "footer": {"text": "Good luck! 🍀"}
        }]
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    mode = os.environ.get("MODE", "daily")

    if mode == "random":
        difficulty = os.environ.get("DIFFICULTY", "MEDIUM")
        q = get_random_problem(difficulty)
        link = f"https://leetcode.com/problems/{q['titleSlug']}/"
        send_to_discord(webhook_url, q["title"], link, q["difficulty"], q["topicTags"])
    else:
        problem = get_daily_problem()
        q = problem["question"]
        link = "https://leetcode.com" + problem["link"]
        send_to_discord(webhook_url, q["title"], link, q["difficulty"], q["topicTags"], date=problem["date"])
