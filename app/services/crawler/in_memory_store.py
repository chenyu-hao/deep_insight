"""
In-Memory Store for MediaCrawler
Collects crawled data in memory instead of writing to files/database
"""
from typing import Dict, List, Any
from MediaCrawler.base.base_crawler import AbstractStore
import asyncio


class InMemoryStore(AbstractStore):
    """Memory-based store that collects data without persisting"""
    
    def __init__(self):
        self.contents: List[Dict[str, Any]] = []
        self.comments: List[Dict[str, Any]] = []
        self.creators: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in memory"""
        async with self._lock:
            # Avoid duplicates based on platform-specific ID
            content_id = self._get_content_id(content_item)
            if not any(item.get("_id") == content_id for item in self.contents):
                content_item["_id"] = content_id
                self.contents.append(content_item)
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in memory"""
        async with self._lock:
            comment_id = self._get_comment_id(comment_item)
            if not any(item.get("_id") == comment_id for item in self.comments):
                comment_item["_id"] = comment_id
                self.comments.append(comment_item)
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator item in memory"""
        async with self._lock:
            creator_id = self._get_creator_id(creator)
            if not any(item.get("_id") == creator_id for item in self.creators):
                creator["_id"] = creator_id
                self.creators.append(creator)
    
    def _get_content_id(self, item: Dict[str, Any]) -> str:
        """Extract content ID based on platform"""
        # Try different platform-specific ID fields
        return (
            item.get("note_id") or 
            item.get("aweme_id") or 
            item.get("video_id") or 
            item.get("bvid") or 
            item.get("id") or 
            str(hash(str(item)))
        )
    
    def _get_comment_id(self, item: Dict[str, Any]) -> str:
        """Extract comment ID based on platform"""
        return (
            item.get("comment_id") or 
            item.get("id") or 
            str(hash(str(item)))
        )
    
    def _get_creator_id(self, item: Dict[str, Any]) -> str:
        """Extract creator ID based on platform"""
        return (
            item.get("user_id") or 
            item.get("uid") or 
            item.get("id") or 
            str(hash(str(item)))
        )
    
    def get_all_contents(self) -> List[Dict[str, Any]]:
        """Get all stored content items"""
        return self.contents.copy()
    
    def get_all_comments(self) -> List[Dict[str, Any]]:
        """Get all stored comment items"""
        return self.comments.copy()
    
    def get_all_creators(self) -> List[Dict[str, Any]]:
        """Get all stored creator items"""
        return self.creators.copy()
    
    def clear(self):
        """Clear all stored data"""
        self.contents.clear()
        self.comments.clear()
        self.creators.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored data"""
        return {
            "contents": len(self.contents),
            "comments": len(self.comments),
            "creators": len(self.creators)
        }
