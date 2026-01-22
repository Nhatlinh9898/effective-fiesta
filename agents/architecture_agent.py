"""
Architecture Agent - Designs system architecture and project structure
"""
from typing import Dict, Any
import json
from core.base_agent import BaseAgent


class ArchitectureAgent(BaseAgent):
    """
    Responsible for:
    - Analyzing requirements
    - Designing system architecture
    - Creating project structure
    - Selecting appropriate technologies
    - Defining component interactions
    """
    
    def __init__(self, ai_provider=None):
        super().__init__(
            name="Architecture Agent",
            description="Expert in system design, architecture patterns, and technology selection",
            ai_provider=ai_provider
        )
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process architecture design task
        
        Args:
            task: Contains requirements, constraints, preferences
            
        Returns:
            Architecture design document
        """
        requirements = task.get("requirements", "")
        languages = task.get("languages", ["Python", "JavaScript"])
        frameworks = task.get("frameworks", [])
        scale = task.get("scale", "medium")
        
        # Build comprehensive architecture prompt
        prompt = self._build_architecture_prompt(requirements, languages, frameworks, scale)
        
        # Get AI response
        architecture_design = await self.call_ai(
            prompt=prompt,
            system_prompt="""You are an expert software architect. 
            Design scalable, maintainable, and production-ready architectures.
            Respond with a detailed JSON structure."""
        )
        
        # Parse and structure the response
        try:
            parsed_design = self._parse_architecture_response(architecture_design)
        except:
            parsed_design = {
                "raw_response": architecture_design,
                "status": "needs_parsing"
            }
        
        result = {
            "status": "success",
            "architecture": parsed_design,
            "agent": self.name
        }
        
        self.add_to_memory({
            "type": "architecture_design",
            "task": task,
            "result": result
        })
        
        return result
    
    def _build_architecture_prompt(self, requirements: str, languages: list, 
                                   frameworks: list, scale: str) -> str:
        """Build detailed architecture design prompt"""
        return f"""Design a complete software architecture based on these specifications:

REQUIREMENTS:
{requirements}

CONSTRAINTS:
- Programming Languages: {', '.join(languages)}
- Frameworks (if specified): {', '.join(frameworks) if frameworks else 'Choose best fit'}
- Scale: {scale}

DELIVERABLES (respond in JSON format):
{{
    "project_name": "suggested name",
    "architecture_type": "microservices/monolith/serverless/etc",
    "layers": [
        {{
            "name": "layer name",
            "purpose": "description",
            "technologies": ["tech1", "tech2"],
            "components": ["component1", "component2"]
        }}
    ],
    "tech_stack": {{
        "frontend": {{"framework": "", "libraries": []}},
        "backend": {{"framework": "", "libraries": [], "database": ""}},
        "infrastructure": {{"hosting": "", "ci_cd": "", "monitoring": ""}}
    }},
    "directory_structure": {{
        "frontend/": ["src/", "components/", "pages/", "utils/"],
        "backend/": ["api/", "services/", "models/", "utils/"],
        "shared/": ["types/", "constants/"]
    }},
    "data_flow": "description of how data flows through the system",
    "api_design": {{
        "style": "REST/GraphQL/gRPC",
        "endpoints": [
            {{"method": "GET", "path": "/api/resource", "purpose": "description"}}
        ]
    }},
    "security_considerations": ["item1", "item2"],
    "scalability_strategy": "description",
    "deployment_strategy": "description"
}}

Provide a complete, production-ready architecture design."""
    
    def _parse_architecture_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured architecture"""
        # Try to extract JSON from response
        try:
            # Find JSON in response (handle markdown code blocks)
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
            # Fallback: return structured dict with raw response
            return {
                "raw_response": response,
                "parse_error": str(e),
                "status": "manual_review_needed"
            }
    
    async def refine_architecture(self, current_design: Dict[str, Any], 
                                  feedback: str) -> Dict[str, Any]:
        """Refine architecture based on feedback"""
        prompt = f"""Refine this architecture design based on feedback:

CURRENT DESIGN:
{json.dumps(current_design, indent=2)}

FEEDBACK:
{feedback}

Provide an improved architecture design in the same JSON format."""
        
        refined_design = await self.call_ai(prompt)
        
        try:
            parsed = self._parse_architecture_response(refined_design)
        except:
            parsed = {"raw_response": refined_design}
        
        return {
            "status": "refined",
            "architecture": parsed,
            "original_design": current_design
        }
