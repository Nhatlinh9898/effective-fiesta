"""
Library Manager Agent - Manages code libraries and reusable components
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from pathlib import Path
from core.base_agent import BaseAgent


class LibraryManagerAgent(BaseAgent):
    """
    Responsible for:
    - Storing reusable code components
    - Cataloging code libraries
    - Searching and retrieving code
    - Managing versions
    - Suggesting relevant components
    """
    
    def __init__(self, library_path: str = "./code_library", ai_provider=None):
        super().__init__(
            name="Library Manager Agent",
            description="Expert in managing, cataloging, and reusing code components",
            ai_provider=ai_provider
        )
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        self.catalog_file = self.library_path / "catalog.json"
        self.catalog = self._load_catalog()
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process library management task
        
        Args:
            task: Contains action (store/search/retrieve/list)
            
        Returns:
            Result of library operation
        """
        action = task.get("action", "list")
        
        if action == "store":
            return await self._store_component(task)
        elif action == "search":
            return await self._search_components(task)
        elif action == "retrieve":
            return await self._retrieve_component(task)
        elif action == "list":
            return self._list_components(task)
        elif action == "suggest":
            return await self._suggest_components(task)
        elif action == "update":
            return await self._update_component(task)
        elif action == "delete":
            return self._delete_component(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }
    
    async def _store_component(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Store a reusable component in library"""
        component_name = task.get("name")
        code = task.get("code")
        language = task.get("language", "python")
        description = task.get("description", "")
        tags = task.get("tags", [])
        category = task.get("category", "general")
        
        if not component_name or not code:
            return {
                "status": "error",
                "message": "Component name and code are required"
            }
        
        # Generate metadata using AI if description is missing
        if not description:
            description = await self._generate_description(code, language)
        
        # Create component entry
        component_id = f"{category}_{component_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        component_entry = {
            "id": component_id,
            "name": component_name,
            "description": description,
            "language": language,
            "category": category,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "usage_count": 0
        }
        
        # Save code to file
        component_dir = self.library_path / category
        component_dir.mkdir(parents=True, exist_ok=True)
        
        file_ext = self._get_file_extension(language)
        code_file = component_dir / f"{component_name}{file_ext}"
        code_file.write_text(code)
        
        component_entry["file_path"] = str(code_file.relative_to(self.library_path))
        
        # Add to catalog
        self.catalog[component_id] = component_entry
        self._save_catalog()
        
        result = {
            "status": "stored",
            "component_id": component_id,
            "component": component_entry,
            "agent": self.name
        }
        
        self.add_to_memory({
            "type": "store_component",
            "result": result
        })
        
        return result
    
    async def _search_components(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Search for components in library"""
        query = task.get("query", "")
        language = task.get("language")
        category = task.get("category")
        tags = task.get("tags", [])
        
        # Filter components
        results = []
        
        for comp_id, comp in self.catalog.items():
            # Apply filters
            if language and comp.get("language") != language:
                continue
            if category and comp.get("category") != category:
                continue
            if tags and not any(tag in comp.get("tags", []) for tag in tags):
                continue
            
            # Text search
            if query:
                search_text = f"{comp.get('name')} {comp.get('description')} {' '.join(comp.get('tags', []))}"
                if query.lower() not in search_text.lower():
                    continue
            
            results.append(comp)
        
        # Sort by relevance (usage count)
        results.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results),
            "agent": self.name
        }
    
    async def _retrieve_component(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a specific component"""
        component_id = task.get("component_id")
        
        if component_id not in self.catalog:
            return {
                "status": "not_found",
                "message": f"Component '{component_id}' not found"
            }
        
        component = self.catalog[component_id]
        
        # Load code from file
        code_file = self.library_path / component["file_path"]
        if code_file.exists():
            code = code_file.read_text()
        else:
            return {
                "status": "error",
                "message": f"Component file not found: {code_file}"
            }
        
        # Increment usage count
        self.catalog[component_id]["usage_count"] += 1
        self._save_catalog()
        
        return {
            "status": "retrieved",
            "component_id": component_id,
            "metadata": component,
            "code": code,
            "agent": self.name
        }
    
    def _list_components(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """List all components with optional filtering"""
        category = task.get("category")
        language = task.get("language")
        
        components = list(self.catalog.values())
        
        if category:
            components = [c for c in components if c.get("category") == category]
        if language:
            components = [c for c in components if c.get("language") == language]
        
        # Group by category
        by_category = {}
        for comp in components:
            cat = comp.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(comp)
        
        return {
            "status": "success",
            "total_components": len(components),
            "by_category": by_category,
            "categories": list(by_category.keys()),
            "agent": self.name
        }
    
    async def _suggest_components(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest relevant components based on requirements"""
        requirements = task.get("requirements", "")
        language = task.get("language")
        
        # Get all components
        all_components = list(self.catalog.values())
        
        if language:
            all_components = [c for c in all_components if c.get("language") == language]
        
        if not all_components:
            return {
                "status": "no_suggestions",
                "message": "No components found in library"
            }
        
        # Use AI to match requirements with components
        components_desc = "\n".join([
            f"- {c['name']}: {c['description']} (tags: {', '.join(c.get('tags', []))})"
            for c in all_components[:50]  # Limit to top 50 for AI processing
        ])
        
        prompt = f"""Match these requirements with available components:

REQUIREMENTS:
{requirements}

AVAILABLE COMPONENTS:
{components_desc}

Suggest the 5 most relevant components and explain why they match.
Respond in JSON:
{{
    "suggestions": [
        {{
            "component_name": "name",
            "relevance_score": 0.95,
            "reason": "why it's relevant"
        }}
    ]
}}"""
        
        suggestions = await self.call_ai(prompt)
        
        return {
            "status": "suggestions_generated",
            "requirements": requirements,
            "suggestions": suggestions,
            "agent": self.name
        }
    
    async def _update_component(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing component"""
        component_id = task.get("component_id")
        updates = task.get("updates", {})
        
        if component_id not in self.catalog:
            return {
                "status": "not_found",
                "message": f"Component '{component_id}' not found"
            }
        
        # Update metadata
        component = self.catalog[component_id]
        component.update(updates)
        component["updated_at"] = datetime.now().isoformat()
        
        # Update code if provided
        if "code" in updates:
            code_file = self.library_path / component["file_path"]
            code_file.write_text(updates["code"])
        
        self._save_catalog()
        
        return {
            "status": "updated",
            "component_id": component_id,
            "component": component,
            "agent": self.name
        }
    
    def _delete_component(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a component from library"""
        component_id = task.get("component_id")
        
        if component_id not in self.catalog:
            return {
                "status": "not_found",
                "message": f"Component '{component_id}' not found"
            }
        
        component = self.catalog[component_id]
        
        # Delete file
        code_file = self.library_path / component["file_path"]
        if code_file.exists():
            code_file.unlink()
        
        # Remove from catalog
        del self.catalog[component_id]
        self._save_catalog()
        
        return {
            "status": "deleted",
            "component_id": component_id,
            "agent": self.name
        }
    
    async def _generate_description(self, code: str, language: str) -> str:
        """Generate description for code using AI"""
        prompt = f"""Analyze this {language} code and provide a concise description:

```{language}
{code[:1000]}  # First 1000 chars
```

Provide a 1-2 sentence description of what this code does."""
        
        description = await self.call_ai(prompt)
        return description.strip()
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "go": ".go",
            "rust": ".rs",
            "java": ".java"
        }
        return extensions.get(language.lower(), ".txt")
    
    def _load_catalog(self) -> Dict[str, Any]:
        """Load catalog from file"""
        if self.catalog_file.exists():
            try:
                return json.loads(self.catalog_file.read_text())
            except:
                return {}
        return {}
    
    def _save_catalog(self):
        """Save catalog to file"""
        self.catalog_file.write_text(json.dumps(self.catalog, indent=2))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        total = len(self.catalog)
        by_language = {}
        by_category = {}
        
        for comp in self.catalog.values():
            lang = comp.get("language", "unknown")
            cat = comp.get("category", "general")
            
            by_language[lang] = by_language.get(lang, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_components": total,
            "by_language": by_language,
            "by_category": by_category,
            "library_path": str(self.library_path)
        }
