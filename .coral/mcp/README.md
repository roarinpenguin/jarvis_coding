# CoralCollective MCP Integration 🪸

## Overview

Model Context Protocol (MCP) integration enables CoralCollective agents to directly interact with external tools and services, transforming them from prompt-based assistants into fully-integrated development partners.

## Quick Start

### 1. Installation

```bash
# Run the setup script
cd coral_collective
chmod +x mcp/setup_mcp.sh
./mcp/setup_mcp.sh
```

### 2. Configuration

```bash
# Copy and edit the environment file
cp mcp/.env.example mcp/.env
# Edit mcp/.env with your API keys and tokens
```

### 3. Test Installation

```bash
# Test MCP servers
npm run mcp:test

# Or test individual servers
npm run mcp:github
npm run mcp:filesystem
```

## Available MCP Servers

### Core Stack (Tier 1)

| Server | Purpose | Status | Agents |
|--------|---------|--------|--------|
| **GitHub** | Repository management, PRs, issues | ✅ Ready | All |
| **Filesystem** | Secure file operations | ✅ Ready | All |
| **PostgreSQL** | Database operations | ✅ Ready | Backend, Database |
| **Docker** | Container management | ✅ Ready | DevOps, Backend |
| **E2B** | Secure code execution | ✅ Ready | QA, Testing |

### Productivity (Tier 2)

| Server | Purpose | Status | Agents |
|--------|---------|--------|--------|
| **Brave Search** | Web research | ✅ Ready | All |
| **Slack** | Team communication | 🔧 Config needed | Project, DevOps |
| **Linear/Jira** | Project management | 🔧 Config needed | Project Architect |
| **Notion** | Documentation | 🔧 Config needed | Technical Writer |

## Agent-Specific Capabilities

### Backend Developer
```python
# Available MCP servers
- GitHub: Full repository access
- PostgreSQL: Database operations
- Docker: Container management
- Filesystem: Code file operations
- E2B: Test execution
```

### Frontend Developer
```python
# Available MCP servers
- GitHub: Repository management
- Filesystem: Component files
- E2B: Component testing
- Brave Search: Documentation lookup
```

### DevOps & Deployment
```python
# Available MCP servers
- Docker: Container orchestration
- GitHub: CI/CD management
- Filesystem: Config files
- Slack: Deployment notifications
```

## Using MCP with Agents

### Python Integration

```python
from mcp.mcp_client import AgentMCPInterface

# Create interface for specific agent
agent = AgentMCPInterface('backend_developer')

# Read a file
content = await agent.filesystem_read('src/api/server.js')

# Create GitHub issue
issue = await agent.github_create_issue(
    title="Bug: API endpoint failing",
    body="The /users endpoint returns 500 error",
    labels=["bug", "api"]
)

# Execute database query
results = await agent.database_query(
    "SELECT * FROM users WHERE active = true"
)

# Search for documentation
docs = await agent.search_web(
    "Next.js 14 app router documentation"
)
```

### Direct CLI Usage

```bash
# GitHub operations
npx @modelcontextprotocol/server-github create-issue --title "New feature" --body "Description"

# File operations
npx @modelcontextprotocol/server-filesystem read --path "./src/index.js"

# Database queries
npx @modelcontextprotocol/server-postgres query --sql "SELECT * FROM users"
```

## Claude Desktop Integration

### Setup

1. Locate Claude Desktop config:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

2. Add MCP servers configuration:
```json
{
  "mcpServers": {
    "coral-github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    },
    "coral-filesystem": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-filesystem",
        "/path/to/coral_collective"
      ]
    }
  }
}
```

3. Restart Claude Desktop

### Using MCP in Claude

Once configured, you can use MCP tools directly in Claude:

```
"Use the GitHub MCP server to create a new issue for the bug we discussed"

"Read the backend configuration file using the filesystem MCP server"

"Query the users table to find active accounts using the PostgreSQL server"
```

## Security Configuration

### Sandboxing

All file operations are sandboxed to the project directory:

```yaml
filesystem:
  sandboxed: true
  excluded_paths:
    - .env
    - .git
    - secrets/
    - node_modules/
```

### Read-Only Mode

For production databases:

```yaml
postgres:
  mode: read_only  # Prevents write operations
  branch: production
```

### Agent Permissions

Each agent has specific MCP server access:

```yaml
security_specialist:
  servers:
    - github
    - filesystem
  read_only: true  # All operations are read-only
```

## Environment Variables

Required environment variables in `mcp/.env`:

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=coral_collective_dev

# Brave Search
BRAVE_API_KEY=BSA_xxxxxxxxxxxxxxxxxxxx

# E2B (Code Execution)
E2B_API_KEY=e2b_xxxxxxxxxxxxxxxxxxxx

# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# Project
PROJECT_ROOT=/path/to/coral_collective
```

## Troubleshooting

### Common Issues

#### MCP Server Not Found
```bash
# Reinstall the server
npm install -g @modelcontextprotocol/server-github
```

#### Permission Denied
```bash
# Check agent permissions in mcp_config.yaml
# Ensure the agent has access to the required server
```

#### Connection Failed
```bash
# Check environment variables
cat mcp/.env | grep GITHUB_TOKEN

# Test server directly
npx @modelcontextprotocol/server-github --help
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Configuration

### Custom MCP Server

Create a custom MCP server for specific needs:

```javascript
// mcp/servers/custom-server.js
const { Server } = require('@modelcontextprotocol/sdk');

const server = new Server({
  name: 'custom-coral-server',
  version: '1.0.0',
  tools: [
    {
      name: 'custom_tool',
      description: 'Custom tool for CoralCollective',
      inputSchema: {
        type: 'object',
        properties: {
          param: { type: 'string' }
        }
      },
      handler: async ({ param }) => {
        // Tool implementation
        return { result: 'success' };
      }
    }
  ]
});

server.start();
```

### Monitoring

Track MCP usage:

```python
# mcp/monitor.py
import json
from datetime import datetime

def log_mcp_operation(agent, server, operation, result):
    with open('mcp/logs/operations.json', 'a') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'agent': agent,
            'server': server,
            'operation': operation,
            'success': result
        }, f)
        f.write('\n')
```

## Best Practices

1. **Start Small**: Begin with GitHub and Filesystem servers
2. **Test Thoroughly**: Validate each integration before production
3. **Monitor Usage**: Track which tools provide most value
4. **Security First**: Always use least privilege principle
5. **Document Everything**: Keep detailed logs of MCP operations
6. **Version Control**: Track MCP configurations in Git

## Performance Optimization

### Caching

Enable caching for frequently accessed data:

```yaml
features:
  enable_caching: true
  cache_ttl: 300  # 5 minutes
```

### Connection Pooling

Reuse MCP connections:

```python
class MCPConnectionPool:
    def __init__(self, max_connections=10):
        self.pool = {}
        self.max_connections = max_connections
    
    async def get_connection(self, server_name):
        if server_name not in self.pool:
            self.pool[server_name] = await self.connect(server_name)
        return self.pool[server_name]
```

## Roadmap

### Phase 1 (Current)
- ✅ GitHub MCP Server
- ✅ Filesystem MCP Server
- ✅ PostgreSQL MCP Server
- ✅ Docker MCP Server
- ✅ E2B Code Execution

### Phase 2 (Next Month)
- 🔄 Slack Integration
- 🔄 Linear/Jira Integration
- 🔄 Notion Documentation
- 🔄 MongoDB Support
- 🔄 Redis Caching

### Phase 3 (Q2 2025)
- 📋 AWS/Azure Integration
- 📋 Stripe Payments
- 📋 Sentry Monitoring
- 📋 Figma Design System
- 📋 Custom MCP Servers

## Contributing

To add a new MCP server:

1. Install the server package
2. Add configuration to `mcp_config.yaml`
3. Update agent permissions
4. Add Python interface methods
5. Test with relevant agents
6. Document usage

## Support

- **Documentation**: See `MCP_INTEGRATION_STRATEGY.md`
- **Issues**: Create GitHub issue with `mcp` label
- **Updates**: Check official MCP repository

---

*Last Updated: January 2025*
*Maintained by: CoralCollective Team*