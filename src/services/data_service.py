"""
Data Service - Handles dataset operations (search, filter, categorize)
Supports multiple data sources: JSON, CSV, Database
"""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class DataService:
    """Service for dataset operations - supports JSON, CSV, and Database"""
    
    def __init__(self, dataset_path: str = None, source_type: str = "auto"):
        """
        Initialize data service
        Args:
            dataset_path: Path to dataset file (JSON or CSV)
            source_type: "json", "csv", "database", or "auto" (auto-detect)
        """
        base_dir = Path(__file__).parent.parent.parent
        
        if dataset_path is None:
            # Try JSON first, then CSV
            json_path = base_dir / "data" / "topics_dataset.json"
            csv_path = base_dir / "data" / "topics_dataset.csv"
            
            if json_path.exists():
                dataset_path = json_path
                source_type = "json"
            elif csv_path.exists():
                dataset_path = csv_path
                source_type = "csv"
            else:
                dataset_path = json_path  # Default to JSON path
        
        self.dataset_path = Path(dataset_path)
        self.source_type = source_type if source_type != "auto" else self._detect_source_type()
        self.data = self._load_dataset()
    
    def _detect_source_type(self) -> str:
        """Auto-detect source type from file extension"""
        ext = self.dataset_path.suffix.lower()
        if ext == ".json":
            return "json"
        elif ext == ".csv":
            return "csv"
        else:
            return "json"  # Default
    
    def _load_dataset(self) -> List[Dict]:
        """Load dataset from JSON, CSV, or Database"""
        if not self.dataset_path.exists():
            print(f"Dataset file not found: {self.dataset_path}")
            return []
        
        try:
            if self.source_type == "json":
                return self._load_json()
            elif self.source_type == "csv":
                return self._load_csv()
            else:
                return []
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []
    
    def _load_json(self) -> List[Dict]:
        """Load dataset from JSON file"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_csv(self) -> List[Dict]:
        """Load dataset from CSV file"""
        data = []
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse key_concepts and tags (semicolon-separated)
                row['key_concepts'] = row.get('key_concepts', '').split(';') if row.get('key_concepts') else []
                row['tags'] = row.get('tags', '').split(';') if row.get('tags') else []
                # Convert id to int
                if 'id' in row:
                    try:
                        row['id'] = int(row['id'])
                    except:
                        pass
                data.append(row)
        return data
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search dataset by topic name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for item in self.data:
            # Search in topic name
            if query_lower in item.get("topic", "").lower():
                results.append(item)
                continue
            
            # Search in description
            if query_lower in item.get("description", "").lower():
                results.append(item)
                continue
            
            # Search in tags
            tags = item.get("tags", [])
            if any(query_lower in tag.lower() for tag in tags):
                results.append(item)
                continue
            
            # Search in key concepts
            concepts = item.get("key_concepts", [])
            if any(query_lower in concept.lower() for concept in concepts):
                results.append(item)
        
        return results[:limit]
    
    def filter(self, filters: Dict[str, Any], limit: int = 20) -> List[Dict]:
        """Filter dataset by category, difficulty, or other attributes"""
        results = []
        
        for item in self.data:
            match = True
            
            # Filter by category
            if "category" in filters:
                if item.get("category", "").lower() != filters["category"].lower():
                    match = False
            
            # Filter by difficulty
            if "difficulty" in filters:
                if item.get("difficulty", "").lower() != filters["difficulty"].lower():
                    match = False
            
            # Filter by tags
            if "tags" in filters:
                item_tags = [t.lower() for t in item.get("tags", [])]
                filter_tags = [t.lower() for t in filters["tags"]]
                if not any(tag in item_tags for tag in filter_tags):
                    match = False
            
            if match:
                results.append(item)
        
        return results[:limit]
    
    def categorize(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """Categorize dataset items by category"""
        categories = {}
        
        for item in self.data:
            category = item.get("category", "uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Limit items per category
        for category in categories:
            categories[category] = categories[category][:limit]
        
        return categories
    
    def get_by_id(self, item_id: int) -> Dict:
        """Get item by ID"""
        for item in self.data:
            if item.get("id") == item_id:
                return item
        return {}
    
    def get_all(self, limit: int = None) -> List[Dict]:
        """Get all items"""
        if limit:
            return self.data[:limit]
        return self.data
    
    def get_source_info(self) -> Dict:
        """Get information about the data source"""
        return {
            "source_type": self.source_type,
            "source_path": str(self.dataset_path),
            "total_items": len(self.data),
            "supported_formats": ["JSON", "CSV", "Database"]
        }

