
"""n8n integration module for VMware MCP Server."""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import httpx
from datetime import datetime
from .config import settings
from .exceptions import VMwareMCPException

logger = logging.getLogger(__name__)


class N8nIntegration:
    """Handles integration with n8n for workflow automation."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)
        self.webhook_url = settings.n8n_webhook_url
        self.api_key = settings.n8n_api_key
        self.enabled = settings.enable_n8n
        self.headers = {}
        
        if self.api_key:
            self.headers["X-N8N-API-KEY"] = self.api_key
    
    async def health_check(self) -> bool:
        """Check if n8n service is available."""
        if not self.enabled:
            return False
        
        try:
            # Try to reach n8n health endpoint
            n8n_base = self.webhook_url.replace("/webhook", "")
            response = await self.client.get(f"{n8n_base}/healthz")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"n8n health check failed: {str(e)}")
            return False
    
    async def trigger_workflow(self, workflow_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an n8n workflow with data."""
        if not self.enabled:
            return {"error": "n8n integration is disabled"}
        
        try:
            payload = {
                "workflow": workflow_name,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "vmware-mcp-server",
                "data": data
            }
            
            response = await self.client.post(
                self.webhook_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "workflow": workflow_name,
                "response": response.json() if response.content else {},
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger n8n workflow {workflow_name}: {str(e)}")
            return {
                "success": False,
                "workflow": workflow_name,
                "error": str(e)
            }
    
    async def send_vm_event(self, event_type: str, vm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send VM-related events to n8n workflows."""
        return await self.trigger_workflow("vm_events", {
            "event_type": event_type,
            "vm_data": vm_data,
            "category": "virtual_machine"
        })
    
    async def send_host_event(self, event_type: str, host_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send host-related events to n8n workflows."""
        return await self.trigger_workflow("host_events", {
            "event_type": event_type,
            "host_data": host_data,
            "category": "host_system"
        })
    
    async def send_alert(self, alert_type: str, severity: str, message: str, 
                        details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send alerts to n8n for processing."""
        return await self.trigger_workflow("alerts", {
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "details": details or {},
            "category": "alert"
        })
    
    async def send_performance_data(self, resource_type: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Send performance metrics to n8n for analysis."""
        return await self.trigger_workflow("performance_monitoring", {
            "resource_type": resource_type,
            "metrics": metrics,
            "category": "performance"
        })
    
    async def send_maintenance_notification(self, maintenance_type: str, 
                                          affected_resources: List[str],
                                          schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Send maintenance notifications to n8n."""
        return await self.trigger_workflow("maintenance_notifications", {
            "maintenance_type": maintenance_type,
            "affected_resources": affected_resources,
            "schedule": schedule,
            "category": "maintenance"
        })
    
    async def request_approval(self, operation: str, details: Dict[str, Any], 
                             requester: str) -> Dict[str, Any]:
        """Request approval for sensitive operations through n8n."""
        return await self.trigger_workflow("approval_requests", {
            "operation": operation,
            "details": details,
            "requester": requester,
            "category": "approval"
        })
    
    async def send_backup_status(self, backup_type: str, status: str, 
                               resources: List[str], details: Dict[str, Any]) -> Dict[str, Any]:
        """Send backup status updates to n8n."""
        return await self.trigger_workflow("backup_status", {
            "backup_type": backup_type,
            "status": status,
            "resources": resources,
            "details": details,
            "category": "backup"
        })
    
    async def send_compliance_report(self, report_type: str, findings: List[Dict[str, Any]],
                                   summary: Dict[str, Any]) -> Dict[str, Any]:
        """Send compliance reports to n8n."""
        return await self.trigger_workflow("compliance_reports", {
            "report_type": report_type,
            "findings": findings,
            "summary": summary,
            "category": "compliance"
        })
    
    async def create_incident(self, title: str, description: str, severity: str,
                            affected_resources: List[str]) -> Dict[str, Any]:
        """Create an incident in external systems via n8n."""
        return await self.trigger_workflow("incident_management", {
            "action": "create",
            "title": title,
            "description": description,
            "severity": severity,
            "affected_resources": affected_resources,
            "category": "incident"
        })
    
    async def update_cmdb(self, resource_type: str, resource_id: str, 
                         changes: Dict[str, Any]) -> Dict[str, Any]:
        """Update CMDB with resource changes via n8n."""
        return await self.trigger_workflow("cmdb_updates", {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "changes": changes,
            "category": "cmdb"
        })
    
    async def send_capacity_alert(self, resource_type: str, current_usage: float,
                                threshold: float, recommendations: List[str]) -> Dict[str, Any]:
        """Send capacity planning alerts to n8n."""
        return await self.trigger_workflow("capacity_alerts", {
            "resource_type": resource_type,
            "current_usage": current_usage,
            "threshold": threshold,
            "recommendations": recommendations,
            "category": "capacity"
        })
    
    async def trigger_automated_remediation(self, issue_type: str, 
                                          affected_resources: List[str],
                                          remediation_steps: List[str]) -> Dict[str, Any]:
        """Trigger automated remediation workflows in n8n."""
        return await self.trigger_workflow("automated_remediation", {
            "issue_type": issue_type,
            "affected_resources": affected_resources,
            "remediation_steps": remediation_steps,
            "category": "remediation"
        })
    
    async def send_custom_webhook(self, webhook_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to a custom n8n webhook endpoint."""
        if not self.enabled:
            return {"error": "n8n integration is disabled"}
        
        try:
            webhook_url = self.webhook_url.replace("/webhook", f"/{webhook_path}")
            
            response = await self.client.post(
                webhook_url,
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "webhook_path": webhook_path,
                "response": response.json() if response.content else {},
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to send custom webhook to {webhook_path}: {str(e)}")
            return {
                "success": False,
                "webhook_path": webhook_path,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class WorkflowTemplates:
    """Pre-defined workflow templates for common VMware operations."""
    
    @staticmethod
    def vm_lifecycle_workflow() -> Dict[str, Any]:
        """Template for VM lifecycle management workflow."""
        return {
            "name": "VM Lifecycle Management",
            "description": "Automated VM provisioning, monitoring, and decommissioning",
            "triggers": [
                "vm_creation_request",
                "vm_performance_degradation",
                "vm_decommission_request"
            ],
            "actions": [
                "validate_requirements",
                "provision_vm",
                "configure_monitoring",
                "send_notifications",
                "update_inventory"
            ]
        }
    
    @staticmethod
    def maintenance_workflow() -> Dict[str, Any]:
        """Template for maintenance management workflow."""
        return {
            "name": "Maintenance Management",
            "description": "Automated maintenance planning and execution",
            "triggers": [
                "maintenance_scheduled",
                "patch_available",
                "hardware_alert"
            ],
            "actions": [
                "create_maintenance_window",
                "migrate_vms",
                "enter_maintenance_mode",
                "apply_updates",
                "validate_systems",
                "exit_maintenance_mode",
                "send_completion_report"
            ]
        }
    
    @staticmethod
    def performance_monitoring_workflow() -> Dict[str, Any]:
        """Template for performance monitoring workflow."""
        return {
            "name": "Performance Monitoring",
            "description": "Continuous performance monitoring and alerting",
            "triggers": [
                "performance_threshold_exceeded",
                "resource_exhaustion",
                "anomaly_detected"
            ],
            "actions": [
                "collect_metrics",
                "analyze_trends",
                "generate_alerts",
                "suggest_optimizations",
                "create_reports"
            ]
        }


# Global n8n integration instance
n8n_integration = N8nIntegration()
