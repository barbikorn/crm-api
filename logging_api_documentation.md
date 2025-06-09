# Professional Logging API System

## Overview

This professional logging API system provides comprehensive logging capabilities for your CRM application with three main types of logs:

1. **System Logs** - Application events, errors, and general system activities
2. **Audit Logs** - User actions and data modifications for compliance
3. **API Logs** - HTTP request/response tracking and performance monitoring

## Features

- ✅ **Multi-level logging** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ **Categorized logging** (API, DATABASE, AUTHENTICATION, etc.)
- ✅ **Advanced filtering and search**
- ✅ **Real-time analytics and statistics**
- ✅ **Automatic log cleanup**
- ✅ **Bulk operations**
- ✅ **Export functionality**
- ✅ **Health monitoring**
- ✅ **Decorators for automatic logging**

## API Endpoints

### System Logs

#### Create System Log
```http
POST /api/v1/logs/system
Content-Type: application/json

{
  "level": "INFO",
  "category": "BUSINESS_LOGIC",
  "message": "User login successful",
  "module": "auth",
  "function_name": "login_user",
  "user_id": 123,
  "extra_data": {
    "login_method": "email"
  }
}
```

#### Get System Logs with Filtering
```http
GET /api/v1/logs/system?page=1&size=50&level=ERROR&start_date=2024-01-01T00:00:00Z&search_text=login
```

#### Get Specific System Log
```http
GET /api/v1/logs/system/{log_id}
```

#### Update System Log
```http
PUT /api/v1/logs/system/{log_id}
Content-Type: application/json

{
  "level": "WARNING",
  "extra_data": {
    "updated": true
  }
}
```

#### Delete System Log
```http
DELETE /api/v1/logs/system/{log_id}
```

### Audit Logs

#### Create Audit Log
```http
POST /api/v1/logs/audit
Content-Type: application/json

{
  "user_id": 123,
  "action": "CREATE",
  "resource_type": "Lead",
  "resource_id": "456",
  "new_values": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

#### Get Audit Logs
```http
GET /api/v1/logs/audit?page=1&size=50&user_id=123&action=CREATE&start_date=2024-01-01T00:00:00Z
```

### API Logs

#### Create API Log
```http
POST /api/v1/logs/api
Content-Type: application/json

{
  "request_id": "req_123",
  "method": "POST",
  "endpoint": "/api/v1/leads",
  "status_code": 201,
  "response_time_ms": 150,
  "user_id": 123,
  "query_params": {
    "limit": 10
  }
}
```

#### Get API Logs
```http
GET /api/v1/logs/api?page=1&size=50&endpoint=/api/v1/leads&method=POST&status_code=201
```

### Analytics & Statistics

#### Get Log Statistics
```http
GET /api/v1/logs/statistics?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z
```

Response:
```json
{
  "total_logs": 1500,
  "error_count": 25,
  "warning_count": 100,
  "info_count": 1300,
  "debug_count": 75,
  "critical_count": 0,
  "avg_response_time_ms": 120.5,
  "total_api_calls": 800,
  "error_rate_percentage": 1.67
}
```

#### Get Log Analytics
```http
GET /api/v1/logs/analytics?group_by=hour&start_date=2024-01-01T00:00:00Z
```

Response:
```json
[
  {
    "time_period": "2024-01-01 00:00:00",
    "log_count": 45,
    "error_count": 2,
    "timestamp": "2024-01-01T00:00:00Z"
  }
]
```

### Management Operations

#### Cleanup Old Logs
```http
DELETE /api/v1/logs/cleanup?days_to_keep=30
```

#### Bulk Create System Logs
```http
POST /api/v1/logs/system/bulk
Content-Type: application/json

[
  {
    "level": "INFO",
    "category": "SYSTEM",
    "message": "System startup"
  },
  {
    "level": "INFO", 
    "category": "SYSTEM",
    "message": "Database connected"
  }
]
```

#### Export Logs
```http
GET /api/v1/logs/export?log_type=system&format=json&start_date=2024-01-01T00:00:00Z
```

#### Health Check
```http
GET /api/v1/logs/health
```

## Using the Logging Service

### Manual Logging

```python
from app.core.logging import LoggingService
from app.models.log import LogLevel, LogCategory

# Log a system event
LoggingService.log_system_event(
    db=db,
    level=LogLevel.INFO,
    category=LogCategory.BUSINESS_LOGIC,
    message="Lead created successfully",
    module="lead_service",
    function_name="create_lead",
    user_id=user_id,
    extra_data={"lead_id": lead.id}
)

# Log an audit event
LoggingService.log_audit_event(
    db=db,
    user_id=user_id,
    action="CREATE",
    resource_type="Lead",
    resource_id=str(lead.id),
    new_values=lead_data
)

# Log an API call
LoggingService.log_api_call(
    db=db,
    request_id=request_id,
    method="POST",
    endpoint="/api/v1/leads",
    status_code=201,
    response_time_ms=150,
    user_id=user_id,
    request=request
)
```

### Automatic Logging with Decorators

```python
from app.core.logging import log_function_call, log_audit_action
from app.models.log import LogCategory

@log_function_call(category=LogCategory.BUSINESS_LOGIC, log_args=True)
def create_lead(db: Session, lead: LeadCreate, user_id: int):
    # Function implementation
    return new_lead

@log_audit_action(action="UPDATE", resource_type="Lead")
def update_lead(db: Session, lead_id: int, lead_update: LeadUpdate, user_id: int):
    # Function implementation
    return updated_lead
```

## Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General information about application flow
- **WARNING**: Something unexpected happened but application continues
- **ERROR**: Due to a serious problem, software has not been able to perform function
- **CRITICAL**: Serious error indicating program itself may be unable to continue

## Log Categories

- **API**: HTTP request/response related logs
- **DATABASE**: Database operations and queries
- **AUTHENTICATION**: User authentication and authorization
- **BUSINESS_LOGIC**: Core business operations
- **SYSTEM**: System-level events (startup, shutdown, etc.)
- **SECURITY**: Security-related events and alerts
- **USER_ACTION**: User-initiated actions and interactions

## Query Parameters

### Common Filters
- `page`: Page number (default: 1)
- `size`: Page size (default: 50, max: 100)
- `start_date`: Filter logs after this date (ISO 8601 format)
- `end_date`: Filter logs before this date (ISO 8601 format)

### System Log Filters
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `category`: Log category
- `user_id`: Filter by user ID
- `module`: Filter by module name
- `endpoint`: Filter by API endpoint
- `search_text`: Search in message, module, and function name

### Audit Log Filters
- `user_id`: Filter by user ID
- `action`: Filter by action type
- `resource_type`: Filter by resource type

### API Log Filters
- `endpoint`: Filter by endpoint
- `method`: Filter by HTTP method
- `status_code`: Filter by status code
- `user_id`: Filter by user ID

## Best Practices

1. **Use appropriate log levels** - Reserve ERROR and CRITICAL for actual problems
2. **Include context** - Add user_id, request_id, and relevant data
3. **Don't log sensitive data** - Passwords, tokens, personal information
4. **Use categories consistently** - Choose the most appropriate category
5. **Clean up regularly** - Use the cleanup endpoint to manage storage
6. **Monitor performance** - Watch for high log volumes affecting performance

## Security Considerations

- Authorization headers are automatically masked
- Sensitive data should not be logged in extra_data or messages
- IP addresses and user agents are captured for security auditing
- Audit logs provide compliance tracking for data modifications

## Database Tables

The system creates three main tables:
- `system_logs`: Application and system events
- `audit_logs`: User actions and data changes
- `api_logs`: HTTP request/response tracking

All tables are properly indexed for performance and include timestamps for time-based queries. 