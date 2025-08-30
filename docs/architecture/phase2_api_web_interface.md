# Phase 2: API & Web Interface Implementation Plan

## Executive Summary

Phase 2 focuses on building a comprehensive REST API and web interface for the Jarvis Coding platform, transforming it from command-line scripts to a modern web-based security event generation system.

## 🎯 Phase 2 Objectives

1. **REST API Development** - Complete API for all generator/parser operations
2. **Web Dashboard** - Interactive interface for managing and executing generators
3. **Real-time Monitoring** - Live event generation and parsing feedback
4. **Authentication System** - Secure access control
5. **API Documentation** - OpenAPI/Swagger specification

## 🏗️ Technical Architecture

### API Architecture
```
┌─────────────────────────────────────────────────────────┐
│                   Web Dashboard (React)                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  REST API (FastAPI)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │Generator │  │ Parser   │  │Scenario  │  │Monitor │ │
│  │Service   │  │Service   │  │Service   │  │Service │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Generators  │ │   Parsers    │ │  Scenarios   │
│   (100+)     │ │   (100+)     │ │    (10+)     │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 📡 REST API Specification

### Core API Endpoints

#### 1. Generator Management
```python
# Generator endpoints
GET    /api/v1/generators                    # List all generators
GET    /api/v1/generators/{id}              # Get generator details
POST   /api/v1/generators/{id}/execute      # Execute generator
POST   /api/v1/generators/{id}/validate     # Validate generator output
GET    /api/v1/generators/{id}/schema       # Get output schema
GET    /api/v1/generators/categories        # List categories

# Batch operations
POST   /api/v1/generators/batch/execute     # Execute multiple generators
POST   /api/v1/generators/batch/validate    # Validate multiple generators
```

#### 2. Parser Management
```python
# Parser endpoints
GET    /api/v1/parsers                      # List all parsers
GET    /api/v1/parsers/{id}                # Get parser details
POST   /api/v1/parsers/{id}/test           # Test parser with sample
GET    /api/v1/parsers/{id}/fields         # Get expected fields
GET    /api/v1/parsers/{id}/compatibility  # Check generator compatibility
POST   /api/v1/parsers/{id}/validate       # Validate parser configuration

# Marketplace parsers
GET    /api/v1/parsers/marketplace         # List marketplace parsers
GET    /api/v1/parsers/marketplace/{id}    # Get marketplace parser
```

#### 3. Scenario Execution
```python
# Scenario endpoints
GET    /api/v1/scenarios                    # List scenarios
GET    /api/v1/scenarios/{id}              # Get scenario details
POST   /api/v1/scenarios/{id}/execute      # Execute scenario
GET    /api/v1/scenarios/{id}/status       # Get execution status
POST   /api/v1/scenarios/{id}/stop         # Stop running scenario
GET    /api/v1/scenarios/{id}/results      # Get scenario results
```

#### 4. Field Validation (Phase 3 Preview)
```python
# Field validation endpoints
POST   /api/v1/validation/check            # Check generator-parser compatibility
GET    /api/v1/validation/report/{gen}/{parser}  # Get validation report
POST   /api/v1/validation/fix/{gen}        # Auto-fix field mismatches
GET    /api/v1/validation/coverage         # Get overall field coverage
```

#### 5. Monitoring & Health
```python
# System monitoring
GET    /api/v1/health                      # Health check
GET    /api/v1/metrics                     # System metrics
GET    /api/v1/stats                       # Usage statistics
WS     /api/v1/events                      # WebSocket for real-time events
```

### API Request/Response Models

```python
# Generator execution request
class GeneratorExecuteRequest(BaseModel):
    count: int = 1
    format: str = "json"  # json, syslog, csv, keyvalue
    options: Dict[str, Any] = {}
    star_trek_theme: bool = True
    
# Generator execution response
class GeneratorExecuteResponse(BaseModel):
    generator_id: str
    events: List[Dict[str, Any]]
    format: str
    execution_time: float
    success: bool
    errors: List[str] = []
    
# Validation result
class ValidationResult(BaseModel):
    generator_id: str
    parser_id: str
    compatibility_score: float  # 0-100%
    matched_fields: List[str]
    missing_fields: List[str]
    extra_fields: List[str]
    recommendations: List[str]
```

## 🖥️ Web Interface Design

### Dashboard Components

#### 1. Main Dashboard
```typescript
// Core dashboard views
- Generator Catalog: Browse and search 100+ generators
- Quick Execute: One-click event generation
- Recent Activity: Live feed of generated events
- System Health: Real-time metrics and status
```

#### 2. Generator Explorer
```typescript
interface GeneratorExplorer {
  // Features
  - Category filtering (cloud, network, endpoint, etc.)
  - Search by vendor/product
  - Favorite generators
  - Quick actions (execute, validate, view schema)
  - Star Trek theme toggle
  - Output format selector
}
```

#### 3. Execution Interface
```typescript
interface ExecutionPanel {
  // Controls
  - Event count slider (1-1000)
  - Format selector (JSON/Syslog/CSV/KeyValue)
  - Advanced options accordion
  - Real-time output viewer
  - Download results button
  - Send to parser button
}
```

#### 4. Validation Dashboard (Phase 3)
```typescript
interface ValidationDashboard {
  // Field validation matrix
  - Generator vs Parser compatibility grid
  - Field coverage heatmap
  - Mismatch highlighting
  - Auto-fix suggestions
  - Validation history
}
```

### UI/UX Mockup Structure
```
┌─────────────────────────────────────────────────────────────┐
│  🔒 Jarvis Coding  │ Generators │ Parsers │ Scenarios │ ⚙️  │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌─────────────────────────────────────┐   │
│ │              │ │       Generator Catalog               │   │
│ │  Categories  │ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │   │
│ │              │ │ │AWS  │ │Cisco│ │Fort │ │Crowd│   │   │
│ │ ☁️ Cloud     │ │ │Cloud│ │FTD  │ │inet │ │Strike│  │   │
│ │ 🔒 Security  │ │ └─────┘ └─────┘ └─────┘ └─────┘   │   │
│ │ 🖥️ Endpoint  │ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │   │
│ │ 👤 Identity  │ │ │Okta │ │Azure│ │Senti│ │Palo │   │   │
│ │              │ │ │Auth │ │AD   │ │nelOne│ │Alto │   │   │
│ └──────────────┘ └─────────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────────────┐   │
│ │             Execution Panel                          │   │
│ │  Generator: CrowdStrike Falcon                       │   │
│ │  Count: [====|====] 50   Format: [JSON ▼]          │   │
│ │  [🚀 Execute] [✓ Validate] [📊 View Fields]        │   │
│ └─────────────────────────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────────────┐   │
│ │             Real-time Output                         │   │
│ │  {"timestamp": "2025-01-29T00:45:32Z",              │   │
│ │   "user": "jean.picard@starfleet.corp", ...}        │   │
│ └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Implementation Details

### Backend Stack (FastAPI)

```python
# main.py - FastAPI application
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Jarvis Coding API",
    description="Security Event Generation Platform",
    version="2.0.0"
)

# Enable CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generator service
@app.get("/api/v1/generators")
async def list_generators(category: str = None):
    """List all available generators"""
    generators = load_generators()
    if category:
        generators = filter_by_category(generators, category)
    return generators

@app.post("/api/v1/generators/{generator_id}/execute")
async def execute_generator(
    generator_id: str,
    request: GeneratorExecuteRequest
):
    """Execute a specific generator"""
    try:
        generator = get_generator(generator_id)
        events = generator.execute(
            count=request.count,
            format=request.format,
            **request.options
        )
        return GeneratorExecuteResponse(
            generator_id=generator_id,
            events=events,
            format=request.format,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend Stack (React + TypeScript)

```typescript
// GeneratorDashboard.tsx
import React, { useState, useEffect } from 'react';
import { Grid, Card, Button, Select } from '@mui/material';

interface Generator {
  id: string;
  name: string;
  category: string;
  vendor: string;
  description: string;
}

const GeneratorDashboard: React.FC = () => {
  const [generators, setGenerators] = useState<Generator[]>([]);
  const [selectedGenerator, setSelectedGenerator] = useState<string>('');
  const [eventCount, setEventCount] = useState<number>(10);
  const [format, setFormat] = useState<string>('json');
  
  const executeGenerator = async () => {
    const response = await fetch(
      `/api/v1/generators/${selectedGenerator}/execute`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          count: eventCount,
          format: format,
          star_trek_theme: true
        })
      }
    );
    const data = await response.json();
    displayResults(data.events);
  };
  
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <GeneratorCatalog 
          generators={generators}
          onSelect={setSelectedGenerator}
        />
      </Grid>
      <Grid item xs={12}>
        <ExecutionPanel
          onExecute={executeGenerator}
          count={eventCount}
          format={format}
        />
      </Grid>
      <Grid item xs={12}>
        <OutputViewer />
      </Grid>
    </Grid>
  );
};
```

## 📅 Implementation Timeline

### Week 1-2: API Foundation
- [ ] Set up FastAPI project structure
- [ ] Implement generator endpoints
- [ ] Create parser endpoints
- [ ] Add authentication middleware
- [ ] Set up database for metadata

### Week 3-4: Web Interface
- [ ] Create React application
- [ ] Build generator catalog component
- [ ] Implement execution panel
- [ ] Add real-time output viewer
- [ ] Create authentication UI

### Week 5-6: Integration & Testing
- [ ] Connect frontend to API
- [ ] Implement WebSocket for real-time events
- [ ] Add error handling
- [ ] Create API tests
- [ ] Performance optimization

### Week 7-8: Polish & Deploy
- [ ] Add monitoring dashboard
- [ ] Implement caching
- [ ] Create Docker containers
- [ ] Write deployment documentation
- [ ] Launch beta version

## 🚀 Quick Start Implementation

### Step 1: Install Dependencies
```bash
# Backend
pip install fastapi uvicorn sqlalchemy redis python-jose[cryptography]

# Frontend
npx create-react-app jarvis-web --template typescript
cd jarvis-web
npm install @mui/material axios react-query socket.io-client
```

### Step 2: Basic API Server
```python
# Save as api_server.py
from fastapi import FastAPI
import sys
sys.path.append('event_generators')

app = FastAPI()

@app.get("/api/v1/generators")
def list_generators():
    # Import and list all generators
    return {"generators": [...]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Run Development Servers
```bash
# Terminal 1: API
python api_server.py

# Terminal 2: Web UI
cd jarvis-web && npm start
```

## 🎯 Success Metrics

### API Metrics
- Response time < 200ms for generator list
- Execution time < 5s for 100 events
- 99.9% API availability
- Support 100+ concurrent users

### UI Metrics
- Page load time < 2 seconds
- Time to first event < 3 seconds
- Mobile responsive design
- Accessibility score > 90

## 🔒 Security Considerations

1. **Authentication**: JWT-based auth with refresh tokens
2. **Rate Limiting**: 100 requests/minute per user
3. **Input Validation**: Strict schema validation
4. **CORS Policy**: Whitelist allowed origins
5. **API Keys**: Secure storage in environment variables

## 📝 Documentation Requirements

1. **API Documentation**: OpenAPI/Swagger spec
2. **User Guide**: How to use web interface
3. **Developer Guide**: How to extend API
4. **Deployment Guide**: Production setup
5. **Security Guide**: Best practices

## Next Phase Preview: Generator-Parser Field Validation

Phase 3 will build on this API to add comprehensive field validation:
- Field compatibility checking endpoint
- Automated field mapping verification
- Visual field coverage reports
- Auto-fix capabilities for mismatches
- Continuous validation monitoring

This Phase 2 implementation provides the foundation for all future enhancements while immediately delivering value through the web interface and API.