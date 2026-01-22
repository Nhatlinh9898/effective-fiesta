"""
Agent Orchestrator - Coordinates multiple agents to complete complex tasks
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio


class AgentOrchestrator:
    """
    Orchestrates multiple agents to work together on complex tasks
    Manages workflow, dependencies, and communication between agents
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.workflows: Dict[str, List[str]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
    def register_agent(self, agent_type: str, agent):
        """Register an agent with the orchestrator"""
        self.agents[agent_type] = agent
        
    def register_workflow(self, workflow_name: str, agent_sequence: List[str]):
        """
        Register a workflow - sequence of agents to execute
        
        Args:
            workflow_name: Name of the workflow
            agent_sequence: List of agent types in execution order
        """
        self.workflows[workflow_name] = agent_sequence
        
    async def execute_workflow(self, workflow_name: str, initial_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered workflow
        
        Args:
            workflow_name: Name of workflow to execute
            initial_task: Initial task data
            
        Returns:
            Final results after all agents complete
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        agent_sequence = self.workflows[workflow_name]
        current_task = initial_task
        results = {
            "workflow": workflow_name,
            "started_at": datetime.now().isoformat(),
            "agent_results": []
        }
        
        for agent_type in agent_sequence:
            if agent_type not in self.agents:
                raise ValueError(f"Agent type '{agent_type}' not registered")
            
            agent = self.agents[agent_type]
            
            # Execute agent
            agent_result = await agent.process(current_task)
            
            results["agent_results"].append({
                "agent": agent_type,
                "timestamp": datetime.now().isoformat(),
                "result": agent_result
            })
            
            # Update task for next agent
            current_task = {
                **current_task,
                "previous_results": results["agent_results"]
            }
        
        results["completed_at"] = datetime.now().isoformat()
        results["final_output"] = results["agent_results"][-1]["result"] if results["agent_results"] else None
        
        self.execution_history.append(results)
        
        return results
    
    async def execute_parallel(self, agent_types: List[str], task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute multiple agents in parallel
        
        Args:
            agent_types: List of agent types to execute
            task: Task to process
            
        Returns:
            List of results from all agents
        """
        tasks = []
        for agent_type in agent_types:
            if agent_type not in self.agents:
                raise ValueError(f"Agent type '{agent_type}' not registered")
            agent = self.agents[agent_type]
            tasks.append(agent.process(task))
        
        results = await asyncio.gather(*tasks)
        return list(results)
    
    async def execute_single_agent(self, agent_type: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single agent
        
        Args:
            agent_type: Type of agent to execute
            task: Task to process
            
        Returns:
            Agent result
        """
        if agent_type not in self.agents:
            raise ValueError(f"Agent type '{agent_type}' not registered")
        
        agent = self.agents[agent_type]
        result = await agent.process(task)
        
        self.execution_history.append({
            "type": "single_agent",
            "agent": agent_type,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        return result
    
    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent types"""
        return list(self.agents.keys())
    
    def get_registered_workflows(self) -> Dict[str, List[str]]:
        """Get all registered workflows"""
        return self.workflows.copy()
    
    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get execution history"""
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
