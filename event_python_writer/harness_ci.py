#!/usr/bin/env python3
"""
Harness CI/CD event generator
Generates synthetic Harness CI/CD pipeline events
"""
import random
from datetime import datetime, timezone, timedelta

ATTR_FIELDS = {
    "dataSource.vendor": "Harness",
    "dataSource.name": "Harness CI/CD",
    "dataSource.category": "system",
}

PIPELINES = ["pipeline-123", "pipeline-456", "pipeline-789", "frontend-build", "backend-deploy"]
STAGES = ["Build", "Test", "Deploy", "Quality Gate", "Security Scan"]
STEPS = ["UnitTests", "Kubernetes_Rollout", "Docker_Build", "SonarQube_Analysis", "Security_Scan"]
STATUSES = ["STARTED", "SUCCEEDED", "FAILED"]
TRIGGERS = ["manual", "webhook", "schedule", "pull_request"]
INITIATORS = ["devuser", "admin", "ci-bot", "scheduler"]

ERROR_MESSAGES = [
    "Deployment failed due to insufficient permissions",
    "Build failed with compilation errors", 
    "Tests failed with 3 failures",
    "Docker image push failed",
    "Kubernetes deployment timeout"
]

def generate_execution_id():
    """Generate execution ID."""
    return f"exec-{random.randint(100, 999)}"

def generate_duration():
    """Generate duration in HH:MM:SS format."""
    minutes = random.randint(0, 30)
    seconds = random.randint(0, 59)
    return f"00:{minutes:02d}:{seconds:02d}"

def harness_ci_log() -> str:
    """Generate a single Harness CI/CD event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 60))
    
    pipeline_id = random.choice(PIPELINES)
    execution_id = generate_execution_id()
    status = random.choice(STATUSES)
    
    timestamp = event_time.isoformat().replace('+00:00', 'Z')
    log_parts = [
        f'{timestamp} Harness',
        f'pipelineId="{pipeline_id}"',
        f'executionId="{execution_id}"'
    ]
    
    # Add stage and step for non-started events
    if status != "STARTED":
        stage = random.choice(STAGES)
        step = random.choice(STEPS)
        log_parts.append(f'stage="{stage}"')
        log_parts.append(f'step="{step}"')
    
    log_parts.append(f'status="{status}"')
    
    if status == "STARTED":
        trigger = random.choice(TRIGGERS)
        initiator = random.choice(INITIATORS)
        log_parts.append(f'trigger="{trigger}"')
        log_parts.append(f'initiator="{initiator}"')
        message = "Pipeline execution started"
    else:
        duration = generate_duration()
        log_parts.append(f'duration="{duration}"')
        
        if status == "SUCCEEDED":
            message = f"{step.replace('_', ' ').lower()} completed successfully"
        else:  # FAILED
            error = random.choice(ERROR_MESSAGES)
            log_parts.append(f'error="{error.split()[-1]}"')
            message = error
    
    log_parts.append(f'message="{message}"')
    return ' '.join(log_parts)

if __name__ == "__main__":
    print("Sample Harness CI/CD Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(harness_ci_log())