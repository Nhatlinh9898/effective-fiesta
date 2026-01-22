"""
Template Manager - Manages project templates and code patterns
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path


class TemplateManager:
    """
    Manages reusable project templates
    - Full-stack application templates
    - Component templates
    - API templates
    - Database schemas
    """
    
    BUILTIN_TEMPLATES = {
        "web_app_react_python": {
            "name": "React + Python FastAPI Web App",
            "description": "Full-stack web application with React frontend and FastAPI backend",
            "stack": {
                "frontend": {"framework": "React", "language": "TypeScript"},
                "backend": {"framework": "FastAPI", "language": "Python"},
                "database": "PostgreSQL"
            },
            "structure": {
                "frontend/": ["src/", "components/", "pages/", "hooks/", "utils/", "types/"],
                "backend/": ["app/", "api/", "models/", "schemas/", "services/", "db/"],
                "shared/": ["types/"]
            }
        },
        "web_app_vue_node": {
            "name": "Vue + Node.js Express Web App",
            "description": "Full-stack web application with Vue.js frontend and Express backend",
            "stack": {
                "frontend": {"framework": "Vue", "language": "TypeScript"},
                "backend": {"framework": "Express", "language": "TypeScript"},
                "database": "MongoDB"
            },
            "structure": {
                "frontend/": ["src/", "components/", "views/", "router/", "store/", "utils/"],
                "backend/": ["src/", "routes/", "controllers/", "models/", "middleware/", "utils/"]
            }
        },
        "microservices": {
            "name": "Microservices Architecture",
            "description": "Microservices-based backend with API gateway",
            "stack": {
                "gateway": {"framework": "Kong/Nginx", "language": "Config"},
                "services": {"framework": "FastAPI/Express", "language": "Python/Node"},
                "database": "PostgreSQL/MongoDB"
            },
            "structure": {
                "gateway/": ["config/", "routes/"],
                "services/": ["auth/", "users/", "products/", "orders/"],
                "shared/": ["models/", "utils/", "types/"]
            }
        },
        "rest_api": {
            "name": "RESTful API",
            "description": "RESTful API with authentication and database",
            "stack": {
                "backend": {"framework": "FastAPI", "language": "Python"},
                "database": "PostgreSQL",
                "auth": "JWT"
            },
            "structure": {
                "app/": ["api/", "models/", "schemas/", "crud/", "auth/", "db/"]
            }
        },
        "graphql_api": {
            "name": "GraphQL API",
            "description": "GraphQL API with schema-first design",
            "stack": {
                "backend": {"framework": "Apollo Server", "language": "TypeScript"},
                "database": "PostgreSQL",
                "orm": "Prisma"
            },
            "structure": {
                "src/": ["schema/", "resolvers/", "models/", "utils/", "auth/"]
            }
        },
        "serverless": {
            "name": "Serverless Application",
            "description": "Serverless application with AWS Lambda/Cloud Functions",
            "stack": {
                "functions": {"framework": "Serverless Framework", "language": "Python/Node"},
                "database": "DynamoDB/Firestore",
                "api": "API Gateway"
            },
            "structure": {
                "functions/": ["auth/", "api/", "workers/"],
                "lib/": ["utils/", "db/"]
            }
        },
        "data_pipeline": {
            "name": "Data Pipeline",
            "description": "ETL/ELT data pipeline with scheduling",
            "stack": {
                "orchestration": {"framework": "Airflow", "language": "Python"},
                "processing": {"framework": "Pandas/Spark", "language": "Python"},
                "storage": "Data Warehouse"
            },
            "structure": {
                "dags/": ["etl/", "elt/"],
                "scripts/": ["extract/", "transform/", "load/"],
                "config/": []
            }
        },
        "machine_learning": {
            "name": "ML Model Service",
            "description": "Machine learning model training and serving",
            "stack": {
                "training": {"framework": "PyTorch/TensorFlow", "language": "Python"},
                "serving": {"framework": "FastAPI", "language": "Python"},
                "storage": "S3/GCS"
            },
            "structure": {
                "training/": ["models/", "data/", "notebooks/"],
                "serving/": ["api/", "models/", "utils/"],
                "pipelines/": []
            }
        }
    }
    
    def __init__(self, templates_dir: str = "./project_templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.custom_templates: Dict[str, Dict] = {}
        self._load_custom_templates()
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        if template_id in self.BUILTIN_TEMPLATES:
            return self.BUILTIN_TEMPLATES[template_id]
        return self.custom_templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available templates"""
        all_templates = []
        
        # Builtin templates
        for template_id, template in self.BUILTIN_TEMPLATES.items():
            all_templates.append({
                "id": template_id,
                "type": "builtin",
                **template
            })
        
        # Custom templates
        for template_id, template in self.custom_templates.items():
            all_templates.append({
                "id": template_id,
                "type": "custom",
                **template
            })
        
        return all_templates
    
    def create_custom_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom template"""
        self.custom_templates[template_id] = template_data
        self._save_custom_templates()
        
        return {
            "status": "created",
            "template_id": template_id,
            "template": template_data
        }
    
    def get_template_structure(self, template_id: str) -> Dict[str, Any]:
        """Get detailed project structure for a template"""
        template = self.get_template(template_id)
        if not template:
            return {"error": f"Template '{template_id}' not found"}
        
        return {
            "template_id": template_id,
            "name": template.get("name"),
            "structure": template.get("structure", {}),
            "stack": template.get("stack", {})
        }
    
    def generate_project_files(self, template_id: str, 
                              customization: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate project file structure based on template
        
        Args:
            template_id: ID of template to use
            customization: Custom parameters (project_name, features, etc.)
            
        Returns:
            Dictionary with file structure and contents
        """
        template = self.get_template(template_id)
        if not template:
            return {"error": f"Template '{template_id}' not found"}
        
        customization = customization or {}
        project_name = customization.get("project_name", "my_project")
        
        files = {}
        
        # Generate base structure
        structure = template.get("structure", {})
        for directory, subdirs in structure.items():
            for subdir in subdirs:
                full_path = f"{directory}{subdir}__init__.py"
                files[full_path] = self._generate_init_file(directory, subdir)
        
        # Generate configuration files
        files.update(self._generate_config_files(template, project_name))
        
        return {
            "template_id": template_id,
            "project_name": project_name,
            "files": files,
            "structure": structure
        }
    
    def _generate_init_file(self, directory: str, subdir: str) -> str:
        """Generate __init__.py content"""
        return f'"""\n{directory}{subdir} module\n"""\n'
    
    def _generate_config_files(self, template: Dict, project_name: str) -> Dict[str, str]:
        """Generate configuration files based on template"""
        files = {}
        stack = template.get("stack", {})
        
        # Package.json for Node/TypeScript projects
        if any("Node" in str(v) or "Express" in str(v) or "React" in str(v) or "Vue" in str(v) 
               for v in stack.values()):
            files["package.json"] = json.dumps({
                "name": project_name,
                "version": "1.0.0",
                "description": template.get("description", ""),
                "scripts": {
                    "dev": "npm run dev",
                    "build": "npm run build",
                    "start": "npm start"
                }
            }, indent=2)
        
        # Requirements.txt for Python projects
        if any("Python" in str(v) for v in stack.values()):
            files["requirements.txt"] = "# Python dependencies\n"
            if "FastAPI" in str(stack):
                files["requirements.txt"] += "fastapi\nuvicorn\nsqlalchemy\n"
        
        # Docker-compose for multi-service projects
        if "services" in template.get("structure", {}):
            files["docker-compose.yml"] = self._generate_docker_compose(template)
        
        return files
    
    def _generate_docker_compose(self, template: Dict) -> str:
        """Generate docker-compose.yml"""
        return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=dbname
"""
    
    def _load_custom_templates(self):
        """Load custom templates from disk"""
        catalog_file = self.templates_dir / "custom_templates.json"
        if catalog_file.exists():
            try:
                self.custom_templates = json.loads(catalog_file.read_text())
            except:
                self.custom_templates = {}
    
    def _save_custom_templates(self):
        """Save custom templates to disk"""
        catalog_file = self.templates_dir / "custom_templates.json"
        catalog_file.write_text(json.dumps(self.custom_templates, indent=2))
    
    def get_template_recommendations(self, requirements: str) -> List[Dict[str, Any]]:
        """
        Recommend templates based on requirements
        
        Args:
            requirements: Text description of project requirements
            
        Returns:
            List of recommended templates with scores
        """
        recommendations = []
        keywords = requirements.lower()
        
        for template_id, template in self.BUILTIN_TEMPLATES.items():
            score = 0
            reasons = []
            
            # Check template name and description
            if any(word in template.get("name", "").lower() for word in keywords.split()):
                score += 2
                reasons.append("Name matches requirements")
            
            if any(word in template.get("description", "").lower() for word in keywords.split()):
                score += 1
                reasons.append("Description matches requirements")
            
            # Check stack
            stack_str = json.dumps(template.get("stack", {})).lower()
            if any(word in stack_str for word in keywords.split()):
                score += 3
                reasons.append("Technology stack matches")
            
            if score > 0:
                recommendations.append({
                    "template_id": template_id,
                    "template": template,
                    "score": score,
                    "reasons": reasons
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
