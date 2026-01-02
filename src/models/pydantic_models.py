"""
Pydantic Models for Validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class TopicRequest(BaseModel):
    topic_name: str = Field(..., min_length=1)

class TopicResponse(BaseModel):
    topic: str
    explanation: str
    youtube_links: List[Dict[str, str]]
    website_references: List[Dict[str, str]]
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Completeness of explanation (0-1)")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in explanation quality (0-1)")

class QuizRequest(BaseModel):
    topic: str
    difficulty: DifficultyLevel
    num_questions: int = Field(..., ge=1, le=50)
    total_marks: int
    marks_per_question: int

class QuestionResponse(BaseModel):
    id: int
    question: str
    type: str
    marks: int

class QuizResponse(BaseModel):
    quiz_id: str
    topic: str
    difficulty: DifficultyLevel
    questions: List[QuestionResponse]
    total_marks: int
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Completeness of quiz (0-1)")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in quiz quality (0-1)")

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    message: str
    action: str
    timestamp: str

class QueryRequest(BaseModel):
    query_type: str
    query: str
    limit: Optional[int] = 20

class QuizEvaluationRequest(BaseModel):
    quiz_id: str
    answers: Dict[str, str] = Field(..., description="Question ID to answer mapping (keys can be string or int)")
    questions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Question details")
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    marks_per_question: Optional[int] = 10
    user_id: Optional[str] = "default"
    time_taken_seconds: Optional[int] = Field(default=0, description="Time taken to complete quiz in seconds")

class QuizEvaluationResponse(BaseModel):
    quiz_id: str
    score: float = Field(..., ge=0.0, le=100.0, description="Score percentage")
    total_questions: int
    correct_answers: int
    total_marks: float
    obtained_marks: float
    feedback: List[Dict[str, Any]] = Field(default_factory=list, description="Per-question feedback")
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Completeness of evaluation (0-1)")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in evaluation (0-1)")

class SummaryResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Completeness of summary (0-1)")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in summary quality (0-1)")

class ClassificationResponse(BaseModel):
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    scores: Dict[str, float]
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Completeness of classification (0-1)")

class YouTubeProcessRequest(BaseModel):
    video_url: str = Field(..., min_length=1, description="YouTube video URL or video ID")

class YouTubeProcessResponse(BaseModel):
    success: bool
    message: str
    video_id: Optional[str] = None
    transcript_length: Optional[int] = None
    chunks_count: Optional[int] = None
    error: Optional[str] = None

class YouTubeQuestionRequest(BaseModel):
    video_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)

class YouTubeQuestionResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    question: Optional[str] = None
    video_id: Optional[str] = None
    error: Optional[str] = None

class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)

class SignInRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    token: Optional[str] = None
    error: Optional[str] = None