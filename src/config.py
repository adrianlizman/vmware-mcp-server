
"""Configuration management for VMware MCP Server."""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # VMware Configuration
    vmware_host: str = Field(..., env="VMWARE_HOST")
    vmware_username: str = Field(..., env="VMWARE_USERNAME")
    vmware_password: str = Field(..., env="VMWARE_PASSWORD")
    vmware_port: int = Field(443, env="VMWARE_PORT")
    vmware_verify_ssl: bool = Field(False, env="VMWARE_VERIFY_SSL")
    vmware_datacenter: str = Field("Datacenter1", env="VMWARE_DATACENTER")
    
    # MCP Server Configuration
    mcp_server_host: str = Field("0.0.0.0", env="MCP_SERVER_HOST")
    mcp_server_port: int = Field(8080, env="MCP_SERVER_PORT")
    mcp_server_name: str = Field("vmware-mcp-server", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field("1.0.0", env="MCP_SERVER_VERSION")
    
    # Security Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(30, env="JWT_EXPIRE_MINUTES")
    enable_rbac: bool = Field(True, env="ENABLE_RBAC")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")
    log_file: str = Field("/var/log/vmware-mcp-server.log", env="LOG_FILE")
    enable_audit_log: bool = Field(True, env="ENABLE_AUDIT_LOG")
    
    # Ollama Integration
    ollama_host: str = Field("http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field("llama3.2", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(30, env="OLLAMA_TIMEOUT")
    enable_ollama: bool = Field(True, env="ENABLE_OLLAMA")
    
    # n8n Integration
    n8n_webhook_url: str = Field("http://localhost:5678/webhook", env="N8N_WEBHOOK_URL")
    n8n_api_key: Optional[str] = Field(None, env="N8N_API_KEY")
    enable_n8n: bool = Field(True, env="ENABLE_N8N")
    
    # Performance and Limits
    max_concurrent_operations: int = Field(10, env="MAX_CONCURRENT_OPERATIONS")
    operation_timeout: int = Field(300, env="OPERATION_TIMEOUT")
    cache_ttl: int = Field(300, env="CACHE_TTL")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")
    
    # Development Settings
    debug: bool = Field(False, env="DEBUG")
    enable_swagger: bool = Field(True, env="ENABLE_SWAGGER")
    cors_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8080"], 
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
