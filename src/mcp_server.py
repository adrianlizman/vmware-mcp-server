
"""Main MCP server implementation for VMware operations."""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from .auth import auth_manager, RBACManager
from .vm_operations import vm_ops
from .host_operations import host_ops
from .snapshot_operations import snapshot_ops
from .resource_operations import resource_ops
from .ollama_integration import ollama_integration
from .n8n_integration import n8n_integration
from .exceptions import VMwareMCPException, AuthorizationError
from .config import settings

logger = logging.getLogger(__name__)


class VMwareMCPServer:
    """Main MCP server for VMware operations."""
    
    def __init__(self):
        self.server = Server("vmware-mcp-server")
        self.setup_tools()
        self.setup_handlers()
    
    def setup_tools(self):
        """Register all available tools."""
        
        # VM Management Tools
        self.server.list_tools = self._list_tools
        
        # VM Operations
        self.register_tool("list_vms", "List all virtual machines", {
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("get_vm_details", "Get detailed information about a VM", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("start_vm", "Start a virtual machine", {
            "vm_name": {"type": "string", "description": "Name of the VM to start"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("stop_vm", "Stop a virtual machine", {
            "vm_name": {"type": "string", "description": "Name of the VM to stop"},
            "force": {"type": "boolean", "description": "Force power off", "default": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("restart_vm", "Restart a virtual machine", {
            "vm_name": {"type": "string", "description": "Name of the VM to restart"},
            "force": {"type": "boolean", "description": "Force restart", "default": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("clone_vm", "Clone a virtual machine", {
            "source_vm_name": {"type": "string", "description": "Name of the source VM"},
            "clone_name": {"type": "string", "description": "Name for the cloned VM"},
            "datastore_name": {"type": "string", "description": "Target datastore name", "required": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("delete_vm", "Delete a virtual machine", {
            "vm_name": {"type": "string", "description": "Name of the VM to delete"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "admin"}
        })
        
        self.register_tool("migrate_vm", "Migrate a virtual machine", {
            "vm_name": {"type": "string", "description": "Name of the VM to migrate"},
            "target_host": {"type": "string", "description": "Target host name", "required": False},
            "target_datastore": {"type": "string", "description": "Target datastore name", "required": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "admin"}
        })
        
        # Host Operations
        self.register_tool("list_hosts", "List all ESXi hosts", {
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("get_host_details", "Get detailed information about a host", {
            "host_name": {"type": "string", "description": "Name of the host"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("enter_maintenance_mode", "Put host into maintenance mode", {
            "host_name": {"type": "string", "description": "Name of the host"},
            "evacuate_powered_off_vms": {"type": "boolean", "description": "Evacuate powered off VMs", "default": True},
            "timeout_seconds": {"type": "integer", "description": "Timeout in seconds", "default": 300},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "admin"}
        })
        
        self.register_tool("exit_maintenance_mode", "Exit maintenance mode", {
            "host_name": {"type": "string", "description": "Name of the host"},
            "timeout_seconds": {"type": "integer", "description": "Timeout in seconds", "default": 300},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "admin"}
        })
        
        self.register_tool("reboot_host", "Reboot an ESXi host", {
            "host_name": {"type": "string", "description": "Name of the host"},
            "force": {"type": "boolean", "description": "Force reboot", "default": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "admin"}
        })
        
        self.register_tool("get_host_performance", "Get host performance metrics", {
            "host_name": {"type": "string", "description": "Name of the host"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        # Snapshot Operations
        self.register_tool("create_snapshot", "Create a VM snapshot", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "snapshot_name": {"type": "string", "description": "Name for the snapshot"},
            "description": {"type": "string", "description": "Snapshot description", "default": ""},
            "memory": {"type": "boolean", "description": "Include memory", "default": False},
            "quiesce": {"type": "boolean", "description": "Quiesce filesystem", "default": True},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("list_snapshots", "List VM snapshots", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("revert_snapshot", "Revert to a snapshot", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "snapshot_name": {"type": "string", "description": "Name of the snapshot"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("delete_snapshot", "Delete a snapshot", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "snapshot_name": {"type": "string", "description": "Name of the snapshot"},
            "remove_children": {"type": "boolean", "description": "Remove child snapshots", "default": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        self.register_tool("delete_all_snapshots", "Delete all snapshots", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "operator"}
        })
        
        # Resource Operations
        self.register_tool("get_cluster_resources", "Get cluster resource summary", {
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("modify_vm_resources", "Modify VM CPU and memory", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "cpu_count": {"type": "integer", "description": "Number of CPU cores", "required": False},
            "memory_mb": {"type": "integer", "description": "Memory in MB", "required": False},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "admin"}
        })
        
        self.register_tool("get_vm_resource_usage", "Get VM resource usage", {
            "vm_name": {"type": "string", "description": "Name of the VM"},
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        self.register_tool("get_datastore_usage", "Get datastore usage", {
            "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
        })
        
        # AI Integration Tools
        if settings.enable_ollama:
            self.register_tool("analyze_vm_performance", "AI analysis of VM performance", {
                "vm_name": {"type": "string", "description": "Name of the VM to analyze"},
                "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
            })
            
            self.register_tool("suggest_vm_sizing", "AI-powered VM sizing recommendations", {
                "workload_description": {"type": "string", "description": "Description of the workload"},
                "requirements": {"type": "object", "description": "Workload requirements"},
                "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
            })
            
            self.register_tool("troubleshoot_issue", "AI troubleshooting assistance", {
                "issue_description": {"type": "string", "description": "Description of the issue"},
                "vm_name": {"type": "string", "description": "Affected VM name", "required": False},
                "user_role": {"type": "string", "description": "User role for authorization", "default": "viewer"}
            })
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any]):
        """Register a tool with the MCP server."""
        tool = Tool(
            name=name,
            description=description,
            inputSchema={
                "type": "object",
                "properties": parameters,
                "required": [k for k, v in parameters.items() if v.get("required", True)]
            }
        )
        # Store tool for later retrieval
        if not hasattr(self, '_tools'):
            self._tools = {}
        self._tools[name] = tool
    
    async def _list_tools(self) -> List[Tool]:
        """Return list of available tools."""
        return list(self._tools.values()) if hasattr(self, '_tools') else []
    
    def setup_handlers(self):
        """Setup MCP message handlers."""
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                result = await self._execute_tool(name, arguments)
                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                logger.error(f"Tool execution failed for {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with the given arguments."""
        
        # VM Operations
        if name == "list_vms":
            return await vm_ops.list_vms(arguments.get("user_role", "viewer"))
        
        elif name == "get_vm_details":
            return await vm_ops.get_vm_details(
                arguments["vm_name"], 
                arguments.get("user_role", "viewer")
            )
        
        elif name == "start_vm":
            return await vm_ops.start_vm(
                arguments["vm_name"], 
                arguments.get("user_role", "operator")
            )
        
        elif name == "stop_vm":
            return await vm_ops.stop_vm(
                arguments["vm_name"], 
                arguments.get("force", False),
                arguments.get("user_role", "operator")
            )
        
        elif name == "restart_vm":
            return await vm_ops.restart_vm(
                arguments["vm_name"], 
                arguments.get("force", False),
                arguments.get("user_role", "operator")
            )
        
        elif name == "clone_vm":
            return await vm_ops.clone_vm(
                arguments["source_vm_name"],
                arguments["clone_name"],
                arguments.get("datastore_name"),
                arguments.get("user_role", "operator")
            )
        
        elif name == "delete_vm":
            return await vm_ops.delete_vm(
                arguments["vm_name"],
                arguments.get("user_role", "admin")
            )
        
        elif name == "migrate_vm":
            return await vm_ops.migrate_vm(
                arguments["vm_name"],
                arguments.get("target_host"),
                arguments.get("target_datastore"),
                arguments.get("user_role", "admin")
            )
        
        # Host Operations
        elif name == "list_hosts":
            return await host_ops.list_hosts(arguments.get("user_role", "viewer"))
        
        elif name == "get_host_details":
            return await host_ops.get_host_details(
                arguments["host_name"],
                arguments.get("user_role", "viewer")
            )
        
        elif name == "enter_maintenance_mode":
            return await host_ops.enter_maintenance_mode(
                arguments["host_name"],
                arguments.get("evacuate_powered_off_vms", True),
                arguments.get("timeout_seconds", 300),
                arguments.get("user_role", "admin")
            )
        
        elif name == "exit_maintenance_mode":
            return await host_ops.exit_maintenance_mode(
                arguments["host_name"],
                arguments.get("timeout_seconds", 300),
                arguments.get("user_role", "admin")
            )
        
        elif name == "reboot_host":
            return await host_ops.reboot_host(
                arguments["host_name"],
                arguments.get("force", False),
                arguments.get("user_role", "admin")
            )
        
        elif name == "get_host_performance":
            return await host_ops.get_host_performance(
                arguments["host_name"],
                arguments.get("user_role", "viewer")
            )
        
        # Snapshot Operations
        elif name == "create_snapshot":
            return await snapshot_ops.create_snapshot(
                arguments["vm_name"],
                arguments["snapshot_name"],
                arguments.get("description", ""),
                arguments.get("memory", False),
                arguments.get("quiesce", True),
                arguments.get("user_role", "operator")
            )
        
        elif name == "list_snapshots":
            return await snapshot_ops.list_snapshots(
                arguments["vm_name"],
                arguments.get("user_role", "viewer")
            )
        
        elif name == "revert_snapshot":
            return await snapshot_ops.revert_snapshot(
                arguments["vm_name"],
                arguments["snapshot_name"],
                arguments.get("user_role", "operator")
            )
        
        elif name == "delete_snapshot":
            return await snapshot_ops.delete_snapshot(
                arguments["vm_name"],
                arguments["snapshot_name"],
                arguments.get("remove_children", False),
                arguments.get("user_role", "operator")
            )
        
        elif name == "delete_all_snapshots":
            return await snapshot_ops.delete_all_snapshots(
                arguments["vm_name"],
                arguments.get("user_role", "operator")
            )
        
        # Resource Operations
        elif name == "get_cluster_resources":
            return await resource_ops.get_cluster_resources(
                arguments.get("user_role", "viewer")
            )
        
        elif name == "modify_vm_resources":
            return await resource_ops.modify_vm_resources(
                arguments["vm_name"],
                arguments.get("cpu_count"),
                arguments.get("memory_mb"),
                arguments.get("user_role", "admin")
            )
        
        elif name == "get_vm_resource_usage":
            return await resource_ops.get_vm_resource_usage(
                arguments["vm_name"],
                arguments.get("user_role", "viewer")
            )
        
        elif name == "get_datastore_usage":
            return await resource_ops.get_datastore_usage(
                arguments.get("user_role", "viewer")
            )
        
        # AI Integration Tools
        elif name == "analyze_vm_performance" and settings.enable_ollama:
            vm_data = await vm_ops.get_vm_details(
                arguments["vm_name"],
                arguments.get("user_role", "viewer")
            )
            return await ollama_integration.analyze_vm_performance(vm_data)
        
        elif name == "suggest_vm_sizing" and settings.enable_ollama:
            return await ollama_integration.suggest_vm_sizing(
                arguments["workload_description"],
                arguments["requirements"]
            )
        
        elif name == "troubleshoot_issue" and settings.enable_ollama:
            vm_context = {}
            if arguments.get("vm_name"):
                vm_context = await vm_ops.get_vm_details(
                    arguments["vm_name"],
                    arguments.get("user_role", "viewer")
                )
            return await ollama_integration.troubleshoot_issue(
                arguments["issue_description"],
                vm_context
            )
        
        else:
            raise VMwareMCPException(f"Unknown tool: {name}")
    
    async def start(self):
        """Start the MCP server."""
        logger.info("Starting VMware MCP Server...")
        
        # Initialize connections
        if not await auth_manager.connect():
            raise VMwareMCPException("Failed to connect to VMware")
        
        # Check integrations
        if settings.enable_ollama:
            ollama_healthy = await ollama_integration.health_check()
            logger.info(f"Ollama integration: {'healthy' if ollama_healthy else 'unavailable'}")
        
        if settings.enable_n8n:
            n8n_healthy = await n8n_integration.health_check()
            logger.info(f"n8n integration: {'healthy' if n8n_healthy else 'unavailable'}")
        
        logger.info("VMware MCP Server started successfully")
        return self.server
    
    async def stop(self):
        """Stop the MCP server."""
        logger.info("Stopping VMware MCP Server...")
        
        # Cleanup connections
        await auth_manager.disconnect()
        
        if settings.enable_ollama:
            await ollama_integration.close()
        
        if settings.enable_n8n:
            await n8n_integration.close()
        
        logger.info("VMware MCP Server stopped")


# Global MCP server instance
mcp_server = VMwareMCPServer()
