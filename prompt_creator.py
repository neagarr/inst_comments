from db_model import Session, CommentAnalysis
session = Session()


# Вводное начало для нейросети
INSTRUCTION = """
You are an AI assistant for analyzing social media comments. 
You will be given a comment (or a chain of comments) and the post summary it belongs to
Some comments may be replies to other comments (child comments). 
You must analyze each comment individually but take into account the full context:
- for parent comments: use the post summary;
- for child comments: use the post summary plus all parent comments in the chain.
Your goal is to classify the sentiment, detect targeted mentions, and identify specific narratives or patterns of coordination.
"""

# Описание структуры входных данных
INPUT_DESCRIPTION = """
The input data is provided as text in the following format:
- "Post Summary": a short summary of the original post.
- "Comment Text": the text of the comment.
- "Parent Comments": (optional) concatenated text of all parent comments, in order from top to immediate parent.
"""

# Формат JSON, который мы хотим получить
JSON_FORMAT = """
Answer in the following JSON format:
{
  "comment_status": "support / disagree / unclear",
  "against_northwest": true/false,
  "against_shelf": true/false,
  "against_burrup": true/false,
  "narrative_a": true/false,
  "narrative_b": true/false,
  "accusation_of_lies": true/false,
  "coordination_signs": true/false
}
"""

# Нарративы, которые используются для анализа
NARRATIVES = {
    "narrative_a": "Existing and planned Woodside assets are inconsistent with international climate targets and the 1.5°C pathway",
    "narrative_b": "Discussions about shareholders, ownership, or corporate interests"
}

# Список детальных вопросов для ChatGPT
QUESTIONS = [
    # sentiment
    "Based on the comment and the post context, classify the sentiment of this comment: support, disagree, or unclear. -> comment_status",
    
    # targeting specific entities
    "Does the comment criticize NorthWest Shelf? -> against_northwest",
    "Does the comment criticize Woodside? -> against_shelf",
    "Does the comment criticize Burrup Hub? -> against_burrup",
    
    # narratives
    f"Does the comment express Narrative A: '{NARRATIVES['narrative_a']}'? -> narrative_a",
    f"Does the comment express Narrative B: '{NARRATIVES['narrative_b']}'? -> narrative_b",
    
    # accusation of lies
    "Does the comment accuse the post author of lying, providing misleading information, fake news, or incorrect statistics? -> accusation_of_lies",
    
    # coordination signs
    "Are there signs that this comment is coordinated with other comments, or posted by non-authentic accounts? -> coordination_signs"
]

def format_parent_comments(parent_comments_list):
    """
    Форматируем цепочку родительских комментариев с табуляцией.
    parent_comments_list: список строк вида "@account_id: текст"
    Возвращает одну строку с красивой иерархией и кавычками вокруг текста.
    """
    formatted = ""
    for depth, comment in enumerate(parent_comments_list, start=1):
        tab = "----" * depth  
        if ": " in comment:
            account, text = comment.split(": ", 1)
            formatted += f"{tab}{account}: \"{text.strip()}\"\n"
        else:
            formatted += f"{tab}{comment}\n"
    return formatted.strip()


def prompt_constructor(comment_text, comment_account_id, post_summary, parent_comments=None):
    """
    Формирует полный промпт для ChatGPT с учётом комментария, поста и родительских комментариев.
    """
    parent_text = format_parent_comments(parent_comments) if parent_comments else "None"

    # Форматируем текущий комментарий
    comment_text_formatted = f"@{comment_account_id}: \"{comment_text.strip()}\""

    prompt = f"""
INPUT DATA:

Post Summary:
"{post_summary}"

Parent Comments:
{parent_text}

Comment Text:
{comment_text_formatted}

{INPUT_DESCRIPTION}

Questions to answer:
- {"\n- ".join(QUESTIONS)}

{JSON_FORMAT}
"""
    return prompt.strip()


def build_prompt_for_comment_by_id(comment_id):
    """
    Формирует промпт для конкретного комментария с учётом цепочки родителей.
    """
    comment = session.query(CommentAnalysis).filter_by(id=comment_id).first()
    if not comment:
        raise ValueError(f"Comment with id={comment_id} not found")

    # собираем родительские комментарии по цепочке
    parent_comments = []
    current = comment
    while current.parent_comment_id:
        parent = session.query(CommentAnalysis).filter_by(id=current.parent_comment_id).first()
        if parent:
            parent_comments.append(f"@{parent.commenter_account_id}: {parent.comment_text}")
            current = parent
        else:
            break
    # разворачиваем чтобы идти сверху вниз
    parent_comments.reverse()

    # создаём промпт
    prompt = prompt_constructor(
        comment_text=comment.comment_text,
        comment_account_id=comment.commenter_account_id,  # <-- добавляем
        post_summary=comment.client_post_summary,
        parent_comments=parent_comments if parent_comments else None
    )

    return prompt

if __name__ == "__main__":
    # пример использования
    test_comment_id = 26  # замените на реальный ID комментария
    prompt = build_prompt_for_comment_by_id(test_comment_id)
    print(prompt)