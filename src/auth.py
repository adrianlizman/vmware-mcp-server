
"""Authentication and authorization module."""

import ssl
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import requests
import urllib3
from vmware.vapi.vsphere.client import create_vsphere_client
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Disable SSL warnings for development (configure properly in production)
if not settings.vmware_verify_ssl:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VMwareAuthManager:
    """Manages VMware vCenter/ESXi authentication and connections."""
    
    def __init__(self):
        self.si: Optional[vim.ServiceInstance] = None
        self.vsphere_client = None
        self.session: Optional[requests.Session] = None
        self._connection_cache: Dict[str, Any] = {}
        
    async def connect(self) -> bool:
        """Establish connection to VMware vCenter/ESXi."""
        try:
            # Create SSL context
            if settings.vmware_verify_ssl:
                context = ssl.create_default_context()
            else:
                context = ssl._create_unverified_context()
            
            # Connect using pyVmomi (SOAP API)
            self.si = SmartConnect(
                host=settings.vmware_host,
                user=settings.vmware_username,
                pwd=settings.vmware_password,
                port=settings.vmware_port,
                sslContext=context
            )
            
            if not self.si:
                logger.error("Failed to connect to VMware host")
                return False
            
            # Create session for REST API
            self.session = requests.Session()
            self.session.verify = settings.vmware_verify_ssl
            
            # Connect using vSphere Automation SDK (REST API)
            self.vsphere_client = create_vsphere_client(
                server=settings.vmware_host,
                username=settings.vmware_username,
                password=settings.vmware_password,
                session=self.session
            )
            
            logger.info(f"Successfully connected to VMware host: {settings.vmware_host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to VMware: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from VMware."""
        try:
            if self.si:
                Disconnect(self.si)
                self.si = None
            
            if self.session:
                self.session.close()
                self.session = None
                
            self.vsphere_client = None
            logger.info("Disconnected from VMware")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
    
    def get_service_instance(self) -> Optional[vim.ServiceInstance]:
        """Get the current service instance."""
        return self.si
    
    def get_vsphere_client(self):
        """Get the vSphere automation client."""
        return self.vsphere_client
    
    async def validate_connection(self) -> bool:
        """Validate the current connection."""
        try:
            if not self.si or not self.vsphere_client:
                return False
            
            # Test SOAP connection
            content = self.si.RetrieveContent()
            if not content:
                return False
            
            # Test REST connection
            try:
                self.vsphere_client.vcenter.VM.list()
                return True
            except Exception:
                return False
                
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False


class JWTManager:
    """Manages JWT tokens for API authentication."""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return None


class RBACManager:
    """Role-Based Access Control manager."""
    
    ROLES = {
        "admin": [
            "vm:create", "vm:delete", "vm:start", "vm:stop", "vm:clone", "vm:migrate",
            "host:add", "host:remove", "host:maintenance", "host:monitor",
            "snapshot:create", "snapshot:delete", "snapshot:revert",
            "resource:allocate", "resource:monitor",
            "network:configure", "storage:configure",
            "system:configure", "system:monitor"
        ],
        "operator": [
            "vm:start", "vm:stop", "vm:clone",
            "snapshot:create", "snapshot:revert",
            "host:monitor", "resource:monitor",
            "system:monitor"
        ],
        "viewer": [
            "vm:list", "host:monitor", "resource:monitor", "system:monitor"
        ]
    }
    
    @classmethod
    def check_permission(cls, user_role: str, required_permission: str) -> bool:
        """Check if a user role has the required permission."""
        if not settings.enable_rbac:
            return True
        
        user_permissions = cls.ROLES.get(user_role, [])
        return required_permission in user_permissions
    
    @classmethod
    def get_user_permissions(cls, user_role: str) -> list:
        """Get all permissions for a user role."""
        return cls.ROLES.get(user_role, [])


# Global auth manager instance
auth_manager = VMwareAuthManager()
