"""
Scenario service for managing attack scenarios
"""
import uuid
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import BackgroundTasks
import importlib.util
import sys

from app.core.config import settings
from app.services.generator_service import GeneratorService


class ScenarioService:
    """Service for managing attack scenarios"""
    
    def __init__(self):
        self.scenarios_path = settings.SCENARIOS_PATH
        self.generator_service = GeneratorService()
        self.executions = {}  # In-memory execution tracking
        
    async def list_scenarios(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all available scenarios"""
        scenarios = []
        
        # Pre-defined scenarios
        predefined = [
            {
                "id": "enterprise_attack",
                "name": "Enterprise Attack Campaign",
                "description": "14-day APT campaign simulation",
                "category": "apt",
                "duration_days": 14,
                "phases": 5,
                "generators_used": 25
            },
            {
                "id": "quick_phishing",
                "name": "Quick Phishing Attack",
                "description": "30-minute phishing simulation",
                "category": "phishing",
                "duration_minutes": 30,
                "phases": 3,
                "generators_used": 5
            },
            {
                "id": "ransomware_sim",
                "name": "Ransomware Simulation",
                "description": "Ransomware attack lifecycle",
                "category": "ransomware",
                "duration_hours": 2,
                "phases": 4,
                "generators_used": 8
            },
            {
                "id": "insider_threat",
                "name": "Insider Threat Scenario",
                "description": "Malicious insider activity",
                "category": "insider",
                "duration_hours": 4,
                "phases": 6,
                "generators_used": 12
            },
            {
                "id": "cloud_breach",
                "name": "Cloud Infrastructure Breach",
                "description": "AWS/Azure account compromise",
                "category": "cloud",
                "duration_hours": 3,
                "phases": 5,
                "generators_used": 10
            }
        ]
        
        # Filter by category
        if category:
            predefined = [s for s in predefined if s.get("category") == category]
        
        # Search filter
        if search:
            search_lower = search.lower()
            predefined = [
                s for s in predefined 
                if search_lower in s["name"].lower() or 
                   search_lower in s["description"].lower()
            ]
        
        return predefined + scenarios
    
    async def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific scenario"""
        scenarios = await self.list_scenarios()
        for scenario in scenarios:
            if scenario["id"] == scenario_id:
                # Add more details
                scenario["configuration"] = self._get_scenario_config(scenario_id)
                return scenario
        return None
    
    def _get_scenario_config(self, scenario_id: str) -> Dict[str, Any]:
        """Get scenario configuration"""
        configs = {
            "enterprise_attack": {
                "phases": [
                    {
                        "name": "Reconnaissance",
                        "duration_hours": 48,
                        "generators": ["aws_cloudtrail", "google_cloud_dns", "cisco_umbrella"],
                        "events_per_hour": 20
                    },
                    {
                        "name": "Initial Access",
                        "duration_hours": 24,
                        "generators": ["okta_authentication", "microsoft_azuread", "cisco_duo"],
                        "events_per_hour": 50
                    },
                    {
                        "name": "Persistence",
                        "duration_hours": 72,
                        "generators": ["crowdstrike_falcon", "sentinelone_endpoint"],
                        "events_per_hour": 30
                    },
                    {
                        "name": "Privilege Escalation",
                        "duration_hours": 48,
                        "generators": ["cyberark_pas", "beyondtrust_passwordsafe"],
                        "events_per_hour": 40
                    },
                    {
                        "name": "Exfiltration",
                        "duration_hours": 144,
                        "generators": ["netskope", "zscaler", "aws_vpcflowlogs"],
                        "events_per_hour": 100
                    }
                ],
                "threat_actors": ["APT28", "Lazarus Group"],
                "mitre_techniques": ["T1190", "T1078", "T1136", "T1055", "T1048"]
            },
            "quick_phishing": {
                "phases": [
                    {
                        "name": "Email Delivery",
                        "duration_minutes": 5,
                        "generators": ["mimecast", "proofpoint"],
                        "events_per_minute": 10
                    },
                    {
                        "name": "Credential Harvest",
                        "duration_minutes": 15,
                        "generators": ["okta_authentication", "microsoft_azuread"],
                        "events_per_minute": 5
                    },
                    {
                        "name": "Account Compromise",
                        "duration_minutes": 10,
                        "generators": ["crowdstrike_falcon", "microsoft_365_collaboration"],
                        "events_per_minute": 8
                    }
                ],
                "indicators": ["malicious-domain.com", "10.13.37.1"],
                "mitre_techniques": ["T1566", "T1078"]
            }
        }
        
        return configs.get(scenario_id, {})
    
    async def start_scenario(
        self,
        scenario_id: str,
        speed: str = "fast",
        dry_run: bool = False,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> str:
        """Start executing a scenario"""
        execution_id = str(uuid.uuid4())
        
        self.executions[execution_id] = {
            "scenario_id": scenario_id,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "speed": speed,
            "dry_run": dry_run,
            "progress": 0,
            "events_generated": 0,
            "current_phase": "",
            "errors": []
        }
        
        # Execute scenario in background if background_tasks provided
        if background_tasks:
            background_tasks.add_task(
                self._execute_scenario,
                scenario_id,
                execution_id,
                speed,
                dry_run
            )
        else:
            # Execute synchronously for testing
            await self._execute_scenario(scenario_id, execution_id, speed, dry_run)
        
        return execution_id
    
    async def _execute_scenario(
        self,
        scenario_id: str,
        execution_id: str,
        speed: str,
        dry_run: bool
    ):
        """Execute scenario phases"""
        try:
            config = self._get_scenario_config(scenario_id)
            if not config:
                self.executions[execution_id]["status"] = "failed"
                self.executions[execution_id]["error"] = "Scenario configuration not found"
                return
            
            total_phases = len(config.get("phases", []))
            
            for i, phase in enumerate(config.get("phases", [])):
                if execution_id not in self.executions:
                    break  # Scenario was stopped
                    
                if self.executions[execution_id]["status"] == "stopped":
                    break
                
                self.executions[execution_id]["current_phase"] = phase["name"]
                self.executions[execution_id]["progress"] = int((i / total_phases) * 100)
                
                if not dry_run:
                    # Generate events for this phase
                    for generator_id in phase.get("generators", []):
                        try:
                            events = await self.generator_service.execute_generator(
                                generator_id,
                                count=phase.get("events_per_minute", 10) if "duration_minutes" in phase 
                                      else phase.get("events_per_hour", 30),
                                format="json"
                            )
                            self.executions[execution_id]["events_generated"] += len(events)
                        except Exception as e:
                            self.executions[execution_id]["errors"].append(
                                f"Generator {generator_id} failed: {str(e)}"
                            )
                
                # Simulate timing based on speed
                if speed == "realtime":
                    if "duration_minutes" in phase:
                        await asyncio.sleep(phase["duration_minutes"] * 60)
                    elif "duration_hours" in phase:
                        await asyncio.sleep(phase["duration_hours"] * 3600)
                elif speed == "fast":
                    await asyncio.sleep(2)  # 2 seconds per phase
                # instant = no delay
            
            self.executions[execution_id]["status"] = "completed"
            self.executions[execution_id]["progress"] = 100
            self.executions[execution_id]["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            self.executions[execution_id]["status"] = "failed"
            self.executions[execution_id]["error"] = str(e)
    
    async def get_execution_status(
        self,
        scenario_id: str,
        execution_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        if execution_id:
            return self.executions.get(execution_id)
        
        # Get all executions for scenario
        scenario_executions = [
            exec_data for exec_id, exec_data in self.executions.items()
            if exec_data["scenario_id"] == scenario_id
        ]
        
        return {
            "scenario_id": scenario_id,
            "executions": scenario_executions
        }
    
    async def stop_execution(self, scenario_id: str, execution_id: str) -> bool:
        """Stop a running execution"""
        if execution_id in self.executions:
            self.executions[execution_id]["status"] = "stopped"
            self.executions[execution_id]["stopped_at"] = datetime.utcnow().isoformat()
            return True
        return False
    
    async def get_execution_results(
        self,
        scenario_id: str,
        execution_id: str,
        include_events: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get execution results"""
        if execution_id not in self.executions:
            return None
        
        results = self.executions[execution_id].copy()
        
        # Add summary statistics
        results["summary"] = {
            "total_events": results.get("events_generated", 0),
            "duration": self._calculate_duration(results),
            "phases_completed": self._count_completed_phases(results),
            "success_rate": 100 if not results.get("errors") else 90
        }
        
        if include_events:
            # In production, this would fetch from storage
            results["sample_events"] = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "generator": "sample",
                    "phase": "sample",
                    "event": {"message": "Sample event data"}
                }
            ]
        
        return results
    
    def _calculate_duration(self, execution: Dict) -> str:
        """Calculate execution duration"""
        if "started_at" in execution and "completed_at" in execution:
            start = datetime.fromisoformat(execution["started_at"])
            end = datetime.fromisoformat(execution["completed_at"])
            duration = end - start
            return str(duration)
        return "In progress"
    
    def _count_completed_phases(self, execution: Dict) -> int:
        """Count completed phases based on progress"""
        progress = execution.get("progress", 0)
        # Rough estimate based on progress percentage
        return int(progress / 20)  # Assuming 5 phases = 20% each
    
    async def create_custom_scenario(self, config: Dict[str, Any]) -> str:
        """Create a custom scenario from configuration"""
        scenario_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # Store custom scenario configuration
        # In production, this would persist to database
        self._custom_scenarios = getattr(self, "_custom_scenarios", {})
        self._custom_scenarios[scenario_id] = config
        
        return scenario_id
    
    async def get_execution_timeline(
        self,
        scenario_id: str,
        execution_id: str
    ) -> List[Dict[str, Any]]:
        """Get timeline of events for visualization"""
        if execution_id not in self.executions:
            return []
        
        execution = self.executions[execution_id]
        config = self._get_scenario_config(scenario_id)
        
        timeline = []
        base_time = datetime.fromisoformat(execution["started_at"])
        
        for i, phase in enumerate(config.get("phases", [])):
            phase_time = base_time + timedelta(hours=i)  # Simplified timing
            timeline.append({
                "timestamp": phase_time.isoformat(),
                "phase": phase["name"],
                "generators": phase["generators"],
                "status": "completed" if execution["progress"] > (i * 20) else "pending"
            })
        
        return timeline