# API Fix Developer Checklist

**Document Version:** 1.0  
**Created:** August 30, 2025  
**Based on QA Results:** 75% pass rate (27/36 tests passed)  
**Target Success Rate:** 95%+  

## Pre-Implementation Checklist

### Environment Setup
- [ ] **Backup current codebase**
  ```bash
  git branch api-fixes-backup
  git checkout -b api-fixes-implementation
  ```

- [ ] **Verify API server is running**
  ```bash
  cd /api && python start_api.py
  # Should be accessible at http://localhost:8000
  ```

- [ ] **Confirm test environment**
  ```bash
  # Install test dependencies
  pip install pytest requests
  
  # Verify API keys are configured
  export API_KEYS_READ_ONLY="your-read-key"
  export API_KEYS_WRITE="your-write-key"
  ```

- [ ] **Run baseline tests**
  ```bash
  python api/tests/comprehensive_api_test.py
  # Document current failure rate
  ```

---

## Phase 1: Critical Issues (1-2 Days)

### 🔴 Priority 1: Input Validation Fixes

#### Task 1.1: Create Request Models
- [ ] **Create `/api/app/models/requests.py`**
  - [ ] `BatchExecuteRequest` class with proper validation
  - [ ] `ScenarioExecuteRequest` class  
  - [ ] `CustomScenarioRequest` class
  - [ ] Add `validator` methods for complex validation
  - [ ] Set `extra = "forbid"` to reject unknown fields

**Acceptance Criteria:**
```python
# Test missing fields
response = requests.post(url, json={})
assert response.status_code == 422

# Test invalid values
response = requests.post(url, json={"count": -1})
assert response.status_code == 422
```

#### Task 1.2: Update Response Models
- [ ] **Edit `/api/app/models/responses.py`**
  - [ ] Add strict validation to `GeneratorExecuteRequest`
  - [ ] Use `Field(..., ge=1, le=1000)` for count validation
  - [ ] Add regex validation for format field
  - [ ] Set `validate_assignment = True`

**Acceptance Criteria:**
- [ ] All request models reject extra fields
- [ ] Required field validation working
- [ ] Field type validation working
- [ ] Range validation working

#### Task 1.3: Update Generators Router
- [ ] **Edit `/api/app/routers/generators.py`**
  - [ ] Import `BatchExecuteRequest` from requests models
  - [ ] Update batch execution endpoint signature
  - [ ] Add `ValidationError` exception handling
  - [ ] Import and use proper request models

**Acceptance Criteria:**
```bash
# Batch execution should work
curl -X POST http://localhost:8000/api/v1/generators/batch/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: write-key" \
  -d '{"executions": [{"generator_id": "crowdstrike_falcon", "count": 3}]}'
# Expected: 200 OK
```

#### Task 1.4: Add Global Exception Handlers
- [ ] **Edit `/api/app/main.py`**
  - [ ] Add `ValidationError` exception handler (422 response)
  - [ ] Add `422` HTTP exception handler
  - [ ] Enhance global exception handler with request IDs
  - [ ] Import required exception types

**Testing Requirements:**
- [ ] Test missing required fields return 422
- [ ] Test invalid field values return 422  
- [ ] Test valid requests return 200
- [ ] Test error response format is consistent

---

### 🔴 Priority 2: Batch Execution Fix

#### Task 2.1: Debug Current Issue
- [ ] **Test current batch endpoint**
  ```bash
  curl -X POST http://localhost:8000/api/v1/generators/batch/execute \
    -H "Content-Type: application/json" \
    -H "X-API-Key: write-key" \
    -d '[{"generator_id": "crowdstrike_falcon", "count": 3}]' -v
  ```
- [ ] Document exact error message and status code
- [ ] Identify root cause (likely validation model mismatch)

#### Task 2.2: Fix Batch Execution Endpoint
- [ ] **Update batch execute function in generators router**
  - [ ] Change parameter from `List[dict]` to `BatchExecuteRequest`
  - [ ] Update function body to use `request.executions`
  - [ ] Add proper error handling for validation failures
  - [ ] Test with valid and invalid payloads

**Acceptance Criteria:**
- [ ] Batch execution returns 200 for valid requests
- [ ] Batch execution returns 422 for invalid requests
- [ ] Response includes execution results for each generator
- [ ] Error responses include detailed validation messages

---

### 🔴 Priority 3: End-to-End Integration Fix

#### Task 3.1: Create Debug Script
- [ ] **Create `/api/debug_integration.py`**
  - [ ] Test generators list endpoint
  - [ ] Test generator details endpoint
  - [ ] Test generator execution endpoint
  - [ ] Log detailed error messages and status codes

#### Task 3.2: Run Integration Debug
- [ ] **Execute debug script**
  ```bash
  cd /api && python debug_integration.py
  ```
- [ ] Identify which step fails in the integration workflow
- [ ] Document the exact failure point and error

#### Task 3.3: Fix Data Consistency Issues
- [ ] **Review `/api/app/services/generator_service.py`**
  - [ ] Ensure consistent data formats between list and details endpoints
  - [ ] Verify generator IDs match between endpoints
  - [ ] Add error handling for missing generators
  - [ ] Test with various generator IDs

**Acceptance Criteria:**
- [ ] End-to-end workflow completes successfully
- [ ] Generator list → details → execution works
- [ ] Consistent data formats across endpoints
- [ ] Proper error handling for missing resources

---

## Phase 2: Missing Endpoints (3-4 Days)

### 🟡 Priority 4: Export Functionality

#### Task 4.1: Implement Export Router
- [ ] **Edit `/api/app/routers/export.py`**
  - [ ] Add `GET /generators` endpoint with format support
  - [ ] Add `POST /events` endpoint for bulk event export
  - [ ] Support JSON, CSV, and YAML formats
  - [ ] Add proper content-type headers and file downloads

#### Task 4.2: Test Export Endpoints
- [ ] **Test generators export**
  ```bash
  curl http://localhost:8000/api/v1/export/generators?format=json
  curl http://localhost:8000/api/v1/export/generators?format=csv
  curl http://localhost:8000/api/v1/export/generators?format=yaml
  ```
- [ ] **Test events export**
  ```bash
  curl -X POST http://localhost:8000/api/v1/export/events \
    -H "Content-Type: application/json" \
    -d '["crowdstrike_falcon", "aws_cloudtrail"]'
  ```

**Acceptance Criteria:**
- [ ] Export endpoints return 200 OK
- [ ] CSV format includes proper headers and formatting
- [ ] JSON format is valid and well-structured
- [ ] YAML format is properly formatted
- [ ] File download headers are correct

---

### 🟡 Priority 5: Search Functionality

#### Task 5.1: Create Search Service
- [ ] **Create `/api/app/services/search_service.py`**
  - [ ] Implement text-based search across generators
  - [ ] Add search scoring based on field relevance
  - [ ] Support category and vendor filtering
  - [ ] Add placeholder parser and scenario search

#### Task 5.2: Implement Search Router
- [ ] **Edit `/api/app/routers/search.py`**
  - [ ] Add `GET /generators` search endpoint
  - [ ] Add `GET /parsers` search endpoint  
  - [ ] Add `GET /all` global search endpoint
  - [ ] Include pagination and search metadata

#### Task 5.3: Test Search Functionality
- [ ] **Test generator search**
  ```bash
  curl "http://localhost:8000/api/v1/search/generators?q=aws"
  curl "http://localhost:8000/api/v1/search/generators?q=crowdstrike&category=endpoint_security"
  ```

**Acceptance Criteria:**
- [ ] Search returns relevant results
- [ ] Search scoring works correctly
- [ ] Pagination is implemented
- [ ] Filters work as expected
- [ ] Search metadata is included in response

---

### 🟡 Priority 6: Base Metrics Endpoint

#### Task 6.1: Update Metrics Router
- [ ] **Edit `/api/app/routers/metrics.py`**
  - [ ] Add base `GET /metrics` endpoint
  - [ ] Return API statistics and health metrics
  - [ ] Include generator and parser counts
  - [ ] Add performance metrics

#### Task 6.2: Enhance Metrics Service
- [ ] **Edit `/api/app/services/metrics_service.py`**
  - [ ] Implement `get_base_metrics()` method
  - [ ] Collect API usage statistics
  - [ ] Calculate system health metrics
  - [ ] Add response time tracking

**Acceptance Criteria:**
- [ ] Base metrics endpoint returns 200 OK
- [ ] Metrics include generator counts
- [ ] Performance metrics are included
- [ ] Response format is consistent

---

### 🟡 Priority 7: Scenario Execution Fix

#### Task 7.1: Create Scenario Service
- [ ] **Create `/api/app/services/scenario_service.py`**
  - [ ] Implement scenario management methods
  - [ ] Add background task execution
  - [ ] Support scenario status tracking
  - [ ] Add execution result storage

#### Task 7.2: Test Scenario Execution
- [ ] **Test scenario endpoints**
  ```bash
  curl -X POST http://localhost:8000/api/v1/scenarios/phishing_campaign/execute \
    -H "Content-Type: application/json" \
    -H "X-API-Key: write-key" \
    -d '{"speed": "fast", "dry_run": true}'
  ```

**Acceptance Criteria:**
- [ ] Scenario execution returns 200 OK (not 405)
- [ ] Execution ID is returned
- [ ] Background execution works
- [ ] Status tracking works
- [ ] Results can be retrieved

---

## Phase 3: Production Hardening (2-3 Days)

### 🟢 Priority 8: Enhanced Error Handling

#### Task 8.1: Global Exception Handlers
- [ ] **Update `/api/app/main.py`**
  - [ ] Add comprehensive global exception handler
  - [ ] Include request IDs for tracking
  - [ ] Add structured logging
  - [ ] Implement error categorization

#### Task 8.2: Standardize Error Responses
- [ ] **Review all router files**
  - [ ] Ensure consistent error response format
  - [ ] Add detailed error codes
  - [ ] Include helpful error messages
  - [ ] Add debug information (development only)

**Acceptance Criteria:**
- [ ] All errors return consistent format
- [ ] Error messages are helpful and actionable
- [ ] Request IDs are included for tracking
- [ ] No sensitive information is leaked

---

### 🟢 Priority 9: API Documentation Updates

#### Task 9.1: Create Endpoint Reference
- [ ] **Create `/api/API_ENDPOINTS_REFERENCE.md`**
  - [ ] Document all endpoints with examples
  - [ ] Include authentication requirements
  - [ ] Add request/response schemas
  - [ ] Include error response examples

#### Task 9.2: Update OpenAPI Schema
- [ ] **Verify OpenAPI documentation**
  - [ ] Check http://localhost:8000/api/v1/docs
  - [ ] Ensure all new endpoints are documented
  - [ ] Verify request/response models are correct
  - [ ] Test interactive API documentation

**Acceptance Criteria:**
- [ ] All endpoints are documented
- [ ] Examples are accurate and working
- [ ] OpenAPI schema is complete
- [ ] Interactive docs work correctly

---

## Testing Checklist

### Automated Testing

#### Task 10.1: Create Fix Verification Script
- [ ] **Create `/api/test_fixes.py`**
  - [ ] Test all fixed validation issues
  - [ ] Test batch execution
  - [ ] Test new endpoints
  - [ ] Test scenario execution

#### Task 10.2: Run Comprehensive Tests
- [ ] **Execute test suite**
  ```bash
  python api/tests/comprehensive_api_test.py
  python api/test_fixes.py
  ```
- [ ] **Document test results**
  - [ ] Current pass rate: ____%
  - [ ] Failed tests: ________
  - [ ] Performance metrics: ________

**Acceptance Criteria:**
- [ ] Test pass rate ≥ 95%
- [ ] All critical issues are resolved
- [ ] Performance is maintained or improved
- [ ] No new issues introduced

---

### Manual Testing

#### Task 10.3: Manual Verification
- [ ] **Test each fixed endpoint manually**
  ```bash
  # Input validation
  curl -X POST .../execute -d '{}' # Should return 422
  
  # Batch execution
  curl -X POST .../batch/execute -d '{"executions": [...]}' # Should return 200
  
  # Export functionality
  curl .../export/generators # Should return 200
  
  # Search functionality
  curl ".../search/generators?q=aws" # Should return 200
  
  # Scenario execution
  curl -X POST .../scenarios/phishing_campaign/execute # Should return 200
  ```

- [ ] **Test error scenarios**
  - [ ] Invalid API keys return 403
  - [ ] Missing resources return 404
  - [ ] Invalid data returns 422
  - [ ] Server errors return 500

**Acceptance Criteria:**
- [ ] All endpoints respond correctly
- [ ] Error handling works as expected
- [ ] Performance is acceptable
- [ ] Response formats are consistent

---

## Rollback Procedures

### Emergency Rollback Checklist
- [ ] **Create rollback script** (`/api/emergency_rollback.py`)
- [ ] **Test rollback procedure** in development environment
- [ ] **Document rollback steps** for each phase
- [ ] **Verify backup branches** are available

### Selective Rollback Options
- [ ] **Phase 1 rollback:** Revert validation changes only
- [ ] **Phase 2 rollback:** Disable new endpoints only  
- [ ] **Phase 3 rollback:** Revert error handling only
- [ ] **Full rollback:** Return to pre-fix state

---

## Final Deployment Checklist

### Pre-Production Verification
- [ ] **All tests pass** (≥95% success rate)
- [ ] **Performance benchmarks** meet requirements
- [ ] **Security review** completed
- [ ] **Documentation** is updated and accurate

### Production Deployment
- [ ] **Deploy to staging** environment first
- [ ] **Run full test suite** against staging
- [ ] **Monitor application** logs and metrics
- [ ] **Deploy to production** with monitoring

### Post-Deployment Monitoring
- [ ] **Monitor API response times**
- [ ] **Track error rates** and types
- [ ] **Verify all endpoints** are accessible
- [ ] **Check logs** for unexpected issues

---

## Success Criteria Summary

### Technical Metrics
- [ ] **API Test Pass Rate:** 95%+ (up from 75%)
- [ ] **Response Time:** <100ms average (maintain current performance)
- [ ] **Error Rate:** <1% for valid requests
- [ ] **Uptime:** 99.9%+ availability

### Functional Requirements
- [ ] **Input validation** properly rejects invalid requests (422 status)
- [ ] **Batch execution** works for multiple generators
- [ ] **Export functionality** supports multiple formats
- [ ] **Search functionality** returns relevant results
- [ ] **Scenario execution** works without 405 errors

### Quality Requirements
- [ ] **Error handling** is consistent across all endpoints
- [ ] **Documentation** is complete and accurate
- [ ] **Security** measures are maintained
- [ ] **Performance** is maintained or improved

---

## Team Assignments

### Lead Developer
- [ ] Oversee implementation across all phases
- [ ] Review all code changes
- [ ] Coordinate testing efforts
- [ ] Approve deployment to production

### Backend Developer
- [ ] Implement Phase 1 critical fixes
- [ ] Create and test validation models
- [ ] Fix batch execution issues
- [ ] Debug integration problems

### API Developer
- [ ] Implement Phase 2 missing endpoints
- [ ] Create export functionality
- [ ] Implement search features
- [ ] Fix scenario execution

### QA Engineer
- [ ] Create and run automated tests
- [ ] Perform manual testing
- [ ] Validate fix effectiveness
- [ ] Update test documentation

### DevOps Engineer
- [ ] Prepare deployment procedures
- [ ] Set up monitoring and alerting
- [ ] Create rollback procedures
- [ ] Monitor production deployment

---

**Next Steps:** Begin with Phase 1 critical fixes and use this checklist to track progress through implementation.