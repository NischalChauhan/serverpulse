
# OpsPulse – REST API Specification

**Project:** OpsPulse  
**API Version:** 1.0.0  
**Base Path:** /api  
**Backend:** Python + FastAPI  
**Authentication:** JWT Bearer Token  
**Status:** Design Phase

---

## 1. Overview

OpsPulse exposes RESTful APIs for server monitoring, user authentication, historical metrics, process information and alert management.

All API responses use JSON.

## 2. API Conventions

### Base URL

Initial local development URL:

`http://localhost:8000`

Production URL will be configured after deployment.

### Authentication

Protected endpoints require:

`Authorization: Bearer <access_token>`

### Standard HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 204 | Request successful, no response body |
| 400 | Bad request |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable |

## 3. Authentication APIs

### POST /api/auth/register

Creates a new user account.

Request:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "StrongPassword123"
}
```

Response – 201:

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

Security:
- Passwords must be securely hashed.
- Registration must not allow users to assign themselves admin privileges.
- Public registration should be disabled or restricted in production.

### POST /api/auth/login

Authenticates a user.

Request:

```json
{
  "username": "admin",
  "password": "StrongPassword123"
}
```

Response – 200:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### GET /api/auth/me

Returns the authenticated user's profile.

Authentication: Required.

Response:

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin"
}
```

## 4. Health API

### GET /api/health

Checks application availability.

Authentication: Not required.

Response – 200:

```json
{
  "status": "healthy",
  "application": "OpsPulse",
  "version": "1.0.0"
}
```

This endpoint should not expose sensitive system information.

## 5. Metrics APIs

### GET /api/metrics

Returns the latest server metrics.

Authentication: Required.

Response:

```json
{
  "cpu": {
    "percent": 35.5
  },
  "memory": {
    "total_bytes": 1073741824,
    "used_bytes": 536870912,
    "percent": 50.0
  },
  "disk": {
    "total_bytes": 21474836480,
    "used_bytes": 4294967296,
    "percent": 20.0
  },
  "network": {
    "bytes_sent": 1024000,
    "bytes_received": 2048000
  },
  "collected_at": "2026-11-23T12:00:00Z"
}
```

### GET /api/metrics/history

Returns historical monitoring data.

Authentication: Required.

Query parameters:

| Parameter | Type | Description |
|---|---|---|
| from | Datetime | Start time |
| to | Datetime | End time |
| interval | String | Aggregation interval |
| limit | Integer | Maximum records |

Response:

```json
{
  "data": [
    {
      "cpu_percent": 35.5,
      "memory_percent": 50.0,
      "disk_percent": 20.0,
      "collected_at": "2026-11-23T12:00:00Z"
    }
  ],
  "pagination": {
    "limit": 100,
    "returned": 1
  }
}
```

## 6. System API

### GET /api/system

Returns system information.

Authentication: Required.

Response:

```json
{
  "hostname": "opspulse-server",
  "operating_system": "Ubuntu",
  "architecture": "x86_64",
  "cpu_cores": 2,
  "uptime_seconds": 86400
}
```

Sensitive infrastructure details must not be exposed to unauthorized users.

## 7. Process API

### GET /api/processes

Returns a list of running processes.

Authentication: Required.

Response:

```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "python3",
      "cpu_percent": 5.2,
      "memory_percent": 2.5,
      "status": "running"
    }
  ]
}
```

Process visibility must follow least-privilege rules.

## 8. Alert APIs

### GET /api/alerts

Returns alert history.

Authentication: Required.

Query parameters:
- status
- severity
- limit
- offset

### POST /api/alerts/rules

Creates an alert rule.

Authentication: Admin or authorized operator.

Request:

```json
{
  "name": "High CPU Usage",
  "metric_name": "cpu_percent",
  "threshold_value": 85,
  "comparison_operator": ">",
  "duration_seconds": 60
}
```

Response – 201:

```json
{
  "id": 1,
  "name": "High CPU Usage",
  "is_enabled": true
}
```

### PATCH /api/alerts/{alert_id}/acknowledge

Acknowledges an alert.

Authentication: Required, with appropriate permission.

### PATCH /api/alerts/{alert_id}/resolve

Resolves an alert.

Authentication: Required, with appropriate permission.

## 9. Error Response Format

All application errors should follow a consistent format.

Example:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Requested resource was not found"
  }
}
```

Validation errors should return HTTP 422 with field-level details.

Sensitive information, passwords, tokens and internal stack traces must never appear in public error responses.

## 10. API Security Requirements

- JWT authentication for protected endpoints.
- Password hashing using a secure password hashing algorithm.
- Role-based authorization.
- Input validation.
- Rate limiting.
- CORS restrictions.
- Parameterized database queries.
- Secure secret management.
- No credentials in API responses.
- HTTPS in production.
- Audit logging for security-sensitive actions.

## 11. Performance Requirements

- Limit historical query results.
- Support pagination.
- Avoid expensive database queries.
- Use database indexes.
- Apply connection pooling.
- Prevent duplicate alert generation.
- Avoid excessive metrics collection.

## 12. API Testing

The API must include tests for:

- Successful authentication.
- Invalid credentials.
- Unauthorized requests.
- Role permissions.
- Metrics retrieval.
- Historical metrics filtering.
- Alert creation.
- Alert acknowledgement.
- Invalid request payloads.
- Database connectivity failures.

## 13. Future API Improvements

- Multiple server registration.
- WebSocket-based live monitoring.
- Alert notifications.
- API key authentication for monitored agents.
- Export metrics to CSV.
- Advanced reporting.
