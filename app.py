"""
Multi-Agent AI Full-Stack Code Generator

An advanced AI system with specialized agents for generating production-ready code
across multiple programming languages and frameworks.
"""

import os
import asyncio
import httpx
import streamlit as st
from datetime import datetime
from secrets_utils import setup_secrets

# Setup secrets
setup_secrets()

# Page config
st.set_page_config(
    page_title="Multi-Agent AI Code Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components after page config
from core.orchestrator import AgentOrchestrator
from agents import (
    ArchitectureAgent,
    CodeGeneratorAgent,
    CodeAnalyzerAgent,
    ExecutionAgent,
    LibraryManagerAgent
)
from ai_providers import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    LocalServerProvider,
)
from templates import TemplateManager
from utils import format_code, parse_json_response, create_file_tree


# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'agents_initialized' not in st.session_state:
    st.session_state.agents_initialized = False
if 'project_history' not in st.session_state:
    st.session_state.project_history = []
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'library_manager' not in st.session_state:
    st.session_state.library_manager = None
if 'template_manager' not in st.session_state:
    st.session_state.template_manager = TemplateManager()


def initialize_ai_provider(provider_type: str, api_key: str, model: str):
    """Initialize AI provider"""
    if provider_type == "OpenAI":
        return OpenAIProvider(api_key=api_key, model=model)
    elif provider_type == "Anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    elif provider_type == "Gemini":
        return GeminiProvider(api_key=api_key, model=model)
    elif provider_type == "Local (Ollama)":
        return OllamaProvider(model=model)
    elif provider_type == "Local Server":
        return LocalServerProvider(model=model)
    return None


def provider_requires_key(provider_type: str) -> bool:
    return provider_type in {"OpenAI", "Anthropic", "Gemini"}


@st.cache_data(ttl=30)
def get_ollama_models(base_url: str) -> list[str]:
    """Fetch installed Ollama models from local Ollama server."""
    try:
        response = httpx.get(f"{base_url}/api/tags", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        models = [item.get("name") for item in data.get("models", []) if item.get("name")]
        return sorted(models)
    except Exception:
        return []


@st.cache_data(ttl=30)
def get_local_server_models(base_url: str) -> list[str]:
    """Fetch installed models from local AI server."""
    try:
        response = httpx.get(f"{base_url}/models", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        models = [item.get("name") for item in data.get("models", []) if item.get("name")]
        return sorted(models)
    except Exception:
        return []


def resolve_api_key(provider_type: str, manual_key: str) -> str:
    """Resolve API key from manual input, Streamlit secrets, or env vars."""
    if not provider_requires_key(provider_type):
        return ""

    if manual_key:
        return manual_key

    provider_map = {
        "OpenAI": {
            "secrets_path": ("openai", "api_key"),
            "env_vars": ["OPENAI_API_KEY"],
        },
        "Anthropic": {
            "secrets_path": ("anthropic", "api_key"),
            "env_vars": ["ANTHROPIC_API_KEY"],
        },
        "Gemini": {
            "secrets_path": ("gemini", "api_key"),
            "env_vars": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        },
    }

    config = provider_map.get(provider_type, {})
    secrets_path = config.get("secrets_path")
    if secrets_path:
        section, key = secrets_path
        try:
            if section in st.secrets and key in st.secrets[section]:
                return st.secrets[section][key]
        except Exception:
            pass

    for env_var in config.get("env_vars", []):
        env_value = os.getenv(env_var)
        if env_value:
            return env_value

    return ""


def initialize_agents(ai_provider):
    """Initialize all agents with AI provider"""
    orchestrator = AgentOrchestrator()
    
    # Create agents
    arch_agent = ArchitectureAgent(ai_provider=ai_provider)
    code_agent = CodeGeneratorAgent(ai_provider=ai_provider)
    analyzer_agent = CodeAnalyzerAgent(ai_provider=ai_provider)
    exec_agent = ExecutionAgent(ai_provider=ai_provider)
    lib_agent = LibraryManagerAgent(ai_provider=ai_provider)
    
    # Register agents
    orchestrator.register_agent("architecture", arch_agent)
    orchestrator.register_agent("code_generator", code_agent)
    orchestrator.register_agent("analyzer", analyzer_agent)
    orchestrator.register_agent("executor", exec_agent)
    orchestrator.register_agent("library", lib_agent)
    
    # Register workflows
    orchestrator.register_workflow(
        "full_stack_development",
        ["architecture", "code_generator", "analyzer"]
    )
    
    orchestrator.register_workflow(
        "code_review",
        ["analyzer", "code_generator"]
    )
    
    st.session_state.orchestrator = orchestrator
    st.session_state.library_manager = lib_agent
    st.session_state.agents_initialized = True
    
    return orchestrator


# Sidebar - Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # AI Provider Selection
    st.subheader("AI Provider")
    provider_type = st.selectbox(
        "Select AI Provider",
        ["OpenAI", "Anthropic", "Gemini", "Local (Ollama)", "Local Server"],
        help="Choose your AI model provider"
    )
    
    # Model selection based on provider
    if provider_type == "OpenAI":
        model = st.selectbox("Model", ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
        api_key_placeholder = "sk-..."
    elif provider_type == "Anthropic":
        model = st.selectbox("Model", ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"])
        api_key_placeholder = "sk-ant-..."
    elif provider_type == "Gemini":
        model = st.selectbox("Model", ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"])
        api_key_placeholder = "AIza..."
    elif provider_type == "Local (Ollama)":
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        installed_models = get_ollama_models(ollama_base_url)
        default_models = [
            "phi3:instruct-q4_0",
            "mistral:instruct-q4_0",
            "llama3.1:8b-instruct-q4_0",
            "llama3.1:8b-instruct-q5_0",
            "phi3",
            "mistral",
            "llama3.1",
            "llama3",
            "qwen2.5:7b",
        ]
        model_options = installed_models or default_models
        model = st.selectbox("Model", model_options)
        api_key_placeholder = "Not required"
    else:  # Local Server
        server_url = os.getenv("LOCAL_AI_SERVER_URL", "http://localhost:8000")
        installed_models = get_local_server_models(server_url)
        if installed_models:
            model = st.selectbox("Model", installed_models)
        else:
            model = st.text_input("Model", value="llama3.1:8b-instruct-q4_0")
        api_key_placeholder = "Not required"
    
    requires_key = provider_requires_key(provider_type)
    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder=api_key_placeholder,
        help="Enter your API key for the selected provider",
        disabled=not requires_key
    )

    resolved_api_key = resolve_api_key(provider_type, api_key_input)
    if not requires_key:
        if provider_type == "Local (Ollama)":
            st.caption("🧠 Local Ollama: no API key required.")
        elif provider_type == "Local Server":
            st.caption("🖥️ Local AI Server: no API key required.")
    elif not api_key_input and resolved_api_key:
        st.caption("🔐 Using API key from environment or Streamlit secrets.")

    if st.button("Initialize Agents", type="primary", disabled=requires_key and not resolved_api_key):
        with st.spinner("Initializing AI agents..."):
            try:
                ai_provider = initialize_ai_provider(provider_type, resolved_api_key, model)
                initialize_agents(ai_provider)
                st.success("✅ All agents initialized!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Agent Status
    if st.session_state.agents_initialized:
        st.subheader("🤖 Active Agents")
        agents = st.session_state.orchestrator.get_registered_agents()
        for agent in agents:
            st.success(f"✓ {agent.replace('_', ' ').title()}")
    else:
        st.info("Configure AI provider to activate agents")


# Main Content
st.title("🤖 Multi-Agent AI Full-Stack Code Generator")
st.markdown("### Generate production-ready code with specialized AI agents")

if not st.session_state.agents_initialized:
    st.warning("⚠️ Please configure and initialize AI agents in the sidebar to get started.")
    
    # Feature Overview
    st.markdown("---")
    st.markdown("## 🌟 Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏗️ Architecture Design")
        st.markdown("""
        - System architecture planning
        - Technology stack selection
        - Component design
        - API design patterns
        """)
    
    with col2:
        st.markdown("### 💻 Code Generation")
        st.markdown("""
        - Multi-language support
        - Clean, documented code
        - Best practices
        - Full-stack applications
        """)
    
    with col3:
        st.markdown("### 🔍 Code Analysis")
        st.markdown("""
        - Quality analysis
        - Security scanning
        - Performance optimization
        - Billions of lines support
        """)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("### ⚡ Code Execution")
        st.markdown("""
        - Syntax validation
        - Test execution
        - Dry run analysis
        - Performance benchmarks
        """)
    
    with col5:
        st.markdown("### 📚 Library Management")
        st.markdown("""
        - Component catalog
        - Code reusability
        - Version control
        - Smart search
        """)
    
    with col6:
        st.markdown("### 📋 Templates")
        st.markdown("""
        - Project templates
        - Quick start
        - Best practices
        - Multiple frameworks
        """)
    
    st.markdown("---")
    st.markdown("### 🛠️ Supported Technologies")
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("**Languages**")
        st.markdown("• Python • JavaScript • TypeScript • Go • Rust • Java")
    
    with tech_col2:
        st.markdown("**Frameworks**")
        st.markdown("• React • Vue • FastAPI • Django • Express • Next.js")
    
    with tech_col3:
        st.markdown("**Databases**")
        st.markdown("• PostgreSQL • MongoDB • MySQL • Redis • DynamoDB")

else:
    # Main application tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 New Project",
        "💻 Code Generation",
        "🔍 Code Analysis",
        "📚 Library",
        "📋 Templates"
    ])
    
    # Tab 1: New Project
    with tab1:
        st.header("Create New Full-Stack Project")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            project_name = st.text_input("Project Name", placeholder="my-awesome-app")
            
            requirements = st.text_area(
                "Project Requirements",
                placeholder="Describe your project...\n\nExample: Build a task management web application with user authentication, real-time updates, and mobile responsiveness.",
                height=200
            )
            
            col_lang1, col_lang2 = st.columns(2)
            
            with col_lang1:
                languages = st.multiselect(
                    "Programming Languages",
                    ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java"],
                    default=["Python", "JavaScript"]
                )
            
            with col_lang2:
                scale = st.selectbox(
                    "Project Scale",
                    ["small", "medium", "large", "enterprise"]
                )
            
            frameworks = st.text_input(
                "Preferred Frameworks (optional)",
                placeholder="e.g., React, FastAPI, PostgreSQL"
            )
        
        with col2:
            st.markdown("### 💡 Quick Templates")
            template_manager = st.session_state.template_manager
            templates = template_manager.list_templates()
            
            for template in templates[:5]:
                if st.button(template['name'], key=f"template_{template['id']}", width="stretch"):
                    st.session_state.selected_template = template['id']
                    st.rerun()
        
        if st.button("🏗️ Generate Architecture", type="primary", disabled=not requirements):
            with st.spinner("AI agents are designing your architecture..."):
                async def design_architecture():
                    task = {
                        "requirements": requirements,
                        "languages": languages,
                        "frameworks": frameworks.split(',') if frameworks else [],
                        "scale": scale
                    }
                    
                    result = await st.session_state.orchestrator.execute_single_agent(
                        "architecture", task
                    )
                    return result
                
                result = asyncio.run(design_architecture())
                
                if result.get("status") == "success":
                    st.success("✅ Architecture design completed!")
                    
                    architecture = result.get("architecture", {})
                    
                    # Display architecture
                    st.markdown("### 📐 System Architecture")
                    
                    if "project_name" in architecture:
                        st.markdown(f"**Project:** {architecture['project_name']}")
                    
                    if "architecture_type" in architecture:
                        st.markdown(f"**Type:** {architecture['architecture_type']}")
                    
                    if "tech_stack" in architecture:
                        st.markdown("#### 🛠️ Technology Stack")
                        st.json(architecture['tech_stack'])
                    
                    if "directory_structure" in architecture:
                        st.markdown("#### 📁 Project Structure")
                        tree = create_file_tree(architecture['directory_structure'])
                        st.text(tree)
                    
                    if "api_design" in architecture:
                        st.markdown("#### 🔌 API Design")
                        st.json(architecture['api_design'])
                    
                    # Save to session
                    st.session_state.current_project = {
                        "name": project_name or architecture.get("project_name", "project"),
                        "architecture": architecture,
                        "requirements": requirements,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    st.info("💡 Go to 'Code Generation' tab to start building your project!")
                else:
                    st.error("❌ Failed to generate architecture")
                    st.json(result)
    
    # Tab 2: Code Generation
    with tab2:
        st.header("Generate Code")
        
        if st.session_state.current_project:
            project = st.session_state.current_project
            st.success(f"📂 Current Project: {project['name']}")
            
            with st.expander("View Architecture", expanded=False):
                st.json(project['architecture'])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            component_spec = st.text_area(
                "Component Specification",
                placeholder="Describe the component to generate...\n\nExample: Create a user authentication API with JWT tokens, including login, register, and password reset endpoints.",
                height=150
            )
            
            col_lang, col_framework = st.columns(2)
            
            with col_lang:
                code_language = st.selectbox(
                    "Language",
                    ["python", "javascript", "typescript", "go", "rust", "java"]
                )
            
            with col_framework:
                code_framework = st.text_input("Framework (optional)", placeholder="FastAPI, Express, etc.")
        
        with col2:
            st.markdown("### ⚙️ Options")
            include_tests = st.checkbox("Include unit tests", value=True)
            include_docs = st.checkbox("Include documentation", value=True)
        
        if st.button("🎨 Generate Code", type="primary", disabled=not component_spec):
            with st.spinner("AI agents are writing code..."):
                async def generate_code():
                    task = {
                        "component_spec": component_spec,
                        "language": code_language,
                        "framework": code_framework,
                        "architecture": st.session_state.current_project.get("architecture", {}) if st.session_state.current_project else {}
                    }
                    
                    result = await st.session_state.orchestrator.execute_single_agent(
                        "code_generator", task
                    )
                    return result
                
                result = asyncio.run(generate_code())
                
                if result.get("status") == "success":
                    st.success("✅ Code generated successfully!")
                    
                    code_files = result.get("code_files", {})
                    
                    if "files" in code_files:
                        st.markdown("### 📝 Generated Files")
                        
                        for file_info in code_files["files"]:
                            with st.expander(f"📄 {file_info.get('path', 'file')}"):
                                st.markdown(f"**Description:** {file_info.get('description', 'N/A')}")
                                
                                if "dependencies" in file_info and file_info["dependencies"]:
                                    st.markdown(f"**Dependencies:** {', '.join(file_info['dependencies'])}")
                                
                                st.code(file_info.get('content', ''), language=code_language)
                                
                                # Save to library button
                                if st.button(f"💾 Save to Library", key=f"save_{file_info.get('path')}"):
                                    async def save_to_library():
                                        save_task = {
                                            "action": "store",
                                            "name": file_info.get('path', 'component').replace('/', '_'),
                                            "code": file_info.get('content', ''),
                                            "language": code_language,
                                            "description": file_info.get('description', ''),
                                            "category": "generated"
                                        }
                                        return await st.session_state.library_manager.process(save_task)
                                    
                                    save_result = asyncio.run(save_to_library())
                                    if save_result.get("status") == "stored":
                                        st.success("✅ Saved to library!")
                        
                        if "setup_instructions" in code_files:
                            st.markdown("### 🚀 Setup Instructions")
                            st.info(code_files["setup_instructions"])
                        
                        if "usage_example" in code_files:
                            st.markdown("### 📖 Usage Example")
                            st.code(code_files["usage_example"], language=code_language)
                    else:
                        st.markdown("### 📝 Generated Code")
                        st.text(code_files.get("raw_response", "No code generated"))
                else:
                    st.error("❌ Failed to generate code")
                    st.json(result)
    
    # Tab 3: Code Analysis
    with tab3:
        st.header("Code Analysis")
        
        analysis_code = st.text_area(
            "Paste Code to Analyze",
            height=300,
            placeholder="Paste your code here for analysis..."
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            analysis_language = st.selectbox(
                "Language",
                ["python", "javascript", "typescript", "go", "rust", "java"],
                key="analysis_lang"
            )
        
        with col2:
            analysis_types = st.multiselect(
                "Analysis Types",
                ["quality", "security", "performance", "style", "architecture"],
                default=["quality", "security"]
            )
        
        with col3:
            st.markdown("### ")
            analyze_btn = st.button("🔍 Analyze Code", type="primary", disabled=not analysis_code)
        
        if analyze_btn:
            with st.spinner("AI agents are analyzing your code..."):
                async def analyze_code():
                    task = {
                        "code": analysis_code,
                        "language": analysis_language,
                        "analysis_types": analysis_types,
                        "file_path": "user_code"
                    }
                    
                    result = await st.session_state.orchestrator.execute_single_agent(
                        "analyzer", task
                    )
                    return result
                
                result = asyncio.run(analyze_code())
                
                if result.get("status") == "success":
                    st.success("✅ Analysis completed!")
                    
                    analysis = result.get("analysis", {})
                    
                    if "overall_score" in analysis:
                        score = analysis["overall_score"]
                        st.metric("Overall Score", f"{score}/100")
                    
                    if "summary" in analysis:
                        st.info(analysis["summary"])
                    
                    if "issues" in analysis and analysis["issues"]:
                        st.markdown("### ⚠️ Issues Found")
                        
                        # Group by severity
                        high = [i for i in analysis["issues"] if i.get("severity") == "high"]
                        medium = [i for i in analysis["issues"] if i.get("severity") == "medium"]
                        low = [i for i in analysis["issues"] if i.get("severity") == "low"]
                        
                        if high:
                            with st.expander(f"🔴 High Priority ({len(high)})", expanded=True):
                                for issue in high:
                                    st.error(f"**Line {issue.get('line', 'N/A')}:** {issue.get('message', 'N/A')}")
                                    if 'suggestion' in issue:
                                        st.markdown(f"💡 **Fix:** {issue['suggestion']}")
                        
                        if medium:
                            with st.expander(f"🟡 Medium Priority ({len(medium)})"):
                                for issue in medium:
                                    st.warning(f"**Line {issue.get('line', 'N/A')}:** {issue.get('message', 'N/A')}")
                                    if 'suggestion' in issue:
                                        st.markdown(f"💡 **Fix:** {issue['suggestion']}")
                        
                        if low:
                            with st.expander(f"🟢 Low Priority ({len(low)})"):
                                for issue in low:
                                    st.info(f"**Line {issue.get('line', 'N/A')}:** {issue.get('message', 'N/A')}")
                    
                    if "recommendations" in analysis and analysis["recommendations"]:
                        st.markdown("### 💡 Recommendations")
                        for rec in analysis["recommendations"][:10]:
                            st.markdown(f"- **{rec.get('category', 'General')}:** {rec.get('description', 'N/A')}")
                    
                    if "metrics" in analysis:
                        st.markdown("### 📊 Code Metrics")
                        st.json(analysis["metrics"])
                else:
                    st.error("❌ Analysis failed")
                    st.json(result)
    
    # Tab 4: Library
    with tab4:
        st.header("Code Library")
        
        tab_search, tab_browse, tab_add = st.tabs(["🔍 Search", "📚 Browse", "➕ Add Component"])
        
        with tab_search:
            search_query = st.text_input("Search components", placeholder="Enter search keywords...")
            
            col1, col2 = st.columns(2)
            with col1:
                filter_language = st.selectbox("Filter by Language", ["All", "python", "javascript", "typescript", "go"])
            with col2:
                filter_category = st.selectbox("Filter by Category", ["All", "general", "generated", "custom"])
            
            if st.button("Search") or search_query:
                async def search_library():
                    task = {
                        "action": "search",
                        "query": search_query,
                        "language": None if filter_language == "All" else filter_language,
                        "category": None if filter_category == "All" else filter_category
                    }
                    return await st.session_state.library_manager.process(task)
                
                result = asyncio.run(search_library())
                
                if result.get("status") == "success":
                    results = result.get("results", [])
                    st.info(f"Found {len(results)} components")
                    
                    for comp in results[:20]:
                        with st.expander(f"📦 {comp['name']} ({comp['language']})"):
                            st.markdown(f"**Description:** {comp['description']}")
                            st.markdown(f"**Category:** {comp['category']}")
                            st.markdown(f"**Usage Count:** {comp['usage_count']}")
                            
                            if st.button("📖 View Code", key=f"view_{comp['id']}"):
                                async def retrieve_component():
                                    return await st.session_state.library_manager.process({
                                        "action": "retrieve",
                                        "component_id": comp['id']
                                    })
                                
                                retrieve_result = asyncio.run(retrieve_component())
                                if retrieve_result.get("status") == "retrieved":
                                    st.code(retrieve_result['code'], language=comp['language'])
        
        with tab_browse:
            async def list_components():
                return await st.session_state.library_manager.process({"action": "list"})
            
            list_result = asyncio.run(list_components())
            
            if list_result.get("status") == "success":
                by_category = list_result.get("by_category", {})
                
                st.info(f"Total Components: {list_result.get('total_components', 0)}")
                
                for category, components in by_category.items():
                    with st.expander(f"📁 {category.upper()} ({len(components)} components)"):
                        for comp in components:
                            st.markdown(f"**{comp['name']}** - {comp['description']}")
        
        with tab_add:
            st.subheader("Add New Component")
            
            new_comp_name = st.text_input("Component Name")
            new_comp_desc = st.text_area("Description")
            new_comp_lang = st.selectbox("Language", ["python", "javascript", "typescript", "go"])
            new_comp_category = st.text_input("Category", value="custom")
            new_comp_code = st.text_area("Code", height=300)
            
            if st.button("💾 Save Component", disabled=not (new_comp_name and new_comp_code)):
                async def save_component():
                    return await st.session_state.library_manager.process({
                        "action": "store",
                        "name": new_comp_name,
                        "code": new_comp_code,
                        "language": new_comp_lang,
                        "description": new_comp_desc,
                        "category": new_comp_category
                    })
                
                save_result = asyncio.run(save_component())
                
                if save_result.get("status") == "stored":
                    st.success("✅ Component saved to library!")
                    st.json(save_result['component'])
    
    # Tab 5: Templates
    with tab5:
        st.header("Project Templates")
        
        template_manager = st.session_state.template_manager
        templates = template_manager.list_templates()
        
        st.info(f"Available Templates: {len(templates)}")
        
        # Display templates in grid
        for i in range(0, len(templates), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(templates):
                    template = templates[i]
                    with st.container():
                        st.markdown(f"### {template['name']}")
                        st.markdown(template['description'])
                        
                        if 'stack' in template:
                            st.markdown("**Stack:**")
                            for key, value in template['stack'].items():
                                st.markdown(f"- {key}: {value}")
                        
                        if st.button("Use Template", key=f"use_template_{i}"):
                            st.session_state.selected_template = template['id']
                            st.info("Template selected! Go to 'New Project' tab to use it.")
            
            with col2:
                if i + 1 < len(templates):
                    template = templates[i + 1]
                    with st.container():
                        st.markdown(f"### {template['name']}")
                        st.markdown(template['description'])
                        
                        if 'stack' in template:
                            st.markdown("**Stack:**")
                            for key, value in template['stack'].items():
                                st.markdown(f"- {key}: {value}")
                        
                        if st.button("Use Template", key=f"use_template_{i+1}"):
                            st.session_state.selected_template = template['id']
                            st.info("Template selected! Go to 'New Project' tab to use it.")

# Footer
st.markdown("---")
st.markdown("**Multi-Agent AI Full-Stack Code Generator** | Powered by Advanced AI Models")
