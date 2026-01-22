"""
Utility functions for the Multi-Agent AI Code Generator
"""
import json
from typing import Dict, Any, List


def format_code(code: str, language: str) -> str:
    """Format code for display"""
    return f"```{language}\n{code}\n```"


def parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from AI response
    Handles markdown code blocks and plain JSON
    """
    try:
        # Try direct JSON parse
        return json.loads(response)
    except:
        pass
    
    # Try extracting from markdown code block
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        json_str = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        json_str = response[start:end].strip()
    else:
        json_str = response
    
    try:
        return json.loads(json_str)
    except:
        return {"raw_response": response, "parse_error": "Could not parse JSON"}


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_language(language: str) -> bool:
    """Validate if language is supported"""
    supported = ["python", "javascript", "typescript", "go", "rust", "java"]
    return language.lower() in supported


def create_file_tree(structure: Dict[str, List[str]]) -> str:
    """
    Create visual file tree from structure
    
    Args:
        structure: Dict with directories as keys and subdirectories as values
        
    Returns:
        String representation of file tree
    """
    tree_lines = []
    for directory, subdirs in structure.items():
        tree_lines.append(f"📁 {directory}")
        for subdir in subdirs:
            tree_lines.append(f"  └── 📁 {subdir}")
    return "\n".join(tree_lines)
