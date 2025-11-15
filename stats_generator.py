# stats_generator.py
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_model import CommentAnalysis, Base

# Подключаемся к базе
engine = create_engine("sqlite:///comments.db")
Session = sessionmaker(bind=engine)
session = Session()


def calculate_percentage(part, whole):
    """Вычисляем процент с округлением до 2 знаков"""
    return round((part / whole) * 100, 2) if whole > 0 else 0.0


def generate_statistics(analysis_round=1):
    """
    Генерирует статистику по каждому посту для указанного раунда анализа (1–5).
    """
    prefix = f"analysis_{analysis_round}_"

    comments = session.query(CommentAnalysis).filter(
        getattr(CommentAnalysis, f"{prefix}comment_status").isnot(None)
    ).all()

    posts = {}
    for c in comments:
        post = c.client_post_summary or "Unknown Post"
        post_url = getattr(c, "client_post_id", None) or "URL not available"

        if post not in posts:
            posts[post] = {
                "post_url": post_url,
                "total_comments": 0,
                "support": 0,
                "disagree": 0,
                "unclear": 0,
                "against_northwest": 0,
                "against_shelf": 0,
                "against_burrup": 0,
                "narrative_a": 0,
                "narrative_b": 0,
                "accusation_of_lies": 0,
                "coordination_signs": 0
            }

        post_data = posts[post]
        post_data["total_comments"] += 1

        # sentiment
        status = getattr(c, f"{prefix}comment_status", "").lower()
        if "support" in status:
            post_data["support"] += 1
        elif "disagree" in status:
            post_data["disagree"] += 1
        else:
            post_data["unclear"] += 1

        # boolean flags
        for field in [
            "against_northwest",
            "against_shelf",
            "against_burrup",
            "narrative_a",
            "narrative_b",
            "accusation_of_lies",
            "coordination_signs"
        ]:
            if getattr(c, f"{prefix}{field}", False):
                post_data[field] += 1

    # Подсчёт процентов
    result = {}
    for post, data in posts.items():
        total = data["total_comments"]
        result[post] = {
            "post_url": data["post_url"],
            "total_comments": total,
            "sentiment": {
                "support_%": calculate_percentage(data["support"], total),
                "disagree_%": calculate_percentage(data["disagree"], total),
                "unclear_%": calculate_percentage(data["unclear"], total)
            },
            "targets": {
                "against_northwest_%": calculate_percentage(data["against_northwest"], total),
                "against_shelf_%": calculate_percentage(data["against_shelf"], total),
                "against_burrup_%": calculate_percentage(data["against_burrup"], total)
            },
            "narratives": {
                "narrative_a_%": calculate_percentage(data["narrative_a"], total),
                "narrative_b_%": calculate_percentage(data["narrative_b"], total)
            },
            "accusations_and_coordination": {
                "accusation_of_lies_%": calculate_percentage(data["accusation_of_lies"], total),
                "coordination_signs_%": calculate_percentage(data["coordination_signs"], total)
            }
        }

    return result


if __name__ == "__main__":
    import sys
    from datetime import datetime

    if len(sys.argv) > 1:
        try:
            round_num = int(sys.argv[1])
        except ValueError:
            print("❌ Ошибка: аргумент должен быть числом от 1 до 5")
            sys.exit(1)
    else:
        round_num = 1  # значение по умолчанию

    # Генерируем статистику
    stats = generate_statistics(round_num)

    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_stats_round_{round_num}_{timestamp}.json"

    # Сохраняем в файл
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

    print(f"✅ Статистика успешно сохранена в файл: {filename}")
