from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine("sqlite:///comments.db")
Session = sessionmaker(bind=engine)


class CommentAnalysis(Base):
    __tablename__ = 'comments_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_text = Column(Text, nullable=False)
    commenter_account_id = Column(String(255))
    commenter_account_link = Column(String(500))
    client_account_id = Column(String(100))
    client_account_link = Column(String(500))
    client_post_id = Column(String(100))
    client_post_summary = Column(Text)

    # 🔹 Родительский комментарий (если это подкомментарий)
    parent_comment_id = Column(Integer, ForeignKey('comments_analysis.id'), nullable=True)

    # Дата последнего анализа
    last_analysis_date = Column(DateTime)

    # ===== Анализы №1–5 =====
    analysis_1_date = Column(DateTime)
    analysis_1_comment_status = Column(Enum("support", "disagree", "unclear", name="comment_status_enum"), nullable=True)
    analysis_1_against_northwest = Column(Boolean, default=False)
    analysis_1_against_shelf = Column(Boolean, default=False)
    analysis_1_against_burrup = Column(Boolean, default=False)
    analysis_1_narrative_a = Column(Boolean, default=False)
    analysis_1_narrative_b = Column(Boolean, default=False)
    analysis_1_accusation_of_lies = Column(Boolean, default=False)
    analysis_1_coordination_signs = Column(Boolean, default=False)

    analysis_2_date = Column(DateTime)
    analysis_2_comment_status = Column(Enum("support", "disagree", "unclear", name="comment_status_enum"), nullable=True)
    analysis_2_against_northwest = Column(Boolean, default=False)
    analysis_2_against_shelf = Column(Boolean, default=False)
    analysis_2_against_burrup = Column(Boolean, default=False)
    analysis_2_narrative_a = Column(Boolean, default=False)
    analysis_2_narrative_b = Column(Boolean, default=False)
    analysis_2_accusation_of_lies = Column(Boolean, default=False)
    analysis_2_coordination_signs = Column(Boolean, default=False)

    analysis_3_date = Column(DateTime)
    analysis_3_comment_status = Column(Enum("support", "disagree", "unclear", name="comment_status_enum"), nullable=True)
    analysis_3_against_northwest = Column(Boolean, default=False)
    analysis_3_against_shelf = Column(Boolean, default=False)
    analysis_3_against_burrup = Column(Boolean, default=False)
    analysis_3_narrative_a = Column(Boolean, default=False)
    analysis_3_narrative_b = Column(Boolean, default=False)
    analysis_3_accusation_of_lies = Column(Boolean, default=False)
    analysis_3_coordination_signs = Column(Boolean, default=False)

    analysis_4_date = Column(DateTime)
    analysis_4_comment_status = Column(Enum("support", "disagree", "unclear", name="comment_status_enum"), nullable=True)
    analysis_4_against_northwest = Column(Boolean, default=False)
    analysis_4_against_shelf = Column(Boolean, default=False)
    analysis_4_against_burrup = Column(Boolean, default=False)
    analysis_4_narrative_a = Column(Boolean, default=False)
    analysis_4_narrative_b = Column(Boolean, default=False)
    analysis_4_accusation_of_lies = Column(Boolean, default=False)
    analysis_4_coordination_signs = Column(Boolean, default=False)

    analysis_5_date = Column(DateTime)
    analysis_5_comment_status = Column(Enum("support", "disagree", "unclear", name="comment_status_enum"), nullable=True)
    analysis_5_against_northwest = Column(Boolean, default=False)
    analysis_5_against_shelf = Column(Boolean, default=False)
    analysis_5_against_burrup = Column(Boolean, default=False)
    analysis_5_narrative_a = Column(Boolean, default=False)
    analysis_5_narrative_b = Column(Boolean, default=False)
    analysis_5_accusation_of_lies = Column(Boolean, default=False)
    analysis_5_coordination_signs = Column(Boolean, default=False)

    # Общие поля
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
