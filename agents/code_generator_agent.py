"""
Code Generator Agent - Generates clean, production-ready code
"""
from typing import Dict, Any, List
import json
from core.base_agent import BaseAgent


class CodeGeneratorAgent(BaseAgent):
    """
    Responsible for:
    - Generating code based on specifications
    - Following best practices and design patterns
    - Creating modular, reusable components
    - Writing clean, documented code
    - Supporting multiple programming languages
    """
    
    SUPPORTED_LANGUAGES = {
        "python": {
            "extensions": [".py"],
            "patterns": ["OOP", "Functional", "Async"],
            "frameworks": ["Django", "Flask", "FastAPI", "Streamlit"]
        },
        "javascript": {
            "extensions": [".js", ".jsx"],
            "patterns": ["OOP", "Functional", "Reactive"],
            "frameworks": ["React", "Vue", "Express", "Next.js"]
        },
        "typescript": {
            "extensions": [".ts", ".tsx"],
            "patterns": ["OOP", "Functional", "Reactive"],
            "frameworks": ["React", "Vue", "Angular", "Next.js", "NestJS"]
        },
        "go": {
            "extensions": [".go"],
            "patterns": ["Concurrent", "Functional"],
            "frameworks": ["Gin", "Echo", "Fiber"]
        },
        "rust": {
            "extensions": [".rs"],
            "patterns": ["Functional", "Systems"],
            "frameworks": ["Actix", "Rocket", "Axum"]
        },
        "java": {
            "extensions": [".java"],
            "patterns": ["OOP", "Enterprise"],
            "frameworks": ["Spring", "Quarkus", "Micronaut"]
        }
    }
    
    def __init__(self, ai_provider=None):
        super().__init__(
            name="Code Generator Agent",
            description="Expert code generator supporting multiple languages and frameworks",
            ai_provider=ai_provider
        )
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code based on task specifications
        
        Args:
            task: Contains code specifications, language, framework, etc.
            
        Returns:
            Generated code files
        """
        component_spec = task.get("component_spec", "")
        language = task.get("language", "python").lower()
        framework = task.get("framework", "")
        architecture = task.get("architecture", {})
        
        # Validate language support
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                "status": "error",
                "message": f"Language '{language}' not supported. Supported: {list(self.SUPPORTED_LANGUAGES.keys())}"
            }
        
        # Generate code
        prompt = self._build_code_generation_prompt(
            component_spec, language, framework, architecture
        )
        
        generated_code = await self.call_ai(
            prompt=prompt,
            system_prompt=f"""You are an expert {language} developer. 
            Generate clean, production-ready, well-documented code.
            Follow best practices and modern design patterns.
            Respond with code files in a structured JSON format."""
        )
        
        # Parse generated code
        try:
            code_files = self._parse_code_response(generated_code)
        except:
            code_files = {
                "raw_response": generated_code,
                "status": "needs_parsing"
            }
        
        result = {
            "status": "success",
            "language": language,
            "framework": framework,
            "code_files": code_files,
            "agent": self.name
        }
        
        self.add_to_memory({
            "type": "code_generation",
            "task": task,
            "result": result
        })
        
        return result
    
    def _build_code_generation_prompt(self, component_spec: str, language: str,
                                     framework: str, architecture: Dict) -> str:
        """Build code generation prompt"""
        lang_info = self.SUPPORTED_LANGUAGES[language]
        
        return f"""Generate production-ready code for this component:

SPECIFICATION:
{component_spec}

LANGUAGE: {language}
FRAMEWORK: {framework if framework else 'Standard library'}
FILE EXTENSIONS: {', '.join(lang_info['extensions'])}

ARCHITECTURE CONTEXT:
{json.dumps(architecture, indent=2) if architecture else 'Not provided'}

REQUIREMENTS:
1. Clean, maintainable code
2. Proper error handling
3. Comprehensive documentation (docstrings/comments)
4. Type hints/annotations where applicable
5. Follow language-specific best practices
6. Modular and reusable design
7. Unit test structure (if applicable)

RESPONSE FORMAT (JSON):
{{
    "files": [
        {{
            "path": "relative/path/to/file.ext",
            "content": "complete file content here",
            "description": "what this file does",
            "dependencies": ["package1", "package2"]
        }}
    ],
    "setup_instructions": "how to set up and run",
    "usage_example": "code example showing how to use"
}}

Generate complete, working code."""
    
    def _parse_code_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into code files structure"""
        try:
            # Extract JSON from response
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
            
            return json.loads(json_str)
        except Exception as e:
            return {
                "raw_response": response,
                "parse_error": str(e),
                "status": "manual_review_needed"
            }
    
    async def generate_multiple_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate multiple components"""
        results = []
        
        for component in components:
            result = await self.process(component)
            results.append(result)
        
        return results
    
    async def refine_code(self, current_code: str, feedback: str, 
                         language: str) -> Dict[str, Any]:
        """Refine code based on feedback"""
        prompt = f"""Improve this {language} code based on feedback:

CURRENT CODE:
```{language}
{current_code}
```

FEEDBACK:
{feedback}

Provide the improved code with explanations."""
        
        refined_code = await self.call_ai(prompt)
        
        return {
            "status": "refined",
            "refined_code": refined_code,
            "language": language
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get information about supported languages"""
        return self.SUPPORTED_LANGUAGES
