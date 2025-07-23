
"""Custom exceptions for VMware MCP Server."""


class VMwareMCPException(Exception):
    """Base exception for VMware MCP Server."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "VMWARE_MCP_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ConnectionError(VMwareMCPException):
    """Raised when connection to VMware fails."""
    
    def __init__(self, message: str = "Failed to connect to VMware", **kwargs):
        super().__init__(message, error_code="CONNECTION_ERROR", **kwargs)


class AuthenticationError(VMwareMCPException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)


class AuthorizationError(VMwareMCPException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, error_code="AUTHZ_ERROR", **kwargs)


class VMOperationError(VMwareMCPException):
    """Raised when VM operations fail."""
    
    def __init__(self, message: str = "VM operation failed", **kwargs):
        super().__init__(message, error_code="VM_OPERATION_ERROR", **kwargs)


class HostOperationError(VMwareMCPException):
    """Raised when host operations fail."""
    
    def __init__(self, message: str = "Host operation failed", **kwargs):
        super().__init__(message, error_code="HOST_OPERATION_ERROR", **kwargs)


class SnapshotOperationError(VMwareMCPException):
    """Raised when snapshot operations fail."""
    
    def __init__(self, message: str = "Snapshot operation failed", **kwargs):
        super().__init__(message, error_code="SNAPSHOT_OPERATION_ERROR", **kwargs)


class ResourceOperationError(VMwareMCPException):
    """Raised when resource operations fail."""
    
    def __init__(self, message: str = "Resource operation failed", **kwargs):
        super().__init__(message, error_code="RESOURCE_OPERATION_ERROR", **kwargs)


class NetworkOperationError(VMwareMCPException):
    """Raised when network operations fail."""
    
    def __init__(self, message: str = "Network operation failed", **kwargs):
        super().__init__(message, error_code="NETWORK_OPERATION_ERROR", **kwargs)


class StorageOperationError(VMwareMCPException):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str = "Storage operation failed", **kwargs):
        super().__init__(message, error_code="STORAGE_OPERATION_ERROR", **kwargs)


class ValidationError(VMwareMCPException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)


class TimeoutError(VMwareMCPException):
    """Raised when operations timeout."""
    
    def __init__(self, message: str = "Operation timed out", **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)


class ConfigurationError(VMwareMCPException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
