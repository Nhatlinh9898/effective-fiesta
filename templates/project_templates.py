"""
Pre-defined Project Templates for common architectures
"""

PROJECT_TEMPLATES = {
    "rest_api": {
        "name": "REST API Backend",
        "description": "RESTful API with database and authentication",
        "languages": ["python", "javascript", "go"],
        "components": {
            "python": {
                "framework": "FastAPI",
                "structure": {
                    "app/": ["main.py", "models.py", "schemas.py", "crud.py", "database.py"],
                    "app/routers/": ["auth.py", "users.py", "items.py"],
                    "app/core/": ["config.py", "security.py"],
                    "tests/": ["test_api.py", "test_auth.py"]
                },
                "dependencies": ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib"]
            },
            "javascript": {
                "framework": "Express",
                "structure": {
                    "src/": ["index.js", "app.js"],
                    "src/routes/": ["auth.js", "users.js", "items.js"],
                    "src/models/": ["user.js", "item.js"],
                    "src/middleware/": ["auth.js", "validation.js"],
                    "tests/": ["api.test.js"]
                },
                "dependencies": ["express", "mongoose", "jsonwebtoken", "bcrypt", "dotenv", "jest"]
            }
        }
    },
    
    "web_app": {
        "name": "Full-Stack Web Application",
        "description": "Complete web app with frontend and backend",
        "languages": ["javascript", "typescript"],
        "components": {
            "typescript": {
                "frontend": {
                    "framework": "React + Next.js",
                    "structure": {
                        "src/app/": ["page.tsx", "layout.tsx"],
                        "src/components/": ["Header.tsx", "Footer.tsx", "Layout.tsx"],
                        "src/lib/": ["api.ts", "utils.ts"],
                        "src/types/": ["index.ts"],
                        "public/": ["assets/"]
                    },
                    "dependencies": ["react", "next", "typescript", "tailwindcss"]
                },
                "backend": {
                    "framework": "NestJS",
                    "structure": {
                        "src/": ["main.ts", "app.module.ts"],
                        "src/modules/": ["auth/", "users/", "posts/"],
                        "src/common/": ["guards/", "decorators/", "filters/"]
                    },
                    "dependencies": ["@nestjs/core", "@nestjs/common", "@nestjs/typeorm", "typeorm"]
                }
            }
        }
    },
    
    "microservices": {
        "name": "Microservices Architecture",
        "description": "Distributed microservices with API gateway",
        "languages": ["python", "go", "java"],
        "components": {
            "python": {
                "services": [
                    {
                        "name": "api-gateway",
                        "framework": "FastAPI",
                        "structure": {"app/": ["main.py", "routes.py", "middleware.py"]}
                    },
                    {
                        "name": "auth-service",
                        "framework": "FastAPI",
                        "structure": {"app/": ["main.py", "auth.py", "users.py"]}
                    },
                    {
                        "name": "data-service",
                        "framework": "FastAPI",
                        "structure": {"app/": ["main.py", "models.py", "crud.py"]}
                    }
                ],
                "shared": {
                    "docker-compose.yml": "service orchestration",
                    "common/": ["utils.py", "config.py", "messaging.py"]
                },
                "dependencies": ["fastapi", "uvicorn", "redis", "celery", "pika"]
            }
        }
    },
    
    "data_pipeline": {
        "name": "Data Processing Pipeline",
        "description": "ETL pipeline for data processing and analysis",
        "languages": ["python"],
        "components": {
            "python": {
                "framework": "Airflow + Pandas",
                "structure": {
                    "dags/": ["etl_pipeline.py", "data_validation.py"],
                    "src/extractors/": ["api_extractor.py", "db_extractor.py"],
                    "src/transformers/": ["data_cleaner.py", "data_enricher.py"],
                    "src/loaders/": ["database_loader.py", "file_loader.py"],
                    "src/utils/": ["config.py", "logger.py"],
                    "tests/": ["test_pipeline.py"]
                },
                "dependencies": ["apache-airflow", "pandas", "sqlalchemy", "requests"]
            }
        }
    },
    
    "machine_learning": {
        "name": "ML Model Training & Serving",
        "description": "Machine learning project with training and API serving",
        "languages": ["python"],
        "components": {
            "python": {
                "framework": "FastAPI + PyTorch/TensorFlow",
                "structure": {
                    "src/models/": ["model.py", "train.py", "evaluate.py"],
                    "src/data/": ["dataset.py", "preprocessing.py"],
                    "src/api/": ["main.py", "endpoints.py"],
                    "src/utils/": ["config.py", "metrics.py"],
                    "notebooks/": ["exploration.ipynb"],
                    "tests/": ["test_model.py"]
                },
                "dependencies": ["torch", "scikit-learn", "fastapi", "pandas", "numpy"]
            }
        }
    },
    
    "mobile_backend": {
        "name": "Mobile App Backend",
        "description": "Backend API for mobile applications",
        "languages": ["python", "javascript"],
        "components": {
            "python": {
                "framework": "Django + DRF",
                "structure": {
                    "api/": ["urls.py", "views.py", "serializers.py"],
                    "users/": ["models.py", "views.py", "serializers.py"],
                    "notifications/": ["models.py", "push_notifications.py"],
                    "core/": ["settings.py", "middleware.py"]
                },
                "dependencies": ["django", "djangorestframework", "django-cors-headers", "fcm-django"]
            }
        }
    },
    
    "serverless": {
        "name": "Serverless Application",
        "description": "Serverless functions with event-driven architecture",
        "languages": ["python", "javascript"],
        "components": {
            "python": {
                "framework": "AWS Lambda",
                "structure": {
                    "functions/": ["auth.py", "users.py", "data.py"],
                    "layers/": ["common/utils.py"],
                    "templates/": ["cloudformation.yaml"],
                    "tests/": ["test_functions.py"]
                },
                "dependencies": ["boto3", "aws-lambda-powertools"]
            }
        }
    },
    
    "realtime_app": {
        "name": "Real-time Application",
        "description": "Real-time app with WebSockets",
        "languages": ["javascript", "python"],
        "components": {
            "javascript": {
                "framework": "Socket.io + React",
                "backend": {
                    "structure": {
                        "server/": ["index.js", "socket.js", "auth.js"],
                        "server/events/": ["chat.js", "notifications.js"]
                    }
                },
                "frontend": {
                    "structure": {
                        "src/": ["App.jsx", "socket.js"],
                        "src/components/": ["Chat.jsx", "Notifications.jsx"]
                    }
                },
                "dependencies": ["socket.io", "socket.io-client", "react", "express"]
            }
        }
    },
    
    "cli_tool": {
        "name": "Command-Line Tool",
        "description": "CLI application with commands and options",
        "languages": ["python", "go"],
        "components": {
            "python": {
                "framework": "Click / Typer",
                "structure": {
                    "src/": ["main.py", "cli.py"],
                    "src/commands/": ["init.py", "run.py", "deploy.py"],
                    "src/utils/": ["config.py", "logger.py"],
                    "tests/": ["test_cli.py"]
                },
                "dependencies": ["typer", "rich", "pydantic"]
            },
            "go": {
                "framework": "Cobra",
                "structure": {
                    "cmd/": ["root.go", "init.go", "run.go"],
                    "pkg/": ["config/", "utils/"],
                    "main.go": ""
                },
                "dependencies": ["github.com/spf13/cobra", "github.com/spf13/viper"]
            }
        }
    }
}


def get_template(template_name: str) -> dict:
    """Get a specific template by name"""
    return PROJECT_TEMPLATES.get(template_name)


def list_templates() -> list:
    """List all available templates"""
    return [
        {
            "name": key,
            "title": value["name"],
            "description": value["description"],
            "languages": value["languages"]
        }
        for key, value in PROJECT_TEMPLATES.items()
    ]


def get_templates_by_language(language: str) -> list:
    """Get templates supporting a specific language"""
    return [
        {
            "name": key,
            "title": value["name"],
            "description": value["description"]
        }
        for key, value in PROJECT_TEMPLATES.items()
        if language.lower() in [lang.lower() for lang in value["languages"]]
    ]
