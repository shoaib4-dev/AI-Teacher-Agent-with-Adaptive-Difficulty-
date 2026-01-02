"""
YouTube Video RAG Service
Handles YouTube transcript fetching, embedding, and RAG-based Q&A
"""

import re
import os
from typing import Dict, Optional, List
from pathlib import Path
import sys

# HuggingFace API Token (hardcoded) - SET BEFORE ANY IMPORTS
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
# Set in environment BEFORE importing HuggingFace libraries
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACE_API_TOKEN
os.environ["HF_TOKEN"] = HUGGINGFACE_API_TOKEN  # Some libraries check this too

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    print("Warning: youtube-transcript-api not installed")

try:
    # Try to login to HuggingFace first using huggingface_hub
    try:
        from huggingface_hub import login
        login(token=HUGGINGFACE_API_TOKEN, add_to_git_credential=False)
        print("✓ Logged in to HuggingFace Hub")
    except ImportError:
        print("Warning: huggingface_hub not available, will use environment variable")
    except Exception as e:
        print(f"Warning: Could not login to HuggingFace Hub: {e}")
    
    from langchain_community.vectorstores import FAISS
    from langchain_core.prompts import PromptTemplate
    from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: Required LangChain packages not installed")

# Gemini API Key (hardcoded)
GEMINI_API_KEY = "AIzaSyAOxW_vwEk50WbyjIyHB6m9AJ4ovj4-www"
print(f"✓ GEMINI_API_KEY configured: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
print(f"✓ HUGGINGFACE_API_TOKEN configured: {HUGGINGFACE_API_TOKEN[:10]}...{HUGGINGFACE_API_TOKEN[-4:]}")


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume the input is already a video ID
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url
    
    return None


class YouTubeRAGService:
    """Service for YouTube video RAG (Retrieval Augmented Generation)"""
    
    def __init__(self):
        self.vector_stores = {}  # Store vector stores per video_id
        self.rag_chains = {}  # Store RAG chains per video_id
        self.embeddings = None
        self.llm = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embeddings and LLM"""
        # Initialize embeddings - try local first (more reliable)
        # Ensure token is set in environment (should already be set at module level, but double-check)
        if "HUGGINGFACEHUB_API_TOKEN" not in os.environ or os.environ.get("HUGGINGFACEHUB_API_TOKEN") != HUGGINGFACE_API_TOKEN:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACE_API_TOKEN
            os.environ["HF_TOKEN"] = HUGGINGFACE_API_TOKEN
        
        try:
            # Try local embeddings first (token should be in environment)
            print("Initializing local HuggingFace embeddings...")
            print(f"Using HuggingFace token from env: {os.environ.get('HUGGINGFACEHUB_API_TOKEN', 'NOT SET')[:10]}...")
            # Use environment variable (already set at module level)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✓ Local embeddings initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize local HuggingFaceEmbeddings: {e}")
            import traceback
            print(f"Full error traceback:\n{traceback.format_exc()}")
            try:
                # Fallback to endpoint embeddings
                print("Trying HuggingFace endpoint embeddings...")
                self.embeddings = HuggingFaceEndpointEmbeddings(
                    repo_id="sentence-transformers/all-MiniLM-L6-v2",
                    task="feature-extraction"
                )
                print("✓ Endpoint embeddings initialized successfully")
            except Exception as e2:
                print(f"Warning: Could not initialize HuggingFaceEndpointEmbeddings: {e2}")
                import traceback
                print(f"Full error traceback:\n{traceback.format_exc()}")
                self.embeddings = None
                print("✗ Embeddings initialization failed. Please install: pip install sentence-transformers")
        
        # Initialize LLM
        api_key = GEMINI_API_KEY
        
        # Debug: Check if API key is found
        if api_key:
            # Mask the key for security (show first 10 and last 4 chars)
            masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
            print(f"✓ Found GEMINI_API_KEY: {masked_key} (length: {len(api_key)})")
        else:
            print("✗ GEMINI_API_KEY not configured")
        
        if api_key and LANGCHAIN_AVAILABLE:
            try:
                print("Initializing Gemini LLM...")
                # Try different model names for compatibility
                model_names = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-pro"]
                self.llm = None
                for model_name in model_names:
                    try:
                        self.llm = ChatGoogleGenerativeAI(
                            model=model_name,
                            temperature=0.2,
                            google_api_key=api_key
                        )
                        print(f"✓ Gemini LLM initialized with model: {model_name}")
                        break
                    except Exception as model_error:
                        print(f"  Failed to initialize {model_name}: {model_error}")
                        continue
                
                if not self.llm:
                    print("✗ Could not initialize any Gemini model")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini LLM: {e}")
                self.llm = None
        else:
            if not api_key:
                print("✗ GEMINI_API_KEY not configured")
            if not LANGCHAIN_AVAILABLE:
                print("✗ LangChain packages not available")
            self.llm = None
    
    def fetch_transcript(self, video_id: str) -> Dict:
        """Fetch YouTube transcript for a video"""
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            raise Exception("youtube-transcript-api package not installed")
        
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id=video_id, languages=["en"])
            
            # Convert list of objects → single long string
            transcript_text = " ".join(chunk.text for chunk in transcript_list)
            
            return {
                "success": True,
                "transcript": transcript_text,
                "length": len(transcript_text),
                "chunks_count": len(transcript_list)
            }
        except TranscriptsDisabled:
            return {
                "success": False,
                "error": "No captions available for this video"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_video(self, video_id: str, video_url: str = None) -> Dict:
        """Process a YouTube video: fetch transcript, create embeddings, build RAG chain"""
        print(f"\n=== Processing YouTube Video: {video_id} ===")
        
        # Check if already processed
        if video_id in self.vector_stores:
            print("Video already processed, returning cached result")
            return {
                "success": True,
                "message": "Video already processed",
                "video_id": video_id
            }
        
        # Re-check and reinitialize LLM if needed
        if not self.llm:
            print("LLM not initialized, attempting to initialize now...")
            # Use hardcoded API key
            api_key = GEMINI_API_KEY
            if api_key and LANGCHAIN_AVAILABLE:
                try:
                    print("Attempting to initialize Gemini LLM...")
                    model_names = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-pro"]
                    for model_name in model_names:
                        try:
                            self.llm = ChatGoogleGenerativeAI(
                                model=model_name,
                                temperature=0.2,
                                google_api_key=api_key
                            )
                            print(f"✓ Gemini LLM initialized with model: {model_name}")
                            break
                        except Exception as model_error:
                            print(f"  Failed to initialize {model_name}: {model_error}")
                            continue
                except Exception as e:
                    print(f"Error initializing LLM: {e}")
        
        # Check if embeddings and LLM are available BEFORE fetching transcript
        if not self.embeddings:
            error_msg = (
                "Embeddings model not available. "
                "Please install: pip install sentence-transformers"
            )
            print(f"✗ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        if not self.llm:
            # Get current API key status for better error message
            api_key = GEMINI_API_KEY
            
            if api_key:
                error_msg = (
                    f"LLM initialization failed even though API key is present. "
                    f"Please check server logs for details. "
                    f"API key length: {len(api_key)}"
                )
            else:
                error_msg = (
                    "LLM not available. GEMINI_API_KEY is not configured. "
                    "Please check the configuration in youtube_rag.py"
                )
            print(f"✗ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        # Fetch transcript
        print(f"Fetching transcript for video: {video_id}")
        transcript_result = self.fetch_transcript(video_id)
        if not transcript_result["success"]:
            error_msg = transcript_result.get("error", "Failed to fetch transcript")
            print(f"✗ Transcript fetch failed: {error_msg}")
            return transcript_result
        
        transcript = transcript_result["transcript"]
        print(f"✓ Transcript fetched: {len(transcript)} characters, {transcript_result.get('chunks_count', 0)} chunks")
        
        try:
            # Step 1: Split transcript into chunks
            print("Splitting transcript into chunks...")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = splitter.create_documents([transcript])
            print(f"✓ Created {len(chunks)} chunks")
            
            # Step 2: Create vector store
            print("Creating FAISS vector store...")
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            print("✓ Vector store created")
            
            # Step 3: Create retriever
            print("Creating retriever...")
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            print("✓ Retriever created")
            
            # Step 4: Create prompt template
            print("Setting up RAG chain...")
            prompt = PromptTemplate(
                template="""
You are a helpful assistant answering questions about a YouTube video.
Answer ONLY using the provided transcript context.
If the context is insufficient, say "I don't have enough information from the video transcript to answer this question."

Context:
{context}

Question: {question}

Answer:""",
                input_variables=["context", "question"],
            )
            
            # Step 5: Format documents function
            def format_docs(docs):
                """Convert list of LangChain Documents → clean text block."""
                return "\n\n".join(doc.page_content for doc in docs)
            
            # Step 6: Build RAG chain
            parallel_chain = RunnableParallel(
                {
                    "context": retriever | RunnableLambda(format_docs),
                    "question": RunnablePassthrough(),
                }
            )
            
            parser = StrOutputParser()
            rag_chain = parallel_chain | prompt | self.llm | parser
            
            # Store for later use
            self.vector_stores[video_id] = vector_store
            self.rag_chains[video_id] = rag_chain
            
            print(f"✓ Video {video_id} processed successfully!")
            print("=" * 50)
            
            return {
                "success": True,
                "message": "Video processed successfully",
                "video_id": video_id,
                "transcript_length": len(transcript),
                "chunks_count": len(chunks)
            }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"✗ Error processing video: {str(e)}")
            print(f"Traceback:\n{error_trace}")
            return {
                "success": False,
                "error": f"Error processing video: {str(e)}. Check server logs for details."
            }
    
    def ask_question(self, video_id: str, question: str) -> Dict:
        """Ask a question about a processed video"""
        if video_id not in self.rag_chains:
            return {
                "success": False,
                "error": "Video not processed yet. Please process the video first."
            }
        
        try:
            rag_chain = self.rag_chains[video_id]
            response = rag_chain.invoke(question)
            
            return {
                "success": True,
                "answer": response,
                "question": question,
                "video_id": video_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error answering question: {str(e)}"
            }
    
    def is_video_processed(self, video_id: str) -> bool:
        """Check if a video has been processed"""
        return video_id in self.rag_chains


# Global instance
_youtube_rag_service = None

def get_youtube_rag_service() -> YouTubeRAGService:
    """Get or create YouTube RAG service instance"""
    global _youtube_rag_service
    if _youtube_rag_service is None:
        _youtube_rag_service = YouTubeRAGService()
    return _youtube_rag_service

