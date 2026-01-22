"""
Code Analyzer Agent - Analyzes code quality, patterns, and issues
"""
from typing import Dict, Any, List
import re
from core.base_agent import BaseAgent


class CodeAnalyzerAgent(BaseAgent):
    """
    Responsible for:
    - Analyzing code quality
    - Detecting bugs and vulnerabilities
    - Identifying performance issues
    - Checking code style and standards
    - Suggesting improvements
    - Handling billions of lines (chunked analysis)
    """
    
    ANALYSIS_TYPES = {
        "quality": "Code quality, maintainability, readability",
        "security": "Security vulnerabilities, injection risks",
        "performance": "Performance bottlenecks, optimization opportunities",
        "style": "Code style, conventions, formatting",
        "architecture": "Architectural patterns, design principles",
        "dependencies": "Dependency analysis, version conflicts",
        "documentation": "Documentation completeness and quality"
    }
    
    def __init__(self, ai_provider=None):
        super().__init__(
            name="Code Analyzer Agent",
            description="Expert code analyzer for quality, security, and performance",
            ai_provider=ai_provider
        )
        self.chunk_size = 10000  # Lines per chunk for large codebases
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code based on task specifications
        
        Args:
            task: Contains code to analyze, analysis types, language
            
        Returns:
            Analysis results with issues and recommendations
        """
        code = task.get("code", "")
        language = task.get("language", "python")
        analysis_types = task.get("analysis_types", ["quality", "security"])
        file_path = task.get("file_path", "unknown")
        
        # Handle large code (chunked analysis)
        if len(code.split('\n')) > self.chunk_size:
            return await self._analyze_large_codebase(code, language, analysis_types)
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(code, language, analysis_types, file_path)
        
        # Get AI analysis
        analysis_result = await self.call_ai(
            prompt=prompt,
            system_prompt="""You are an expert code reviewer and security analyst.
            Provide detailed, actionable feedback on code quality, security, and performance.
            Respond with structured JSON format."""
        )
        
        # Parse analysis result
        try:
            parsed_analysis = self._parse_analysis_response(analysis_result)
        except:
            parsed_analysis = {
                "raw_response": analysis_result,
                "status": "needs_parsing"
            }
        
        result = {
            "status": "success",
            "file_path": file_path,
            "language": language,
            "analysis": parsed_analysis,
            "agent": self.name
        }
        
        self.add_to_memory({
            "type": "code_analysis",
            "task": task,
            "result": result
        })
        
        return result
    
    def _build_analysis_prompt(self, code: str, language: str,
                              analysis_types: List[str], file_path: str) -> str:
        """Build code analysis prompt"""
        types_desc = "\n".join([
            f"- {t}: {self.ANALYSIS_TYPES.get(t, 'General analysis')}"
            for t in analysis_types
        ])
        
        return f"""Analyze this {language} code thoroughly:

FILE: {file_path}

CODE:
```{language}
{code}
```

ANALYSIS FOCUS:
{types_desc}

RESPONSE FORMAT (JSON):
{{
    "overall_score": 85,
    "summary": "brief overview of code quality",
    "issues": [
        {{
            "severity": "high/medium/low",
            "type": "security/performance/style/etc",
            "line": 42,
            "message": "description of issue",
            "suggestion": "how to fix it",
            "code_example": "corrected code snippet"
        }}
    ],
    "strengths": ["what the code does well"],
    "recommendations": [
        {{
            "priority": "high/medium/low",
            "category": "category",
            "description": "what to improve",
            "impact": "expected benefit"
        }}
    ],
    "metrics": {{
        "complexity": "assessment",
        "maintainability": "score/assessment",
        "test_coverage": "estimated or noted as needed"
    }}
}}

Provide actionable, specific feedback."""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse AI analysis response"""
        try:
            # Extract JSON
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
            
            import json
            return json.loads(json_str)
        except Exception as e:
            return {
                "raw_response": response,
                "parse_error": str(e),
                "status": "manual_review_needed"
            }
    
    async def _analyze_large_codebase(self, code: str, language: str,
                                     analysis_types: List[str]) -> Dict[str, Any]:
        """
        Analyze large codebase by chunking
        Handles billions of lines efficiently
        """
        lines = code.split('\n')
        total_lines = len(lines)
        chunks = []
        
        # Split into chunks
        for i in range(0, total_lines, self.chunk_size):
            chunk = '\n'.join(lines[i:i + self.chunk_size])
            chunks.append({
                "start_line": i + 1,
                "end_line": min(i + self.chunk_size, total_lines),
                "code": chunk
            })
        
        # Analyze each chunk
        chunk_results = []
        for idx, chunk in enumerate(chunks):
            chunk_analysis = await self.process({
                "code": chunk["code"],
                "language": language,
                "analysis_types": analysis_types,
                "file_path": f"chunk_{idx + 1}_lines_{chunk['start_line']}-{chunk['end_line']}"
            })
            chunk_results.append(chunk_analysis)
        
        # Aggregate results
        aggregated = self._aggregate_chunk_results(chunk_results, total_lines)
        
        return {
            "status": "success",
            "analysis_type": "large_codebase",
            "total_lines": total_lines,
            "chunks_analyzed": len(chunks),
            "aggregated_analysis": aggregated,
            "agent": self.name
        }
    
    def _aggregate_chunk_results(self, chunk_results: List[Dict], 
                                total_lines: int) -> Dict[str, Any]:
        """Aggregate results from multiple chunks"""
        all_issues = []
        all_recommendations = []
        
        for result in chunk_results:
            analysis = result.get("analysis", {})
            if "issues" in analysis:
                all_issues.extend(analysis["issues"])
            if "recommendations" in analysis:
                all_recommendations.extend(analysis["recommendations"])
        
        # Sort by severity/priority
        severity_order = {"high": 0, "medium": 1, "low": 2}
        all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))
        
        return {
            "total_lines_analyzed": total_lines,
            "total_issues": len(all_issues),
            "critical_issues": len([i for i in all_issues if i.get("severity") == "high"]),
            "issues": all_issues[:100],  # Top 100 issues
            "recommendations": all_recommendations[:50],  # Top 50 recommendations
            "summary": f"Analyzed {total_lines:,} lines of code across {len(chunk_results)} chunks"
        }
    
    async def compare_code_versions(self, old_code: str, new_code: str,
                                   language: str) -> Dict[str, Any]:
        """Compare two versions of code"""
        prompt = f"""Compare these two versions of {language} code:

OLD VERSION:
```{language}
{old_code}
```

NEW VERSION:
```{language}
{new_code}
```

Analyze:
1. What changed and why
2. Quality improvements or regressions
3. Potential issues introduced
4. Recommendations

Provide structured JSON response."""
        
        comparison = await self.call_ai(prompt)
        
        return {
            "status": "comparison_complete",
            "comparison": comparison,
            "language": language
        }
    
    def get_analysis_types(self) -> Dict[str, str]:
        """Get available analysis types"""
        return self.ANALYSIS_TYPES.copy()
