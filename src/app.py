"""
Simple AI Teacher Agent Backend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from pathlib import Path
import io
import hashlib
import secrets

import sys

# Gemini API Key (hardcoded)
GEMINI_API_KEY = "[enter api here]"
print(f"✓ GEMINI_API_KEY configured: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.db import init_db, get_db_connection
from src.models.pydantic_models import (
    TopicRequest, TopicResponse, QuizRequest, QuizResponse,
    ChatRequest, ChatResponse, QueryRequest,
    QuizEvaluationRequest, QuizEvaluationResponse,
    SummaryResponse, ClassificationResponse,
    YouTubeProcessRequest, YouTubeProcessResponse,
    YouTubeQuestionRequest, YouTubeQuestionResponse,
    SignUpRequest, SignInRequest, AuthResponse
)
from src.agent import AIAgent

# Setup - Use your own database file
try:
    from config import DB_PATH, STUDENT_DB_PATH
except ImportError:
    from src.config import DB_PATH, STUDENT_DB_PATH

# Ensure STUDENT_DB_PATH is defined
try:
    STUDENT_DB_PATH
except NameError:
    STUDENT_DB_PATH = None

init_db(DB_PATH)

# Initialize student database if path is configured
try:
    from src.database.student_db import init_student_db
    from pathlib import Path
    if STUDENT_DB_PATH:
        # Ensure directory exists
        Path(STUDENT_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        # Initialize student database
        init_student_db(STUDENT_DB_PATH)
        print(f"Student database initialized at: {STUDENT_DB_PATH}")
    else:
        print("Warning: STUDENT_DB_PATH not configured, student database features disabled")
except Exception as e:
    print(f"Warning: Could not initialize student database: {e}")
    STUDENT_DB_PATH = None

# Initialize agent with student database
agent = AIAgent(DB_PATH, STUDENT_DB_PATH)

# Create app
app = FastAPI(title="AI Teacher Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"service": "AI Teacher Agent", "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/topics/explain", response_model=TopicResponse)
def explain_topic(request: TopicRequest):
    """Get topic explanation with validation"""
    try:
        # #region agent log
        import json
        import time
        try:
            with open(r'c:\Users\Shoaib Ahmad\OneDrive\Desktop\AI\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"src/app.py:97","message":"API: Received explain request","data":{"topicName":request.topic_name[:150]},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + '\n')
        except: pass
        # #endregion
        result = agent.explain_topic(request.topic_name)
        
        # Validate with Pydantic
        validated = TopicResponse(**result)
        
        # Log query and output
        conn = get_db_connection(DB_PATH)
        conn.execute(
            "INSERT INTO topic_queries (topic_name, timestamp, student_id) VALUES (?, ?, ?)",
            (request.topic_name, datetime.now().isoformat(), "default")
        )
        # Log output/report
        conn.execute(
            """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp) 
               VALUES (?, ?, ?, ?, ?)""",
            ("topic_explanation", request.topic_name, 
             f"Generated explanation with completeness: {validated.completeness_score}, confidence: {validated.confidence_score}",
             validated.confidence_score, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        return validated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quiz/generate", response_model=QuizResponse)
def generate_quiz(request: QuizRequest):
    """Generate quiz with validation - only AI topics allowed"""
    try:
        # Validate that topic is AI-related
        from src.utils.ai_topics import is_ai_topic
        
        if not is_ai_topic(request.topic):
            raise HTTPException(
                status_code=400,
                detail=f"Quiz generation is only available for AI-related topics. '{request.topic}' is not recognized as an AI topic. Please enter an AI-related topic such as Machine Learning, Deep Learning, Neural Networks, Natural Language Processing, etc."
            )
        
        result = agent.generate_quiz(
            request.topic, request.num_questions, 
            request.difficulty, request.marks_per_question
        )
        
        # Validate with Pydantic
        validated = QuizResponse(**result)
        
        # Log generation and output
        conn = get_db_connection(DB_PATH)
        conn.execute(
            """INSERT INTO quiz_generations 
               (topic, difficulty, num_questions, total_marks, timestamp, student_id) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (request.topic, request.difficulty, request.num_questions,
             validated.total_marks, datetime.now().isoformat(), "default")
        )
        # Log agent decision
        conn.execute(
            """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp) 
               VALUES (?, ?, ?, ?, ?)""",
            ("quiz_generation", request.topic,
             f"Generated {len(validated.questions)} questions with completeness: {validated.completeness_score}",
             validated.confidence_score, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        return validated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quiz/generate-from-pdf", response_model=QuizResponse)
async def generate_quiz_from_pdf(
    pdf_file: UploadFile = File(...),
    difficulty: str = Form(...),
    num_questions: int = Form(...),
    total_marks: int = Form(...),
    marks_per_question: int = Form(...)
):
    """Generate quiz from uploaded PDF file"""
    try:
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read PDF file content
        pdf_content = await pdf_file.read()
        
        # Extract text from PDF
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
            
            if not pdf_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from PDF. The PDF might be image-based or encrypted.")
        except ImportError:
            raise HTTPException(status_code=500, detail="PDF processing library not installed. Please install PyPDF2.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
        
        # Generate quiz from PDF content using agent
        result = agent.generate_quiz_from_pdf(
            pdf_text, num_questions, difficulty, marks_per_question
        )
        
        # Validate with Pydantic
        validated = QuizResponse(**result)
        
        # Log generation
        conn = get_db_connection(DB_PATH)
        conn.execute(
            """INSERT INTO quiz_generations 
               (topic, difficulty, num_questions, total_marks, timestamp, student_id) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (f"PDF: {pdf_file.filename}", difficulty, num_questions,
             validated.total_marks, datetime.now().isoformat(), "default")
        )
        conn.execute(
            """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp) 
               VALUES (?, ?, ?, ?, ?)""",
            ("quiz_generation_from_pdf", pdf_file.filename,
             f"Generated {len(validated.questions)} questions from PDF with completeness: {validated.completeness_score}",
             validated.confidence_score, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        return validated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/message")
def chat(request: ChatRequest):
    """Chat with agent (uses memory)"""
    try:
        result = agent.chat(request.message, request.user_id or "default")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory")
def get_memory(user_id: str = "default", limit: int = 50):
    """Get conversation memory"""
    try:
        return agent.get_memory(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
def query_data(request: QueryRequest):
    """Query data (search, filter, categorize) - Uses dataset"""
    try:
        # For filter type, parse query as JSON or use as category
        filters = None
        if request.query_type == "filter":
            try:
                import json
                filters = json.loads(request.query)
            except:
                filters = {"category": request.query} if request.query else {}
        
        return agent.query(request.query_type, request.query, request.limit or 20, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dataset/stats")
def get_dataset_stats():
    """Get dataset statistics"""
    try:
        data_service = agent.data_service
        all_data = data_service.get_all()
        source_info = data_service.get_source_info()
        
        stats = {
            "data_source": source_info,
            "total_items": len(all_data),
            "categories": {},
            "difficulties": {}
        }
        
        for item in all_data:
            cat = item.get("category", "uncategorized")
            diff = item.get("difficulty", "unknown")
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
            stats["difficulties"][diff] = stats["difficulties"].get(diff, 0) + 1
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data-sources")
def get_data_sources():
    """Get information about available data sources"""
    try:
        data_service = agent.data_service
        source_info = data_service.get_source_info()
        
        return {
            "available_sources": [
                {
                    "type": "JSON Dataset",
                    "file": "data/topics_dataset.json",
                    "description": "Custom-made educational topics dataset in JSON format",
                    "query_types": ["search", "filter", "categorize"],
                    "active": source_info["source_type"] == "json"
                },
                {
                    "type": "CSV Dataset",
                    "file": "data/topics_dataset.csv",
                    "description": "Custom-made educational topics dataset in CSV format",
                    "query_types": ["search", "filter", "categorize"],
                    "active": source_info["source_type"] == "csv"
                },
                {
                    "type": "SQLite Database",
                    "file": "database/ai_teacher.db",
                    "description": "Database storing logs, queries, decisions, and memory",
                    "query_types": ["database_search"],
                    "active": True
                }
            ],
            "current_source": source_info,
            "supported_formats": ["JSON", "CSV", "Database"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/quiz/evaluate", response_model=QuizEvaluationResponse)
def evaluate_quiz(request: QuizEvaluationRequest):
    """Evaluate quiz answers with validation - gives 0 marks for wrong/unanswered"""
    try:
        # Debug: Log received time
        print(f"[DEBUG] Backend received time_taken_seconds: {request.time_taken_seconds}")
        
        # Convert string keys to integers for answers (JavaScript sends string keys)
        answers_dict = {}
        if isinstance(request.answers, dict):
            for key, value in request.answers.items():
                try:
                    # Convert string key to int
                    int_key = int(key) if isinstance(key, str) else key
                    answers_dict[int_key] = value
                except (ValueError, TypeError):
                    # If conversion fails, keep original key
                    answers_dict[key] = value
        else:
            answers_dict = request.answers
        
        time_seconds = request.time_taken_seconds if request.time_taken_seconds is not None else 0
        print(f"[DEBUG] Backend passing time_taken_seconds to agent: {time_seconds}")
        
        result = agent.evaluate_quiz(
            quiz_id=request.quiz_id,
            answers=answers_dict,
            questions=request.questions,
            topic=request.topic,
            difficulty=request.difficulty,
            marks_per_question=request.marks_per_question or 10,
            user_id=request.user_id or "default",
            time_taken_seconds=time_seconds
        )
        
        # Validate with Pydantic
        validated = QuizEvaluationResponse(**result)
        
        return validated
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error in evaluate_quiz: {error_detail}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/reasoning/summarize", response_model=SummaryResponse)
def summarize(request: dict):
    """Summarize content with validation"""
    try:
        content = request.get("content", "")
        if not content:
            raise HTTPException(status_code=400, detail="Content required")
        
        result = agent.summarize(content)
        
        # Validate with Pydantic
        validated = SummaryResponse(**result)
        
        return validated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reasoning/classify", response_model=ClassificationResponse)
def classify(request: dict):
    """Classify content with validation"""
    try:
        content = request.get("content", "")
        categories = request.get("categories", ["academic", "technical", "general"])
        if not content:
            raise HTTPException(status_code=400, detail="Content required")
        
        result = agent.classify(content, categories)
        
        # Validate with Pydantic
        validated = ClassificationResponse(**result)
        
        return validated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Authentication API Endpoints
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == password_hash
    except:
        return False

def generate_token() -> str:
    """Generate a simple session token"""
    return secrets.token_urlsafe(32)

@app.post("/api/auth/signup", response_model=AuthResponse)
def sign_up(request: SignUpRequest):
    """Sign up a new user and create student profile"""
    try:
        conn = get_db_connection(DB_PATH)
        
        # Check if email already exists
        cursor = conn.execute("SELECT id FROM users WHERE email = ?", (request.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user account
        password_hash = hash_password(request.password)
        user_id = f"user_{secrets.token_urlsafe(16)}"
        now = datetime.now().isoformat()
        
        conn.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
            (request.name, request.email, password_hash, now)
        )
        
        # Generate token
        token = generate_token()
        
        # Create student profile in student database
        if STUDENT_DB_PATH:
            try:
                from src.database.student_db import create_or_update_student
                create_or_update_student(STUDENT_DB_PATH, user_id, request.name, request.email)
                print(f"Student profile created for: {user_id}")
            except Exception as e:
                print(f"Warning: Could not create student profile: {e}")
        
        conn.commit()
        conn.close()
        
        return AuthResponse(
            success=True,
            message="Account created successfully",
            user_id=user_id,
            name=request.name,
            email=request.email,
            token=token
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating account: {str(e)}")

@app.post("/api/auth/signin", response_model=AuthResponse)
def sign_in(request: SignInRequest):
    """Sign in an existing user"""
    try:
        conn = get_db_connection(DB_PATH)
        
        # Find user by email
        cursor = conn.execute("SELECT id, name, email, password FROM users WHERE email = ?", (request.email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_dict = dict(user)
        
        # Verify password
        if not verify_password(request.password, user_dict['password']):
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Generate token
        token = generate_token()
        
        # Use user ID from database (convert to string)
        user_id = f"user_{user_dict['id']}"
        
        # Update last active in student database
        if STUDENT_DB_PATH:
            try:
                from src.database.student_db import create_or_update_student
                create_or_update_student(STUDENT_DB_PATH, user_id, user_dict['name'], user_dict['email'])
            except Exception as e:
                print(f"Warning: Could not update student profile: {e}")
        
        conn.close()
        
        return AuthResponse(
            success=True,
            message="Signed in successfully",
            user_id=user_id,
            name=user_dict['name'],
            email=user_dict['email'],
            token=token
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error signing in: {str(e)}")

@app.get("/api/auth/me")
def get_current_user(token: str = None):
    """Get current user information (for frontend to check auth status)"""
    # For now, return a simple check
    # In production, you'd verify the token
    return {"authenticated": False, "message": "Token verification not implemented"}

# Student Database API Endpoints
@app.get("/api/students")
def get_all_students():
    """Get list of all students"""
    if not STUDENT_DB_PATH:
        raise HTTPException(status_code=503, detail="Student database not configured")
    try:
        from src.database.student_db import get_all_students
        students = get_all_students(STUDENT_DB_PATH)
        return {"students": students, "count": len(students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students/{student_id}/stats")
def get_student_stats(student_id: str):
    """Get comprehensive statistics for a student"""
    if not STUDENT_DB_PATH:
        raise HTTPException(status_code=503, detail="Student database not configured")
    try:
        from src.database.student_db import get_student_stats
        stats = get_student_stats(STUDENT_DB_PATH, student_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Student not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/students")
def create_student(name: str, student_id: str, email: str = None):
    """Create or update a student"""
    if not STUDENT_DB_PATH:
        raise HTTPException(status_code=503, detail="Student database not configured")
    try:
        from src.database.student_db import create_or_update_student
        create_or_update_student(STUDENT_DB_PATH, student_id, name, email)
        return {"message": "Student created/updated successfully", "student_id": student_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# YouTube RAG API Endpoints
@app.get("/api/youtube/test")
def test_youtube_endpoint():
    """Test endpoint to verify YouTube RAG feature is available"""
    try:
        from src.services.youtube_rag import get_youtube_rag_service
        return {
            "status": "available",
            "message": "YouTube RAG feature is available",
            "endpoints": [
                "POST /api/youtube/process",
                "POST /api/youtube/ask"
            ]
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": f"YouTube RAG feature not available: {str(e)}",
            "error": str(e)
        }

@app.post("/api/youtube/process", response_model=YouTubeProcessResponse)
def process_youtube_video(request: YouTubeProcessRequest):
    """Process a YouTube video: fetch transcript and create RAG chain"""
    try:
        print(f"\n[API] Received YouTube video processing request: {request.video_url}")
        from src.services.youtube_rag import get_youtube_rag_service, extract_video_id
        
        # Extract video ID from URL
        video_id = extract_video_id(request.video_url)
        if not video_id:
            error_msg = "Invalid YouTube URL. Please provide a valid YouTube video URL or video ID."
            print(f"[API] Error: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        print(f"[API] Extracted video ID: {video_id}")
        
        # Get YouTube RAG service
        rag_service = get_youtube_rag_service()
        
        # Process video
        print(f"[API] Processing video...")
        result = rag_service.process_video(video_id, request.video_url)
        
        if not result["success"]:
            error_msg = result.get("error", "Failed to process video")
            print(f"[API] Processing failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        print(f"[API] Video processed successfully: {video_id}")
        
        # Log to database
        try:
            conn = get_db_connection(DB_PATH)
            conn.execute(
                """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp) 
                   VALUES (?, ?, ?, ?, ?)""",
                ("youtube_video_processing", request.video_url,
                 f"Processed video {video_id} with {result.get('chunks_count', 0)} chunks",
                 0.9, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not log to database: {e}")
        
        return YouTubeProcessResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[API] Unexpected error processing video: {str(e)}")
        print(f"[API] Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/youtube/ask", response_model=YouTubeQuestionResponse)
def ask_youtube_question(request: YouTubeQuestionRequest):
    """Ask a question about a processed YouTube video"""
    try:
        from src.services.youtube_rag import get_youtube_rag_service
        
        # Get YouTube RAG service
        rag_service = get_youtube_rag_service()
        
        # Ask question
        result = rag_service.ask_question(request.video_id, request.question)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to answer question"))
        
        # Log to database
        try:
            conn = get_db_connection(DB_PATH)
            conn.execute(
                """INSERT INTO agent_decisions (decision_type, context, decision, confidence, timestamp) 
                   VALUES (?, ?, ?, ?, ?)""",
                ("youtube_question", f"Video: {request.video_id}, Question: {request.question[:100]}",
                 f"Answered question about video {request.video_id}",
                 0.85, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not log to database: {e}")
        
        return YouTubeQuestionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Test if YouTube endpoints can be imported
    print("\n=== Checking YouTube RAG Feature ===")
    try:
        from src.services.youtube_rag import get_youtube_rag_service, extract_video_id
        print("✓ YouTube RAG service imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import YouTube RAG service: {e}")
        print("  This may prevent YouTube endpoints from working.")
    except Exception as e:
        print(f"✗ Error importing YouTube RAG service: {e}")
    
    # Print available routes for debugging
    print("\n=== Available YouTube API Endpoints ===")
    youtube_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'youtube' in route.path.lower():
            methods = list(route.methods) if hasattr(route, 'methods') else ['GET']
            youtube_routes.append((methods[0], route.path))
    
    if youtube_routes:
        for method, path in youtube_routes:
            print(f"  {method} {path}")
    else:
        print("  WARNING: No YouTube endpoints found!")
        print("  This usually means:")
        print("    1. The server was started before endpoints were added")
        print("    2. There's an import error preventing registration")
        print("    3. Check the error messages above")
    print("========================================\n")
    
    # Print available auth routes for debugging
    print("\n=== Available Authentication API Endpoints ===")
    auth_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'auth' in route.path.lower():
            methods = list(route.methods) if hasattr(route, 'methods') else ['GET']
            auth_routes.append((methods[0], route.path))
    
    if auth_routes:
        for method, path in auth_routes:
            print(f"  {method} {path}")
    else:
        print("  WARNING: No authentication endpoints found!")
        print("  This usually means:")
        print("    1. The server was started before endpoints were added")
        print("    2. There's an import error preventing registration")
        print("    3. Check the error messages above")
    print("========================================\n")
    
    print("Starting AI Teacher Agent on http://localhost:5000")
    print("Visit http://localhost:5000/docs to see all available endpoints\n")
    
    uvicorn.run(app, host="0.0.0.0", port=5000)
