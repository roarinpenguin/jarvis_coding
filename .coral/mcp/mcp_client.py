#!/usr/bin/env python3
"""
MCP Client for CoralCollective
Provides Python interface to MCP servers for agent integration
"""

import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPServer:
    """Represents an MCP server configuration"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str] = None
    enabled: bool = True
    permissions: List[str] = None


class MCPClient:
    """MCP Client for CoralCollective agents"""
    
    def __init__(self, config_path: str = "mcp/configs/mcp_config.yaml"):
        self.config_path = Path(config_path)
        self.servers: Dict[str, MCPServer] = {}
        self.active_connections = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load MCP configuration from file"""
        if self.config_path.suffix == '.yaml':
            import yaml
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        
        config = self.config  # Keep compatibility
        
        for server_name, server_config in config.get('mcp_servers', {}).items():
            if server_config.get('enabled', True):
                self.servers[server_name] = MCPServer(
                    name=server_name,
                    command=server_config['command'],
                    args=server_config.get('args', []),
                    env=server_config.get('env', {}),
                    permissions=server_config.get('permissions', [])
                )
    
    async def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found in configuration")
            return False
        
        server = self.servers[server_name]
        
        try:
            # Build command with environment variables
            env = os.environ.copy()
            if server.env:
                env.update(server.env)
            
            # Start the MCP server process
            process = await asyncio.create_subprocess_exec(
                server.command,
                *server.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.active_connections[server_name] = process
            logger.info(f"Connected to {server_name} MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            return False
    
    async def execute_tool(self, server_name: str, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool on an MCP server"""
        if server_name not in self.active_connections:
            if not await self.connect_server(server_name):
                return None
        
        process = self.active_connections[server_name]
        
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            },
            "id": 1
        }
        
        try:
            # Send request to server
            process.stdin.write(json.dumps(request).encode() + b'\n')
            await process.stdin.drain()
            
            # Read response
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode())
            
            if 'error' in response:
                logger.error(f"Tool execution error: {response['error']}")
                return None
            
            return response.get('result')
            
        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name}: {e}")
            return None
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools from an MCP server"""
        if server_name not in self.active_connections:
            if not await self.connect_server(server_name):
                return []
        
        process = self.active_connections[server_name]
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        try:
            process.stdin.write(json.dumps(request).encode() + b'\n')
            await process.stdin.drain()
            
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode())
            
            return response.get('result', {}).get('tools', [])
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name in self.active_connections:
            process = self.active_connections[server_name]
            process.terminate()
            await process.wait()
            del self.active_connections[server_name]
            logger.info(f"Disconnected from {server_name} MCP server")
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        for server_name in list(self.active_connections.keys()):
            await self.disconnect_server(server_name)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools from all configured servers"""
        tools = []
        for server_name, server in self.servers.items():
            if server.enabled:
                tools.append(f"{server_name}: {', '.join(server.permissions or ['all'])}")
        return tools
    
    def get_tools_for_agent(self, agent_id: str) -> Dict[str, List[str]]:
        """Get available tools for a specific agent based on permissions"""
        # Check agent permissions in config
        if hasattr(self, 'config') and 'agent_permissions' in self.config:
            agent_perms = self.config.get('agent_permissions', {}).get(agent_id, {})
            return agent_perms.get('allowed_tools', {})
        return {}


class AgentMCPInterface:
    """High-level MCP interface for CoralCollective agents"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.client = MCPClient()
        self.allowed_servers = self._get_allowed_servers()
    
    def _get_allowed_servers(self) -> List[str]:
        """Get list of MCP servers allowed for this agent type"""
        # Define agent-specific server permissions
        agent_permissions = {
            'backend_developer': ['github', 'postgres', 'filesystem', 'docker'],
            'frontend_developer': ['github', 'filesystem', 'brave-search'],
            'devops_deployment': ['docker', 'github', 'filesystem'],
            'qa_testing': ['github', 'filesystem', 'e2b'],
            'project_architect': ['github', 'linear', 'notion'],
            'security_specialist': ['github', 'sentry'],
            'database_specialist': ['postgres', 'mongodb', 'redis'],
            'technical_writer': ['notion', 'github', 'filesystem'],
            'model_strategy_specialist': ['github', 'filesystem']
        }
        
        return agent_permissions.get(self.agent_type, ['filesystem'])
    
    async def github_create_issue(self, title: str, body: str, labels: List[str] = None) -> Dict:
        """Create a GitHub issue"""
        if 'github' not in self.allowed_servers:
            logger.warning(f"Agent {self.agent_type} not allowed to use GitHub server")
            return None
        
        params = {
            'title': title,
            'body': body,
            'labels': labels or []
        }
        
        return await self.client.execute_tool('github', 'create_issue', params)
    
    async def filesystem_read(self, path: str) -> str:
        """Read a file from the filesystem"""
        if 'filesystem' not in self.allowed_servers:
            logger.warning(f"Agent {self.agent_type} not allowed to use Filesystem server")
            return None
        
        params = {'path': path}
        result = await self.client.execute_tool('filesystem', 'read_file', params)
        return result.get('content') if result else None
    
    async def filesystem_write(self, path: str, content: str) -> bool:
        """Write a file to the filesystem"""
        if 'filesystem' not in self.allowed_servers:
            logger.warning(f"Agent {self.agent_type} not allowed to use Filesystem server")
            return False
        
        params = {
            'path': path,
            'content': content
        }
        
        result = await self.client.execute_tool('filesystem', 'write_file', params)
        return result.get('success', False) if result else False
    
    async def database_query(self, query: str, params: List[Any] = None) -> List[Dict]:
        """Execute a database query"""
        if 'postgres' not in self.allowed_servers:
            logger.warning(f"Agent {self.agent_type} not allowed to use Database server")
            return []
        
        query_params = {
            'query': query,
            'params': params or []
        }
        
        result = await self.client.execute_tool('postgres', 'execute_query', query_params)
        return result.get('rows', []) if result else []
    
    async def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search the web using Brave Search"""
        if 'brave-search' not in self.allowed_servers:
            logger.warning(f"Agent {self.agent_type} not allowed to use Brave Search server")
            return []
        
        params = {
            'query': query,
            'max_results': max_results
        }
        
        result = await self.client.execute_tool('brave-search', 'search', params)
        return result.get('results', []) if result else []
    
    async def docker_run(self, image: str, command: str = None, env: Dict[str, str] = None) -> str:
        """Run a Docker container"""
        if 'docker' not in self.allowed_servers:
            logger.warning(f"Agent {self.agent_type} not allowed to use Docker server")
            return None
        
        params = {
            'image': image,
            'command': command,
            'environment': env or {}
        }
        
        result = await self.client.execute_tool('docker', 'run_container', params)
        return result.get('output') if result else None


# Example usage
async def main():
    """Example usage of MCP client"""
    
    # Create interface for backend developer agent
    backend_interface = AgentMCPInterface('backend_developer')
    
    # Read a file
    content = await backend_interface.filesystem_read('README.md')
    if content:
        print(f"Read {len(content)} characters from README.md")
    
    # Create a GitHub issue
    issue = await backend_interface.github_create_issue(
        title="Test Issue from MCP",
        body="This is a test issue created via MCP",
        labels=["test", "mcp"]
    )
    if issue:
        print(f"Created issue: {issue}")
    
    # Execute a database query
    results = await backend_interface.database_query(
        "SELECT * FROM users LIMIT 5"
    )
    print(f"Query returned {len(results)} rows")
    
    # Clean up
    await backend_interface.client.disconnect_all()


if __name__ == "__main__":
    asyncio.run(main())