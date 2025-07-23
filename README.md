
# VMware MCP Server

A comprehensive Model Context Protocol (MCP) server for VMware vCenter and ESXi management with production-ready features, Ollama integration, and n8n workflow automation support.

## Features

### Core VMware Operations
- **VM Management**: Create, delete, start, stop, clone, migrate VMs
- **Host Management**: Add/remove hosts, monitor resources, maintenance mode
- **Snapshot Operations**: Create, delete, revert, list snapshots
- **Resource Management**: CPU, memory, storage allocation
- **Network Management**: Virtual switches, port groups, VLANs
- **Storage Management**: Datastores, volumes, disk operations
- **Performance Monitoring**: Real-time metrics and reporting

### Production Features
- **Security**: Certificate-based authentication, RBAC integration
- **Logging**: Comprehensive audit trails and error tracking
- **Error Handling**: Robust exception management and recovery
- **Configuration**: Environment-based settings management
- **Health Monitoring**: Service health checks and diagnostics

### Integrations
- **Ollama**: Local LLM processing for intelligent operations
- **n8n**: Workflow automation and webhook triggers
- **Docker**: Containerized deployment
- **REST API**: OpenAPI/Swagger documentation

## Quick Start

### Prerequisites
- Python 3.9+
- VMware vCenter Server or ESXi host
- Docker (optional)
- Ollama (for AI features)
- n8n (for workflow automation)

### Installation

1. Clone and setup:
```bash
cd ~/vmware-mcp-server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp config/.env.example config/.env
# Edit config/.env with your VMware credentials
```

3. Run the server:
```bash
python -m src.main
```

### Docker Deployment

```bash
docker-compose up -d
```

## Configuration

See `config/.env.example` for all configuration options.

## Documentation

- [Security Guide](SECURITY.md)
- [Integration Guide](docs/integration_guide.md)
- [API Documentation](docs/api.md)

## License

MIT License - see LICENSE file for details.
