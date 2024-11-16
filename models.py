from pydantic import BaseModel
from typing import List, Dict


class AIKSUpdate(BaseModel):
    abilities: List[str] = []
    interests: List[str] = []
    knowledge: List[str] = []
    skills: List[str] = []
    suggested_options: List[str] = []


class AssessmentResponse(BaseModel):
    next_question: str
    analysis: str
    aiks_updates: AIKSUpdate
    suggested_options: List[str]


class Profession(BaseModel):
    title: str
    explanation: str
    required_skills: List[str]
    aiks_alignment: Dict[str, List[str]]
    daily_life_example: str


class ProfessionResponse(BaseModel):
    professions: List[Profession]
