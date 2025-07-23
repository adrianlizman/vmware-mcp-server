
"""Main entry point for VMware MCP Server."""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from dotenv import load_dotenv
from .config import settings
from .mcp_server import mcp_server
from .exceptions import VMwareMCPException

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

# Configure logging
def setup_logging():
    """Setup logging configuration."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("pyvmomi").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.INFO)


class VMwareMCPApplication:
    """Main application class."""
    
    def __init__(self):
        self.server = None
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the application."""
        try:
            self.logger.info("Initializing VMware MCP Server...")
            self.logger.info(f"Configuration: Host={settings.vmware_host}, Port={settings.mcp_server_port}")
            
            # Start the MCP server
            self.server = await mcp_server.start()
            self.running = True
            
            self.logger.info(f"VMware MCP Server is running on {settings.mcp_server_host}:{settings.mcp_server_port}")
            
            # Keep the server running
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the application."""
        if self.running:
            self.logger.info("Shutting down VMware MCP Server...")
            self.running = False
            
            if self.server:
                await mcp_server.stop()
            
            self.logger.info("VMware MCP Server stopped")
    
    def handle_signal(self, signum, frame):
        """Handle system signals."""
        self.logger.info(f"Received signal {signum}")
        self.running = False


async def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        if not settings.vmware_host:
            raise VMwareMCPException("VMWARE_HOST environment variable is required")
        
        if not settings.vmware_username:
            raise VMwareMCPException("VMWARE_USERNAME environment variable is required")
        
        if not settings.vmware_password:
            raise VMwareMCPException("VMWARE_PASSWORD environment variable is required")
        
        if not settings.secret_key:
            raise VMwareMCPException("SECRET_KEY environment variable is required")
        
        # Create and start application
        app = VMwareMCPApplication()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, app.handle_signal)
        signal.signal(signal.SIGTERM, app.handle_signal)
        
        # Start the application
        await app.start()
        
    except VMwareMCPException as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
