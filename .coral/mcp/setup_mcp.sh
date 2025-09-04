#!/bin/bash

# CoralCollective MCP Setup Script
# This script installs and configures MCP servers for CoralCollective

set -e

echo "🪸 CoralCollective MCP Setup"
echo "============================"
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js (v18+) and try again."
    exit 1
fi

# Check for npm/npx
if ! command -v npx &> /dev/null; then
    echo "❌ npx is required but not installed."
    echo "Please install npm and try again."
    exit 1
fi

echo "✅ Prerequisites checked"
echo ""

# Create necessary directories
echo "Creating MCP directories..."
mkdir -p mcp/servers
mkdir -p mcp/configs
mkdir -p mcp/scripts
mkdir -p mcp/logs
echo "✅ Directories created"
echo ""

# Install MCP SDK
echo "Installing MCP SDK..."
npm install --save-dev @modelcontextprotocol/sdk
echo "✅ MCP SDK installed"
echo ""

# Install Core MCP Servers
echo "Installing Core MCP Servers..."
echo "This will install servers globally for use with Claude Desktop"
echo ""

# GitHub MCP Server
echo "1. Installing GitHub MCP Server..."
npm install -g @modelcontextprotocol/server-github
echo "   ✅ GitHub server installed"

# Filesystem MCP Server
echo "2. Installing Filesystem MCP Server..."
npm install -g @modelcontextprotocol/server-filesystem
echo "   ✅ Filesystem server installed"

# PostgreSQL MCP Server
echo "3. Installing PostgreSQL MCP Server..."
npm install -g @modelcontextprotocol/server-postgres
echo "   ✅ PostgreSQL server installed"

# Brave Search MCP Server
echo "4. Installing Brave Search MCP Server..."
npm install -g @modelcontextprotocol/server-brave-search
echo "   ✅ Brave Search server installed"

# Slack MCP Server
echo "5. Installing Slack MCP Server..."
npm install -g @modelcontextprotocol/server-slack
echo "   ✅ Slack server installed"

echo ""
echo "✅ Core MCP servers installed"
echo ""

# Check for .env file
if [ ! -f "mcp/.env" ]; then
    echo "📝 Creating .env file from template..."
    cp mcp/.env.example mcp/.env
    echo "   ⚠️  Please edit mcp/.env with your actual API keys and tokens"
else
    echo "✅ .env file already exists"
fi

# Create package.json if it doesn't exist
if [ ! -f "package.json" ]; then
    echo "Creating package.json..."
    npm init -y
    echo "✅ package.json created"
fi

# Add MCP scripts to package.json
echo "Adding MCP scripts to package.json..."
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
pkg.scripts = pkg.scripts || {};
pkg.scripts['mcp:github'] = 'npx @modelcontextprotocol/server-github';
pkg.scripts['mcp:filesystem'] = 'npx @modelcontextprotocol/server-filesystem .';
pkg.scripts['mcp:postgres'] = 'npx @modelcontextprotocol/server-postgres';
pkg.scripts['mcp:brave'] = 'npx @modelcontextprotocol/server-brave-search';
pkg.scripts['mcp:slack'] = 'npx @modelcontextprotocol/server-slack';
pkg.scripts['mcp:test'] = 'node mcp/scripts/test_servers.js';
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
"
echo "✅ MCP scripts added to package.json"
echo ""

# Create Claude Desktop configuration
echo "Setting up Claude Desktop configuration..."
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "Found Claude Desktop configuration directory"
    echo "To use MCP servers with Claude Desktop:"
    echo "1. Copy the configuration from mcp/claude_desktop_config.json"
    echo "2. Add it to your Claude Desktop settings at:"
    echo "   $CLAUDE_CONFIG_DIR/claude_desktop_config.json"
else
    echo "⚠️  Claude Desktop configuration directory not found"
    echo "   The configuration is saved in mcp/claude_desktop_config.json"
    echo "   You can manually add it to Claude Desktop when installed"
fi
echo ""

# Create test script
echo "Creating MCP test script..."
cat > mcp/scripts/test_servers.js << 'EOF'
#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

console.log('🧪 Testing MCP Servers...\n');

const servers = [
    {
        name: 'GitHub',
        command: 'npx',
        args: ['@modelcontextprotocol/server-github', '--help'],
        env: { GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_TOKEN }
    },
    {
        name: 'Filesystem',
        command: 'npx',
        args: ['@modelcontextprotocol/server-filesystem', '--help']
    },
    {
        name: 'PostgreSQL',
        command: 'npx',
        args: ['@modelcontextprotocol/server-postgres', '--help']
    }
];

servers.forEach(server => {
    console.log(`Testing ${server.name} server...`);
    try {
        const child = spawn(server.command, server.args, {
            env: { ...process.env, ...server.env },
            stdio: 'pipe'
        });
        
        child.on('error', (err) => {
            console.log(`   ❌ ${server.name} failed: ${err.message}`);
        });
        
        child.on('exit', (code) => {
            if (code === 0 || code === 1) {
                console.log(`   ✅ ${server.name} server is available`);
            }
        });
    } catch (err) {
        console.log(`   ❌ ${server.name} failed: ${err.message}`);
    }
});
EOF

chmod +x mcp/scripts/test_servers.js
echo "✅ Test script created"
echo ""

# Summary
echo "========================================="
echo "🎉 MCP Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit mcp/.env with your API keys and tokens"
echo "2. Configure Claude Desktop with mcp/claude_desktop_config.json"
echo "3. Test servers with: npm run mcp:test"
echo "4. Start using MCP servers with your CoralCollective agents!"
echo ""
echo "Available MCP servers:"
echo "  • GitHub - Repository management"
echo "  • Filesystem - Secure file operations"
echo "  • PostgreSQL - Database operations"
echo "  • Brave Search - Web research"
echo "  • Slack - Team communication"
echo ""
echo "For more servers, visit: https://github.com/modelcontextprotocol/servers"
echo ""