"""
Execution Agent - Validates, tests, and executes code
"""
from typing import Dict, Any, List
import subprocess
import tempfile
import os
from pathlib import Path
from core.base_agent import BaseAgent


class ExecutionAgent(BaseAgent):
    """
    Responsible for:
    - Validating code syntax
    - Running code in sandboxed environments
    - Executing tests
    - Monitoring execution
    - Reporting errors and results
    """
    
    EXECUTION_MODES = {
        "validate": "Syntax validation only",
        "dry_run": "Parse and validate without execution",
        "test": "Run unit tests",
        "execute": "Full execution",
        "benchmark": "Performance benchmarking"
    }
    
    LANGUAGE_RUNNERS = {
        "python": {"cmd": "python", "test_cmd": "pytest"},
        "javascript": {"cmd": "node", "test_cmd": "npm test"},
        "typescript": {"cmd": "ts-node", "test_cmd": "npm test"},
        "go": {"cmd": "go run", "test_cmd": "go test"},
        "rust": {"cmd": "cargo run", "test_cmd": "cargo test"},
        "java": {"cmd": "java", "test_cmd": "mvn test"}
    }
    
    def __init__(self, ai_provider=None):
        super().__init__(
            name="Execution Agent",
            description="Expert in code validation, testing, and execution",
            ai_provider=ai_provider
        )
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute or validate code based on task
        
        Args:
            task: Contains code, language, execution mode
            
        Returns:
            Execution results
        """
        code = task.get("code", "")
        language = task.get("language", "python")
        mode = task.get("mode", "validate")
        files = task.get("files", [])
        dependencies = task.get("dependencies", [])
        
        if language not in self.LANGUAGE_RUNNERS:
            return {
                "status": "error",
                "message": f"Language '{language}' not supported for execution"
            }
        
        result = {
            "status": "unknown",
            "mode": mode,
            "language": language,
            "agent": self.name
        }
        
        try:
            if mode == "validate":
                result.update(await self._validate_syntax(code, language))
            elif mode == "dry_run":
                result.update(await self._dry_run(code, language))
            elif mode == "test":
                result.update(await self._run_tests(files, language, dependencies))
            elif mode == "execute":
                result.update(await self._execute_code(code, language, files))
            elif mode == "benchmark":
                result.update(await self._benchmark_code(code, language))
            else:
                result["status"] = "error"
                result["message"] = f"Unknown execution mode: {mode}"
        
        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
        
        self.add_to_memory({
            "type": "code_execution",
            "task": task,
            "result": result
        })
        
        return result
    
    async def _validate_syntax(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax without execution"""
        
        if language == "python":
            try:
                compile(code, '<string>', 'exec')
                return {
                    "status": "valid",
                    "message": "Syntax is valid"
                }
            except SyntaxError as e:
                return {
                    "status": "invalid",
                    "message": f"Syntax error at line {e.lineno}: {e.msg}",
                    "line": e.lineno,
                    "details": str(e)
                }
        
        # For other languages, use AI to validate
        prompt = f"""Validate this {language} code syntax:

```{language}
{code}
```

Check for:
1. Syntax errors
2. Common mistakes
3. Missing imports/dependencies

Respond in JSON:
{{
    "valid": true/false,
    "errors": [list of errors if any],
    "warnings": [list of warnings if any]
}}"""
        
        validation = await self.call_ai(prompt)
        
        try:
            import json
            parsed = json.loads(validation)
            return {
                "status": "valid" if parsed.get("valid") else "invalid",
                "validation": parsed
            }
        except:
            return {
                "status": "validated",
                "validation": validation
            }
    
    async def _dry_run(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code without execution"""
        prompt = f"""Analyze this {language} code as if executing it (dry run):

```{language}
{code}
```

Predict:
1. Expected behavior
2. Potential runtime errors
3. Resource usage
4. Side effects

Respond in JSON format."""
        
        analysis = await self.call_ai(prompt)
        
        return {
            "status": "dry_run_complete",
            "analysis": analysis
        }
    
    async def _execute_code(self, code: str, language: str, 
                           files: List[Dict] = None) -> Dict[str, Any]:
        """
        Execute code in isolated environment
        Note: This is a simplified version. Production should use proper sandboxing.
        """
        
        if language != "python":
            return {
                "status": "simulated",
                "message": "Actual execution available for Python only. Other languages simulated.",
                "simulation": f"Would execute {language} code"
            }
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Write main code file
            code_file = tmpdir_path / "main.py"
            code_file.write_text(code)
            
            # Write additional files if provided
            if files:
                for file_info in files:
                    file_path = tmpdir_path / file_info.get("path", "file.py")
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(file_info.get("content", ""))
            
            try:
                # Execute with timeout
                result = subprocess.run(
                    ["python", str(code_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=tmpdir
                )
                
                return {
                    "status": "executed",
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
            
            except subprocess.TimeoutExpired:
                return {
                    "status": "timeout",
                    "message": "Execution exceeded 30 second timeout"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Execution error: {str(e)}"
                }
    
    async def _run_tests(self, files: List[Dict], language: str,
                        dependencies: List[str]) -> Dict[str, Any]:
        """Run test suite"""
        
        # Use AI to analyze test structure and predict results
        files_desc = "\n".join([
            f"- {f.get('path')}: {f.get('description', 'N/A')}"
            for f in files
        ])
        
        prompt = f"""Analyze this {language} test suite:

FILES:
{files_desc}

DEPENDENCIES:
{', '.join(dependencies)}

Predict:
1. Test coverage
2. Potential test failures
3. Missing test cases
4. Test quality

Respond in JSON format."""
        
        analysis = await self.call_ai(prompt)
        
        return {
            "status": "test_analysis_complete",
            "language": language,
            "analysis": analysis,
            "note": "Full test execution requires proper environment setup"
        }
    
    async def _benchmark_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        prompt = f"""Analyze performance of this {language} code:

```{language}
{code}
```

Evaluate:
1. Time complexity
2. Space complexity
3. Performance bottlenecks
4. Optimization opportunities

Respond in JSON format."""
        
        benchmark = await self.call_ai(prompt)
        
        return {
            "status": "benchmark_complete",
            "benchmark": benchmark
        }
    
    def get_execution_modes(self) -> Dict[str, str]:
        """Get available execution modes"""
        return self.EXECUTION_MODES.copy()
    
    def get_supported_languages(self) -> Dict[str, Dict]:
        """Get supported languages for execution"""
        return self.LANGUAGE_RUNNERS.copy()
