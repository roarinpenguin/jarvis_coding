# API Fix Implementation Guide

**Document Version:** 1.0  
**Created:** August 30, 2025  
**Last Updated:** August 30, 2025  
**QA Test Results:** 75% pass rate (27/36 tests)  

## Executive Summary

This implementation guide provides step-by-step instructions to fix critical API issues identified during comprehensive QA testing. The API currently has a 75% pass rate with excellent security and performance, but requires fixes in input validation, batch execution, and missing endpoints.

## Issue Priority Classification

### 🔴 CRITICAL ISSUES (Must Fix First)
1. **Input Validation Gaps** - Missing field validation not working
2. **Batch Execution Endpoint** - Returns 422 validation error  
3. **End-to-End Integration** - Workflow test fails at generator details step

### 🟡 HIGH PRIORITY ISSUES
4. **Missing API Endpoints** - Export, Search, Base Metrics endpoints
5. **Scenario Execution** - Execute endpoint returns 405 Method Not Allowed

### 🟢 MEDIUM PRIORITY ISSUES
6. **API Documentation** - Some endpoints return 404 when expected to exist

---

## Phase 1: Critical Issues (Estimated: 1-2 Days)

### Issue #1: Fix Input Validation Gaps

**Problem:** API accepts requests with missing required fields and invalid field values  
**Impact:** Malformed requests could cause downstream issues  
**Test Results:** 
- "Missing Required Fields" test failed (Status 200 instead of 422)
- "Invalid Field Values" test failed (Status 200 instead of 422)

#### Step 1.1: Update Pydantic Models

**File to edit:** `/api/app/models/responses.py`

```python
# Add strict validation to GeneratorExecuteRequest
class GeneratorExecuteRequest(BaseModel):
    # Make validation stricter
    count: int = Field(..., ge=1, le=1000, description="Number of events to generate")
    format: str = Field(..., regex="^(json|csv|syslog|key_value)$", description="Output format")
    star_trek_theme: bool = Field(default=True, description="Use Star Trek themed data")
    options: Dict[str, Any] = Field(default_factory=dict, description="Generator-specific options")
    
    class Config:
        # Enable strict validation
        validate_assignment = True
        extra = "forbid"  # Reject extra fields
```

**File to create:** `/api/app/models/requests.py`

```python
"""
Request models with strict validation
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
import re

class BatchExecuteRequest(BaseModel):
    """Batch execution request with proper validation"""
    executions: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50)
    
    @validator('executions')
    def validate_executions(cls, v):
        for i, execution in enumerate(v):
            if 'generator_id' not in execution:
                raise ValueError(f"Execution {i}: missing required field 'generator_id'")
            if 'count' in execution and (execution['count'] < 1 or execution['count'] > 1000):
                raise ValueError(f"Execution {i}: count must be between 1 and 1000")
            if 'format' in execution and execution['format'] not in ['json', 'csv', 'syslog', 'key_value']:
                raise ValueError(f"Execution {i}: invalid format '{execution['format']}'")
        return v
    
    class Config:
        extra = "forbid"
        validate_assignment = True

class ScenarioExecuteRequest(BaseModel):
    """Scenario execution request"""
    speed: str = Field("fast", regex="^(realtime|fast|instant)$")
    dry_run: bool = Field(False)
    
    class Config:
        extra = "forbid"

class CustomScenarioRequest(BaseModel):
    """Custom scenario creation request"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    phases: List[Dict[str, Any]] = Field(..., min_items=1)
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\- ]+$', v):
            raise ValueError('Name can only contain letters, numbers, spaces, hyphens, and underscores')
        return v
    
    class Config:
        extra = "forbid"
```

#### Step 1.2: Update Generator Router

**File to edit:** `/api/app/routers/generators.py`

```python
# Add at top of file
from pydantic import ValidationError
from app.models.requests import BatchExecuteRequest

# Update batch execute endpoint
@router.post("/batch/execute", response_model=BaseResponse)
async def batch_execute_generators(
    request: BatchExecuteRequest,  # Use proper model instead of List[dict]
    _: str = Depends(require_write_access)
):
    """Execute multiple generators in batch"""
    try:
        results = []
        total_events = 0
        total_time = 0
        
        for execution in request.executions:
            generator_id = execution.get("generator_id")
            count = execution.get("count", 1)
            format = execution.get("format", "json")
            
            try:
                start_time = time.time()
                events = await generator_service.execute_generator(
                    generator_id,
                    count=count,
                    format=format
                )
                execution_time = (time.time() - start_time) * 1000
                
                results.append({
                    "generator_id": generator_id,
                    "success": True,
                    "events_count": len(events),
                    "execution_time_ms": execution_time
                })
                total_events += len(events)
                total_time += execution_time
                
            except Exception as e:
                results.append({
                    "generator_id": generator_id,
                    "success": False,
                    "error": str(e)
                })
        
        return BaseResponse(
            success=True,
            data={
                "batch_id": f"batch_{int(time.time())}",
                "executions": results,
                "total_events": total_events,
                "total_execution_time_ms": total_time,
                "parallel_execution": False  # Currently sequential
            }
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": e.errors()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch execution failed: {str(e)}"
        )
```

#### Step 1.3: Add Global Exception Handler

**File to edit:** `/api/app/main.py`

```python
# Add after other imports
from pydantic import ValidationError

# Add exception handler for validation errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(422)
async def unprocessable_entity_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "UNPROCESSABLE_ENTITY",
                "message": "The request was well-formed but contains semantic errors"
            }
        }
    )
```

#### Step 1.4: Test Validation Fixes

```bash
# Test missing required fields
curl -X POST http://localhost:8000/api/v1/generators/crowdstrike_falcon/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{}'
# Expected: 422 Unprocessable Entity

# Test invalid field values  
curl -X POST http://localhost:8000/api/v1/generators/crowdstrike_falcon/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{"count": -1, "format": "invalid_format"}'
# Expected: 422 Unprocessable Entity

# Test valid request
curl -X POST http://localhost:8000/api/v1/generators/crowdstrike_falcon/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{"count": 5, "format": "json"}'
# Expected: 200 OK with events
```

### Issue #2: Fix Batch Execution Endpoint

**Problem:** Batch execute endpoint returns 422 validation error  
**Impact:** Multi-generator workflows broken

#### Step 2.1: Debug Current Batch Execution Issue

```bash
# Test current batch endpoint to see exact error
curl -X POST http://localhost:8000/api/v1/generators/batch/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '[{"generator_id": "crowdstrike_falcon", "count": 3}]' \
  -v
```

#### Step 2.2: Implementation (Already covered in Step 1.2)

The batch execution fix is included in the validation improvements above using the `BatchExecuteRequest` model.

#### Step 2.3: Test Batch Execution Fix

```bash
# Test with proper request model
curl -X POST http://localhost:8000/api/v1/generators/batch/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{"executions": [{"generator_id": "crowdstrike_falcon", "count": 3}, {"generator_id": "aws_cloudtrail", "count": 2}]}'
# Expected: 200 OK with batch results
```

### Issue #3: Fix End-to-End Integration Workflow

**Problem:** End-to-End workflow test fails at generator details step  
**Impact:** Data inconsistency between API endpoints

#### Step 3.1: Debug Integration Issue

**File to create:** `/api/debug_integration.py`

```python
#!/usr/bin/env python3
"""
Debug script to identify integration issues
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"X-API-Key": "your-read-key"}

def debug_integration():
    print("🔍 Debugging End-to-End Integration")
    
    # Step 1: List generators
    print("\n1. Listing generators...")
    response = requests.get(f"{BASE_URL}/generators", headers=HEADERS)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to list generators: {response.text}")
        return
    
    data = response.json()
    generators = data.get("data", {}).get("generators", [])
    print(f"   ✅ Found {len(generators)} generators")
    
    if not generators:
        print("   ❌ No generators found")
        return
    
    # Step 2: Get first generator details
    first_generator = generators[0]["id"]
    print(f"\n2. Getting details for generator: {first_generator}")
    
    response = requests.get(f"{BASE_URL}/generators/{first_generator}", headers=HEADERS)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to get generator details: {response.text}")
        print(f"   Debug: URL = {BASE_URL}/generators/{first_generator}")
        return
    
    details = response.json()
    print(f"   ✅ Got details for {first_generator}")
    
    # Step 3: Execute generator
    print(f"\n3. Executing generator: {first_generator}")
    
    execute_data = {"count": 1, "format": "json"}
    response = requests.post(
        f"{BASE_URL}/generators/{first_generator}/execute",
        headers={**HEADERS, "X-API-Key": "your-write-key"},
        json=execute_data
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to execute generator: {response.text}")
        return
    
    print("   ✅ End-to-End workflow successful!")

if __name__ == "__main__":
    debug_integration()
```

#### Step 3.2: Run Debug Script

```bash
cd /api
python debug_integration.py
```

#### Step 3.3: Fix Data Consistency Issues

Based on debug results, the most likely issue is in the generator service returning inconsistent data formats.

**File to check:** `/api/app/services/generator_service.py`

Ensure consistent data structure across all generator service methods:

```python
# Standardize generator info format
async def get_generator(self, generator_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific generator"""
    try:
        # Ensure consistent format with list_generators
        generators = await self.list_generators()
        for generator in generators:
            if generator["id"] == generator_id:
                # Add additional details for single generator view
                generator["detailed"] = True
                generator["last_accessed"] = datetime.utcnow().isoformat()
                return generator
        return None
    except Exception as e:
        logger.error(f"Error getting generator {generator_id}: {e}")
        return None
```

---

## Phase 2: Missing Endpoints (Estimated: 3-4 Days)

### Issue #4: Implement Missing API Endpoints

**Problem:** Export, Search, and Base Metrics endpoints missing  
**Impact:** Reduced API functionality

#### Step 4.1: Fix Export Endpoint

**File to edit:** `/api/app/routers/export.py`

```python
"""
Export functionality endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Response
from typing import Optional, List
import json
import csv
import io
from datetime import datetime

from app.models.responses import BaseResponse
from app.core.simple_auth import require_read_access
from app.services.generator_service import GeneratorService

router = APIRouter()
generator_service = GeneratorService()

@router.get("/generators", response_model=BaseResponse)
async def export_generators_list(
    format: str = Query("json", regex="^(json|csv|yaml)$"),
    category: Optional[str] = Query(None),
    _: str = Depends(require_read_access)
):
    """Export generators list in various formats"""
    try:
        generators = await generator_service.list_generators(category=category)
        
        if format == "csv":
            output = io.StringIO()
            if generators:
                fieldnames = generators[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(generators)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=generators.csv"}
            )
        
        elif format == "yaml":
            import yaml
            yaml_content = yaml.dump({"generators": generators}, default_flow_style=False)
            return Response(
                content=yaml_content,
                media_type="text/yaml",
                headers={"Content-Disposition": "attachment; filename=generators.yaml"}
            )
        
        else:  # json
            return BaseResponse(
                success=True,
                data={"generators": generators, "exported_at": datetime.utcnow().isoformat()}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events")
async def export_generated_events(
    generator_ids: List[str],
    count_per_generator: int = Query(5, ge=1, le=100),
    format: str = Query("json", regex="^(json|csv)$"),
    _: str = Depends(require_read_access)
):
    """Export events from multiple generators"""
    try:
        all_events = []
        
        for generator_id in generator_ids:
            events = await generator_service.execute_generator(
                generator_id, count=count_per_generator, format="json"
            )
            
            # Add metadata to each event
            for event in events:
                event["_generator"] = generator_id
                event["_exported_at"] = datetime.utcnow().isoformat()
            
            all_events.extend(events)
        
        if format == "csv":
            if not all_events:
                return Response(content="", media_type="text/csv")
            
            output = io.StringIO()
            # Flatten nested objects for CSV
            flattened_events = []
            for event in all_events:
                flat_event = {}
                for key, value in event.items():
                    if isinstance(value, (dict, list)):
                        flat_event[key] = json.dumps(value)
                    else:
                        flat_event[key] = value
                flattened_events.append(flat_event)
            
            fieldnames = flattened_events[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_events)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=events.csv"}
            )
        
        else:  # json
            return BaseResponse(
                success=True,
                data={
                    "events": all_events,
                    "total_events": len(all_events),
                    "generators": generator_ids,
                    "exported_at": datetime.utcnow().isoformat()
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 4.2: Fix Search Endpoints

**File to edit:** `/api/app/routers/search.py`

```python
"""
Search functionality across generators, parsers, and scenarios
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
import re

from app.models.responses import BaseResponse
from app.core.simple_auth import require_read_access
from app.services.generator_service import GeneratorService
from app.services.search_service import SearchService

router = APIRouter()
generator_service = GeneratorService()
search_service = SearchService()

@router.get("/generators", response_model=BaseResponse)
async def search_generators(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: str = Depends(require_read_access)
):
    """Search generators by name, description, or metadata"""
    try:
        results = await search_service.search_generators(
            query=q,
            category=category,
            vendor=vendor
        )
        
        # Apply pagination
        total = len(results)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = results[start:end]
        
        return BaseResponse(
            success=True,
            data={
                "results": paginated_results,
                "total": total,
                "query": q
            },
            metadata={
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page
                },
                "search": {
                    "query": q,
                    "category": category,
                    "vendor": vendor
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parsers", response_model=BaseResponse)
async def search_parsers(
    q: str = Query(..., min_length=2, description="Search query"),
    type: Optional[str] = Query(None, regex="^(community|marketplace)$"),
    _: str = Depends(require_read_access)
):
    """Search parsers by name or description"""
    try:
        results = await search_service.search_parsers(query=q, parser_type=type)
        
        return BaseResponse(
            success=True,
            data={
                "results": results,
                "total": len(results),
                "query": q
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all", response_model=BaseResponse)
async def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    types: List[str] = Query(["generators", "parsers", "scenarios"]),
    _: str = Depends(require_read_access)
):
    """Search across all resource types"""
    try:
        results = {}
        
        if "generators" in types:
            results["generators"] = await search_service.search_generators(q)
        
        if "parsers" in types:
            results["parsers"] = await search_service.search_parsers(q)
        
        if "scenarios" in types:
            results["scenarios"] = await search_service.search_scenarios(q)
        
        total_results = sum(len(items) for items in results.values())
        
        return BaseResponse(
            success=True,
            data={
                "results": results,
                "total": total_results,
                "query": q,
                "types_searched": types
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 4.3: Create Search Service

**File to create:** `/api/app/services/search_service.py`

```python
"""
Search service for finding generators, parsers, and scenarios
"""
import re
from typing import List, Dict, Any, Optional
import logging

from app.services.generator_service import GeneratorService

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.generator_service = GeneratorService()
    
    async def search_generators(
        self, 
        query: str, 
        category: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search generators using text matching"""
        try:
            generators = await self.generator_service.list_generators(
                category=category,
                vendor=vendor
            )
            
            # Simple text search across multiple fields
            query_lower = query.lower()
            results = []
            
            for generator in generators:
                # Search in multiple fields
                searchable_text = " ".join([
                    generator.get("name", ""),
                    generator.get("description", ""),
                    generator.get("vendor", ""),
                    generator.get("category", ""),
                    " ".join(generator.get("supported_formats", []))
                ]).lower()
                
                # Calculate relevance score
                score = 0
                if query_lower in generator.get("name", "").lower():
                    score += 10
                if query_lower in generator.get("vendor", "").lower():
                    score += 5
                if query_lower in generator.get("category", "").lower():
                    score += 3
                if query_lower in generator.get("description", "").lower():
                    score += 1
                
                if score > 0 or query_lower in searchable_text:
                    generator["search_score"] = score
                    results.append(generator)
            
            # Sort by relevance score (highest first)
            results.sort(key=lambda x: x.get("search_score", 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching generators: {e}")
            return []
    
    async def search_parsers(
        self, 
        query: str, 
        parser_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search parsers (placeholder - implement based on parser service)"""
        # This would integrate with a parser service when available
        results = []
        
        # Mock parser search for now
        mock_parsers = [
            {
                "id": "crowdstrike_endpoint",
                "name": "CrowdStrike Endpoint",
                "type": "community",
                "vendor": "CrowdStrike",
                "description": "CrowdStrike Falcon endpoint events"
            },
            {
                "id": "aws_cloudtrail",
                "name": "AWS CloudTrail",
                "type": "marketplace",
                "vendor": "AWS",
                "description": "AWS CloudTrail API audit events"
            }
        ]
        
        query_lower = query.lower()
        for parser in mock_parsers:
            if parser_type and parser["type"] != parser_type:
                continue
                
            searchable = f"{parser['name']} {parser['vendor']} {parser['description']}".lower()
            if query_lower in searchable:
                results.append(parser)
        
        return results
    
    async def search_scenarios(self, query: str) -> List[Dict[str, Any]]:
        """Search scenarios (placeholder)"""
        # Mock scenario search
        mock_scenarios = [
            {
                "id": "phishing_campaign",
                "name": "Phishing Campaign",
                "description": "Multi-stage phishing attack"
            },
            {
                "id": "ransomware_attack", 
                "name": "Ransomware Attack",
                "description": "Ransomware deployment and lateral movement"
            }
        ]
        
        query_lower = query.lower()
        results = []
        for scenario in mock_scenarios:
            searchable = f"{scenario['name']} {scenario['description']}".lower()
            if query_lower in searchable:
                results.append(scenario)
        
        return results
```

#### Step 4.4: Fix Base Metrics Endpoint

**File to edit:** `/api/app/routers/metrics.py`

```python
# Add base metrics endpoint
@router.get("", response_model=BaseResponse)
async def get_base_metrics(_: str = Depends(require_read_access)):
    """Get base API metrics"""
    try:
        metrics = await metrics_service.get_base_metrics()
        
        return BaseResponse(
            success=True,
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Issue #5: Fix Scenario Execution Method Not Allowed

**Problem:** Scenario execute endpoint returns 405 Method Not Allowed  
**Impact:** Attack scenario generation not working

#### Step 5.1: Debug Scenario Router

The scenario router looks correct with POST method defined. The issue might be in the service implementation or HTTP method mismatch.

**File to check:** `/api/app/services/scenario_service.py`

Create the service if it doesn't exist:

```python
"""
Scenario service for managing attack scenarios
"""
from typing import Dict, Any, List, Optional
import uuid
import time
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ScenarioService:
    def __init__(self):
        self.running_scenarios = {}
        self.scenario_templates = {
            "phishing_campaign": {
                "id": "phishing_campaign",
                "name": "Phishing Campaign",
                "description": "Multi-stage phishing attack with credential harvesting",
                "phases": [
                    {"name": "Initial Email", "generators": ["mimecast"], "duration": 5},
                    {"name": "Credential Harvest", "generators": ["okta_authentication"], "duration": 10},
                    {"name": "Lateral Movement", "generators": ["crowdstrike_falcon"], "duration": 15}
                ]
            }
        }
    
    async def list_scenarios(
        self, 
        category: Optional[str] = None, 
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available scenarios"""
        scenarios = list(self.scenario_templates.values())
        
        if search:
            search_lower = search.lower()
            scenarios = [
                s for s in scenarios 
                if search_lower in s["name"].lower() or search_lower in s["description"].lower()
            ]
        
        return scenarios
    
    async def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed scenario information"""
        return self.scenario_templates.get(scenario_id)
    
    async def start_scenario(
        self, 
        scenario_id: str, 
        speed: str = "fast", 
        dry_run: bool = False,
        background_tasks=None
    ) -> str:
        """Start scenario execution"""
        scenario = await self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_id}' not found")
        
        execution_id = str(uuid.uuid4())
        
        self.running_scenarios[execution_id] = {
            "scenario_id": scenario_id,
            "execution_id": execution_id,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "speed": speed,
            "dry_run": dry_run,
            "progress": 0
        }
        
        if background_tasks:
            background_tasks.add_task(self._execute_scenario, execution_id, scenario)
        
        return execution_id
    
    async def _execute_scenario(self, execution_id: str, scenario: Dict[str, Any]):
        """Execute scenario in background"""
        try:
            # Simulate scenario execution
            for i, phase in enumerate(scenario.get("phases", [])):
                await asyncio.sleep(1)  # Simulate work
                
                progress = ((i + 1) / len(scenario["phases"])) * 100
                self.running_scenarios[execution_id]["progress"] = progress
            
            self.running_scenarios[execution_id]["status"] = "completed"
            self.running_scenarios[execution_id]["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Scenario execution failed: {e}")
            self.running_scenarios[execution_id]["status"] = "failed"
            self.running_scenarios[execution_id]["error"] = str(e)
    
    async def get_execution_status(
        self, 
        scenario_id: str, 
        execution_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        if execution_id:
            return self.running_scenarios.get(execution_id)
        
        # Return latest execution for scenario
        for exec_id, execution in self.running_scenarios.items():
            if execution["scenario_id"] == scenario_id:
                return execution
        
        return None
    
    async def stop_execution(self, scenario_id: str, execution_id: str) -> bool:
        """Stop scenario execution"""
        if execution_id in self.running_scenarios:
            self.running_scenarios[execution_id]["status"] = "stopped"
            self.running_scenarios[execution_id]["stopped_at"] = datetime.utcnow().isoformat()
            return True
        return False
    
    async def get_execution_results(
        self, 
        scenario_id: str, 
        execution_id: str,
        include_events: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get execution results"""
        execution = self.running_scenarios.get(execution_id)
        if not execution:
            return None
        
        results = {
            "execution_id": execution_id,
            "scenario_id": scenario_id,
            "status": execution["status"],
            "events_generated": 0,  # Placeholder
            "total_time_ms": 0      # Placeholder
        }
        
        if include_events:
            results["events"] = []  # Placeholder
        
        return results
    
    async def get_execution_timeline(
        self, 
        scenario_id: str, 
        execution_id: str
    ) -> List[Dict[str, Any]]:
        """Get execution timeline"""
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "phase": "Initial Email",
                "status": "completed",
                "events_count": 3
            }
        ]
    
    async def create_custom_scenario(self, config: Dict[str, Any]) -> str:
        """Create custom scenario"""
        scenario_id = f"custom_{int(time.time())}"
        
        self.scenario_templates[scenario_id] = {
            "id": scenario_id,
            "name": config["name"],
            "description": config["description"],
            "phases": config["phases"],
            "custom": True
        }
        
        return scenario_id
```

#### Step 5.2: Test Scenario Execution

```bash
# Test scenario execution
curl -X POST http://localhost:8000/api/v1/scenarios/phishing_campaign/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{"speed": "fast", "dry_run": false}'
# Expected: 200 OK with execution details
```

---

## Phase 3: Production Hardening (Estimated: 2-3 Days)

### Step 6: Enhanced Error Handling

**File to edit:** `/api/app/main.py`

```python
# Enhanced error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": str(uuid.uuid4())  # For tracking
            }
        }
    )
```

### Step 7: API Documentation Updates

**File to create:** `/api/API_ENDPOINTS_REFERENCE.md`

```markdown
# API Endpoints Reference

## Authentication
All endpoints except `/health` require authentication via `X-API-Key` header or `api_key` query parameter.

## Response Format
```json
{
  "success": true,
  "data": {},
  "metadata": {}
}
```

## Error Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Endpoints

### Generators
- `GET /api/v1/generators` - List all generators
- `GET /api/v1/generators/{id}` - Get generator details
- `POST /api/v1/generators/{id}/execute` - Execute generator
- `POST /api/v1/generators/batch/execute` - Batch execute generators

### Scenarios  
- `GET /api/v1/scenarios` - List scenarios
- `POST /api/v1/scenarios/{id}/execute` - Execute scenario

### Export
- `GET /api/v1/export/generators` - Export generators list
- `POST /api/v1/export/events` - Export generated events

### Search
- `GET /api/v1/search/generators` - Search generators
- `GET /api/v1/search/all` - Search all resources

### Metrics
- `GET /api/v1/metrics` - Get base metrics
```

---

## Testing After Fixes

### Automated Testing

**File to create:** `/api/test_fixes.py`

```python
#!/usr/bin/env python3
"""
Test script to verify all fixes are working
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
HEADERS_READ = {"X-API-Key": "your-read-key"}
HEADERS_WRITE = {"X-API-Key": "your-write-key"}

def test_validation_fixes():
    """Test input validation fixes"""
    print("🔍 Testing Input Validation Fixes...")
    
    # Test 1: Missing required fields
    response = requests.post(
        f"{BASE_URL}/generators/crowdstrike_falcon/execute",
        headers={**HEADERS_WRITE, "Content-Type": "application/json"},
        json={}
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("   ✅ Missing required fields properly rejected")
    
    # Test 2: Invalid field values
    response = requests.post(
        f"{BASE_URL}/generators/crowdstrike_falcon/execute", 
        headers={**HEADERS_WRITE, "Content-Type": "application/json"},
        json={"count": -1, "format": "invalid_format"}
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("   ✅ Invalid field values properly rejected")

def test_batch_execution():
    """Test batch execution fixes"""
    print("🔍 Testing Batch Execution Fixes...")
    
    response = requests.post(
        f"{BASE_URL}/generators/batch/execute",
        headers={**HEADERS_WRITE, "Content-Type": "application/json"},
        json={
            "executions": [
                {"generator_id": "crowdstrike_falcon", "count": 2},
                {"generator_id": "aws_cloudtrail", "count": 1}
            ]
        }
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✅ Batch execution working")

def test_missing_endpoints():
    """Test missing endpoint implementations"""
    print("🔍 Testing Missing Endpoint Fixes...")
    
    # Test export endpoint
    response = requests.get(f"{BASE_URL}/export/generators", headers=HEADERS_READ)
    assert response.status_code == 200, f"Export endpoint failed: {response.status_code}"
    print("   ✅ Export endpoint working")
    
    # Test search endpoint
    response = requests.get(f"{BASE_URL}/search/generators?q=aws", headers=HEADERS_READ)
    assert response.status_code == 200, f"Search endpoint failed: {response.status_code}"
    print("   ✅ Search endpoint working")
    
    # Test base metrics endpoint
    response = requests.get(f"{BASE_URL}/metrics", headers=HEADERS_READ)
    assert response.status_code == 200, f"Metrics endpoint failed: {response.status_code}"
    print("   ✅ Base metrics endpoint working")

def test_scenario_execution():
    """Test scenario execution fix"""
    print("🔍 Testing Scenario Execution Fix...")
    
    response = requests.post(
        f"{BASE_URL}/scenarios/phishing_campaign/execute",
        headers={**HEADERS_WRITE, "Content-Type": "application/json"},
        json={"speed": "fast", "dry_run": true}
    )
    assert response.status_code == 200, f"Scenario execution failed: {response.status_code}"
    print("   ✅ Scenario execution working")

def main():
    print("🚀 Running API Fix Tests\n")
    
    try:
        test_validation_fixes()
        test_batch_execution()
        test_missing_endpoints()
        test_scenario_execution()
        
        print("\n✅ All tests passed! API fixes are working correctly.")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Manual Testing Commands

```bash
# Run the automated test suite
python test_fixes.py

# Manual testing commands
curl -X POST http://localhost:8000/api/v1/generators/batch/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{"executions": [{"generator_id": "crowdstrike_falcon", "count": 3}]}'

curl -X GET "http://localhost:8000/api/v1/search/generators?q=aws" \
  -H "X-API-Key: your-read-key"

curl -X GET http://localhost:8000/api/v1/export/generators \
  -H "X-API-Key: your-read-key"

curl -X POST http://localhost:8000/api/v1/scenarios/phishing_campaign/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-write-key" \
  -d '{"speed": "fast", "dry_run": false}'
```

---

## Rollback Procedures

### If Issues Arise

1. **Stop the API server:**
   ```bash
   # Find and kill the process
   ps aux | grep uvicorn
   kill <process_id>
   ```

2. **Revert changes using git:**
   ```bash
   git stash  # Save current changes
   git checkout HEAD~1  # Go back to previous commit
   python start_api.py  # Restart with previous version
   ```

3. **Selective rollback for specific issues:**
   - **Validation fixes:** Comment out ValidationError exception handler
   - **Batch execution:** Revert to `List[dict]` parameter type
   - **Missing endpoints:** Remove new router inclusions from main.py

### Emergency Recovery

**File to create:** `/api/emergency_rollback.py`

```python
#!/usr/bin/env python3
"""
Emergency rollback script
"""
import os
import sys
import subprocess

def rollback():
    print("🚨 Starting emergency rollback...")
    
    # Stop current server
    subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
    
    # Revert git changes
    subprocess.run(["git", "checkout", "HEAD~1"], capture_output=True)
    
    # Restart with safe configuration
    env = os.environ.copy()
    env["DISABLE_AUTH"] = "true"  # Disable auth for emergency access
    
    subprocess.run(["python", "start_api.py"], env=env)
    
    print("✅ Emergency rollback completed")

if __name__ == "__main__":
    rollback()
```

---

## Summary

This implementation guide provides step-by-step instructions to fix all critical API issues:

1. **Phase 1 (1-2 days):** Fix input validation, batch execution, and integration issues
2. **Phase 2 (3-4 days):** Implement missing endpoints (export, search, metrics, scenarios)
3. **Phase 3 (2-3 days):** Production hardening and enhanced error handling

**Expected outcome:** API test success rate improves from 75% to 95%+

**Key files to modify:**
- `/api/app/models/responses.py` - Add strict validation
- `/api/app/models/requests.py` - New request models
- `/api/app/routers/generators.py` - Fix batch execution
- `/api/app/routers/export.py` - Add export functionality
- `/api/app/routers/search.py` - Add search functionality
- `/api/app/routers/metrics.py` - Fix base metrics
- `/api/app/services/scenario_service.py` - Scenario management
- `/api/app/services/search_service.py` - Search functionality
- `/api/app/main.py` - Enhanced error handling

Follow the testing procedures after each phase to ensure fixes are working correctly.