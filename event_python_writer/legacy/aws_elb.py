#!/usr/bin/env python3
"""
AWS Elastic Load Balancer (ELB) event generator (JSON format)
Generates AWS Application Load Balancer (ALB) and Network Load Balancer (NLB) access logs
"""
from __future__ import annotations
import json
import random
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "AWS",
    "dataSource.name": "AWS Elastic Load Balancer",
    "dataSource.category": "security",
    "event.type": "Elastic Load Balancer Access log"
}

# ELB types
ELB_TYPES = ["http", "https", "h2", "ws", "wss"]

# HTTP methods
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]

# Common paths
PATHS = [
    "/", "/api/v1/users", "/api/v1/products", "/api/v1/orders",
    "/health", "/status", "/metrics", "/login", "/logout",
    "/static/css/main.css", "/static/js/app.js", "/images/logo.png",
    "/api/v2/accounts", "/api/v2/transactions", "/webhooks/payment",
    "/admin/dashboard", "/reports/daily", "/download/file.pdf"
]

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "curl/7.68.0",
    "python-requests/2.25.1",
    "Java/11.0.11",
    "Go-http-client/2.0",
    "PostmanRuntime/7.28.0"
]

# SSL protocols and ciphers
SSL_PROTOCOLS = ["TLSv1.2", "TLSv1.3"]
SSL_CIPHERS = [
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES128-SHA256",
    "ECDHE-RSA-AES256-SHA384",
    "TLS_AES_128_GCM_SHA256",
    "TLS_AES_256_GCM_SHA384"
]

# Target groups
TARGET_GROUPS = [
    "targetgroup/app-servers/50dc6c495c0c9188",
    "targetgroup/api-servers/73e2d6bc24d8a067",
    "targetgroup/web-servers/f8c5d4e9a1b2c3d4",
    "targetgroup/backend-services/a1b2c3d4e5f6g7h8"
]

# Actions
ACTIONS = ["forward", "redirect", "fixed-response", "authenticate-oidc", "authenticate-cognito"]

# Redirect status codes
REDIRECT_STATUS_CODES = ["301", "302", "303", "307", "308"]

def _generate_ip(internal: bool = True) -> str:
    """Generate an IP address"""
    if internal:
        return random.choice([
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
        ])
    else:
        # Public IPs
        return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def _generate_elb_name() -> str:
    """Generate an ELB name"""
    environments = ["prod", "staging", "dev", "test"]
    services = ["web", "api", "app", "backend", "frontend"]
    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
    
    env = random.choice(environments)
    service = random.choice(services)
    region = random.choice(regions)
    
    return f"app/{env}-{service}-alb/{uuid.uuid4().hex[:16]}"

def _generate_trace_id() -> str:
    """Generate an AWS X-Ray trace ID"""
    return f"Root=1-{int(time.time()):08x}-{uuid.uuid4().hex[:24]}"

def aws_elb_log(overrides: dict | None = None) -> Dict:
    """
    Return a single AWS ELB access log event as JSON string.
    
    Pass `overrides` to force any field to a specific value:
        aws_elb_log({"request_verb": "POST", "alb_status_code": "200"})
    """
    # Generate timestamps
    now = datetime.now(timezone.utc)
    timestamp = now - timedelta(seconds=random.randint(0, 300))
    
    # Request processing times (in seconds)
    request_processing_time = random.uniform(0.0001, 0.01)
    backend_processing_time = random.uniform(0.001, 2.0)
    response_processing_time = random.uniform(0.0001, 0.01)
    
    # Determine request details
    elb_type = random.choice(ELB_TYPES)
    method = random.choice(HTTP_METHODS)
    path = random.choice(PATHS)
    http_version = random.choice(["HTTP/1.1", "HTTP/2.0"])
    
    # Determine status codes
    if path in ["/health", "/status"]:
        # Health checks usually succeed
        backend_status_code = 200
        alb_status_code = "-"
    elif method == "POST" and "/api/" in path:
        # API posts might have various responses
        backend_status_code = random.choices(
            [200, 201, 400, 401, 403, 500],
            weights=[0.4, 0.3, 0.1, 0.05, 0.05, 0.1]
        )[0]
        alb_status_code = "-"
    else:
        # General requests
        backend_status_code = random.choices(
            [200, 301, 302, 304, 400, 401, 403, 404, 500, 502, 503],
            weights=[0.6, 0.05, 0.05, 0.1, 0.05, 0.02, 0.03, 0.05, 0.02, 0.02, 0.01]
        )[0]
        alb_status_code = "-"
    
    # Sometimes ALB returns its own status
    if random.random() < 0.05:
        alb_status_code = random.choice(["400", "403", "500", "502", "503", "504"])
        backend_status_code = "-"
        backend_processing_time = -1
    
    # Calculate bytes based on request type
    if method in ["GET", "HEAD"]:
        received_bytes = random.randint(100, 500)
    elif method in ["POST", "PUT", "PATCH"]:
        received_bytes = random.randint(200, 50000)
    else:
        received_bytes = random.randint(100, 300)
    
    # Response bytes based on status and path
    if backend_status_code == "-":
        sent_bytes = 0
    elif backend_status_code in [301, 302, 303, 307, 308, 304]:
        sent_bytes = random.randint(200, 500)
    elif backend_status_code >= 400:
        sent_bytes = random.randint(200, 2000)
    elif path.endswith(('.css', '.js', '.png', '.jpg')):
        sent_bytes = random.randint(5000, 500000)
    else:
        sent_bytes = random.randint(500, 50000)
    
    # Client and backend IPs
    client_ip = _generate_ip(internal=False)
    client_port = random.randint(1024, 65535)
    
    # Backend details
    if backend_status_code != "-":
        backend_ip = _generate_ip(internal=True)
        backend_port = random.choice([80, 8080, 3000, 5000, 8000])
    else:
        backend_ip = "-"
        backend_port = "-"
    
    # Generate request string
    request_url = f"{elb_type.upper()}://{random.choice(['app.example.com', 'api.example.com', 'www.example.com'])}:{443 if 'https' in elb_type else 80}{path}"
    request = f"{method} {request_url} {http_version}"
    
    event = {
        "type": elb_type,
        "time": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "alb": _generate_elb_name(),
        "client_ip": client_ip,
        "client_port": client_port,
        "backend_ip": backend_ip,
        "backend_port": backend_port,
        "request_processing_time": round(request_processing_time, 6),
        "backend_processing_time": round(backend_processing_time, 6),
        "response_processing_time": round(response_processing_time, 6),
        "alb_status_code": alb_status_code,
        "backend_status_code": str(backend_status_code) if backend_status_code != "-" else "-",
        "received_bytes": received_bytes,
        "sent_bytes": sent_bytes,
        "request_verb": method,
        "request": request,
        "user_agent": random.choice(USER_AGENTS),
        "ssl_cipher": random.choice(SSL_CIPHERS) if "https" in elb_type else "-",
        "ssl_protocol": random.choice(SSL_PROTOCOLS) if "https" in elb_type else "-",
        "target_group_arn": random.choice(TARGET_GROUPS) if backend_status_code != "-" else "-",
        "trace_id": _generate_trace_id(),
        "domain_name": random.choice(["app.example.com", "api.example.com", "www.example.com"]),
        "chosen_cert_arn": f"arn:aws:acm:us-east-1:123456789012:certificate/{uuid.uuid4()}" if "https" in elb_type else "-",
        "matched_rule_priority": str(random.randint(1, 100)),
        "request_creation_time": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "actions_executed": random.choice(ACTIONS),
        "redirect_url": f"https://www.example.com{path}" if alb_status_code in REDIRECT_STATUS_CODES else "-",
        "lambda_error_reason": "-",
        "target_port_list": [str(backend_port)] if backend_port != "-" else [],
        "target_status_code_list": [str(backend_status_code)] if backend_status_code != "-" else [],
        "classification": "-",
        "classification_reason": "-"
    }
    
    # Apply any overrides
    if overrides:
        event.update(overrides)
    
    return event

if __name__ == "__main__":
    # Generate sample logs
    print("Sample AWS ELB access logs:")
    
    # Successful request
    print("\nSuccessful request:")
    print(aws_elb_log({"request_verb": "GET", "backend_status_code": "200"}))
    
    # Failed request
    print("\nFailed request:")
    print(aws_elb_log({"request_verb": "POST", "backend_status_code": "500"}))
    
    # ALB rejection
    print("\nALB rejection:")
    print(aws_elb_log({"alb_status_code": "403", "backend_status_code": "-"}))
    
    print()