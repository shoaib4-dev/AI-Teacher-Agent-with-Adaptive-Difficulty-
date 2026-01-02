"""
Quick script to check if YouTube endpoints are registered in the FastAPI app
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.app import app
    
    print("=== Checking YouTube Endpoints ===\n")
    
    # Get all routes
    all_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = list(route.methods)
            for method in methods:
                all_routes.append((method, route.path))
    
    # Filter YouTube routes
    youtube_routes = [(m, p) for m, p in all_routes if 'youtube' in p.lower()]
    
    if youtube_routes:
        print("✓ YouTube endpoints found:")
        for method, path in youtube_routes:
            print(f"  {method:6} {path}")
        print(f"\nTotal: {len(youtube_routes)} endpoint(s)")
    else:
        print("✗ No YouTube endpoints found!")
        print("\nPossible reasons:")
        print("  1. Server needs to be restarted")
        print("  2. Import error in youtube_rag.py")
        print("  3. Endpoints not properly registered")
        
        # Check if the file exists
        youtube_rag_file = project_root / "src" / "services" / "youtube_rag.py"
        if youtube_rag_file.exists():
            print(f"\n✓ youtube_rag.py exists at: {youtube_rag_file}")
        else:
            print(f"\n✗ youtube_rag.py NOT found at: {youtube_rag_file}")
        
        # Try to import
        try:
            from src.services.youtube_rag import get_youtube_rag_service
            print("✓ YouTube RAG service can be imported")
        except ImportError as e:
            print(f"✗ Cannot import YouTube RAG service: {e}")
        except Exception as e:
            print(f"✗ Error importing YouTube RAG service: {e}")
    
    print("\n=== All API Endpoints ===")
    print(f"Total endpoints: {len(all_routes)}")
    print("\nFirst 10 endpoints:")
    for method, path in all_routes[:10]:
        print(f"  {method:6} {path}")
    if len(all_routes) > 10:
        print(f"  ... and {len(all_routes) - 10} more")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

