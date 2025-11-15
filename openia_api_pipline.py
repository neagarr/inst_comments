# import json
# from datetime import datetime
# from openai import OpenAI
# from db_model import Session, CommentAnalysis
# from prompt_creator import build_prompt_for_comment_by_id, INSTRUCTION

# from config import API_KEY, MODEL_NAME

# # Создаём клиент OpenAI
# client = OpenAI(api_key=API_KEY)
# session = Session()

# def analyze_comment(comment):
#     """
#     Анализ одного комментария через ChatGPT.
#     Возвращает словарь с результатами анализа.
#     """
#     # Строим промпт
#     prompt = build_prompt_for_comment_by_id(comment.id)

#     # Отправляем в OpenAI
#     messages = [
#         {"role": "system", "content": INSTRUCTION},
#         {"role": "user", "content": prompt}
#     ]
#     response = client.chat.completions.create(
#         model=MODEL_NAME,
#         messages=messages,
#         temperature=0,
#         max_tokens=1000
#     )

#     answer_text = response.choices[0].message.content

#     # Парсим JSON из ответа
#     try:
#         result = json.loads(answer_text)
#     except json.JSONDecodeError:
#         print(f"Ошибка парсинга JSON для комментария id={comment.id}")
#         print("Ответ ChatGPT:", answer_text)
#         return None

#     return result


# def run_pipeline(analysis_round: int = 1):
#     """
#     Проходит по всем комментариям, которые ещё не анализировались, 
#     и сохраняет результаты в поля analysis_{analysis_round}_*.

#     :param analysis_round: номер этапа анализа (1–5)
#     """
#     assert 1 <= analysis_round <= 5, "analysis_round должен быть в диапазоне от 1 до 5"

#     # Берём комментарии без анализа (например, last_analysis_date is NULL)
#     comments_to_analyze = session.query(CommentAnalysis).filter(
#         CommentAnalysis.last_analysis_date.is_(None)
#     ).all()

#     print(f"Найдено {len(comments_to_analyze)} комментариев для анализа (раунд {analysis_round}).")

#     for comment in comments_to_analyze:
#         print(f"Анализируем комментарий id={comment.id}")
#         analysis_result = analyze_comment(comment)
#         if not analysis_result:
#             continue

#         # Формируем имена полей динамически
#         prefix = f"analysis_{analysis_round}_"

#         setattr(comment, prefix + "date", datetime.utcnow())
#         setattr(comment, prefix + "comment_status", analysis_result.get("comment_status"))
#         setattr(comment, prefix + "against_northwest", analysis_result.get("against_northwest", False))
#         setattr(comment, prefix + "against_shelf", analysis_result.get("against_shelf", False))
#         setattr(comment, prefix + "against_burrup", analysis_result.get("against_burrup", False))
#         setattr(comment, prefix + "narrative_a", analysis_result.get("narrative_a", False))
#         setattr(comment, prefix + "narrative_b", analysis_result.get("narrative_b", False))
#         setattr(comment, prefix + "accusation_of_lies", analysis_result.get("accusation_of_lies", False))
#         setattr(comment, prefix + "coordination_signs", analysis_result.get("coordination_signs", False))

#         # Обновляем дату последнего анализа
#         comment.last_analysis_date = datetime.utcnow()

#         # Сохраняем изменения
#         session.add(comment)
#         session.commit()
#         print(f"Комментарий id={comment.id} успешно сохранён (раунд {analysis_round}).")


# if __name__ == "__main__":
#     import sys

#     if len(sys.argv) > 1:
#         try:
#             round_num = int(sys.argv[1])
#         except ValueError:
#             print("❌ Ошибка: аргумент должен быть числом от 1 до 5")
#             sys.exit(1)
#     else:
#         round_num = 1  # значение по умолчанию

#     run_pipeline(round_num)


import asyncio
import json
from datetime import datetime
from openai import AsyncOpenAI
from db_model import Session, CommentAnalysis
from prompt_creator import build_prompt_for_comment_by_id, INSTRUCTION
from config import API_KEY, MODEL_NAME

# создаём асинхронного клиента
client = AsyncOpenAI(api_key=API_KEY)
session = Session()

async def analyze_comment_async(comment):
    """
    Асинхронный анализ одного комментария через ChatGPT API.
    """
    prompt = build_prompt_for_comment_by_id(comment.id)
    messages = [
        {"role": "system", "content": INSTRUCTION},
        {"role": "user", "content": prompt}
    ]

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0,
            max_tokens=1000,
        )
        answer_text = response.choices[0].message.content
        return json.loads(answer_text)
    except Exception as e:
        print(f"❌ Ошибка при анализе id={comment.id}: {e}")
        return None


async def run_pipeline_async(analysis_round: int = 1, max_concurrent: int = 3):
    """
    Асинхронный пайплайн анализа.
    max_concurrent — сколько запросов одновременно (ограничение для стабильности)
    """
    comments_to_analyze = session.query(CommentAnalysis).filter(
        CommentAnalysis.last_analysis_date.is_(None)
    ).all()

    print(f"Найдено {len(comments_to_analyze)} комментариев для анализа (раунд {analysis_round}).")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_comment(comment):
        async with semaphore:
            result = await analyze_comment_async(comment)
            if not result:
                return
            prefix = f"analysis_{analysis_round}_"
            setattr(comment, prefix + "date", datetime.utcnow())
            setattr(comment, prefix + "comment_status", result.get("comment_status"))
            setattr(comment, prefix + "against_northwest", result.get("against_northwest", False))
            setattr(comment, prefix + "against_shelf", result.get("against_shelf", False))
            setattr(comment, prefix + "against_burrup", result.get("against_burrup", False))
            setattr(comment, prefix + "narrative_a", result.get("narrative_a", False))
            setattr(comment, prefix + "narrative_b", result.get("narrative_b", False))
            setattr(comment, prefix + "accusation_of_lies", result.get("accusation_of_lies", False))
            setattr(comment, prefix + "coordination_signs", result.get("coordination_signs", False))
            comment.last_analysis_date = datetime.utcnow()
            session.add(comment)
            session.commit()
            print(f"✅ Комментарий id={comment.id} обработан")

    await asyncio.gather(*[process_comment(c) for c in comments_to_analyze])


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        try:
            round_num = int(sys.argv[1])
        except ValueError:
            print("❌ Ошибка: аргумент должен быть числом от 1 до 5")
            sys.exit(1)
    else:
        round_num = 1

    asyncio.run(run_pipeline_async(round_num))