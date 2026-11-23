
# OpsPulse – Security Architecture

**Project:** OpsPulse  
**Version:** 1.0.0  
**Status:** Design Phase  
**Environment:** AWS EC2 – Ubuntu 24.04 LTS

---

## 1. Security Overview

OpsPulse follows a defense-in-depth security approach.

Security controls will protect:
- User accounts and authentication.
- Application APIs.
- Monitoring data.
- Database credentials.
- Docker containers.
- Host-level metrics collection.
- Infrastructure access.

## 2. Authentication

JWT-based authentication will be used.

Requirements:
- Authenticate users before accessing protected endpoints.
- Use short-lived access tokens.
- Validate token signature and expiration.
- Reject invalid or expired tokens.
- Never store passwords in plaintext.
- Do not expose authentication tokens in application logs.

## 3. Password Security

Passwords must be hashed using Argon2id or another appropriately configured modern password hashing algorithm.

Requirements:
- Never store plaintext passwords.
- Never log passwords.
- Validate password strength.
- Use secure password verification.
- Apply rate limiting to login attempts.

## 4. Role-Based Access Control

OpsPulse will initially support three roles.

| Role | Permissions |
|---|---|
| Admin | Full application administration |
| Operator | Monitoring and alert management |
| Viewer | Read-only monitoring access |

Authorization must be enforced on the backend, not only in the frontend.

Users must not be able to assign themselves administrator privileges.

## 5. Secrets Management

Sensitive configuration includes:
- Database passwords.
- JWT signing keys.
- Application secrets.
- Database connection strings.

Requirements:
- Keep `.env` files outside Git.
- Maintain `.env.example` without real credentials.
- Use strong randomly generated secrets.
- Restrict secret file permissions.
- Rotate credentials when necessary.
- Never print secrets in terminal logs or CI/CD output.

## 6. API Security

- Validate all incoming requests.
- Apply authentication to protected endpoints.
- Enforce role-based permissions.
- Implement rate limiting.
- Restrict CORS origins.
- Use parameterized SQL queries.
- Return safe error messages.
- Avoid exposing internal stack traces.
- Use HTTPS in production.

## 7. Database Security

PostgreSQL security requirements:

- No public exposure of port 5432.
- Dedicated application database user.
- Strong database credentials.
- Least-privilege permissions.
- Internal Docker networking.
- Secure backups.
- Restricted database administration.

The application database user must not have unnecessary superuser privileges.

## 8. Docker Security

- Avoid privileged containers.
- Run containers as non-root users where practical.
- Do not mount the Docker socket.
- Expose only required ports.
- Use trusted base images.
- Pin image versions.
- Apply dependency updates.
- Restrict Linux capabilities.
- Keep database storage persistent.
- Avoid storing secrets in Docker image layers.

## 9. Host Metrics Collector Security

The metrics collector requires access to host-level system metrics.

Requirements:
- Run under a dedicated unprivileged Linux user.
- Avoid unrestricted root execution.
- Avoid privileged Docker containers.
- Expose only the required metrics interface.
- Restrict communication to the OpsPulse backend.
- Do not expose sensitive process information to unauthorized users.

The collector must not allow remote users to execute arbitrary host commands.

## 10. AWS Infrastructure Security

EC2 Security Group requirements:

| Protocol | Port | Access |
|---|---|---|
| SSH | 22 | Administrator IP only |
| HTTP | 80 | Public when required |
| HTTPS | 443 | Public when required |

Additional requirements:
- Do not expose PostgreSQL port 5432.
- Do not expose FastAPI port 8000 publicly.
- Restrict SSH access.
- Protect the private SSH key.
- Review security group rules periodically.
- Use IAM roles with least privilege when AWS API access is needed.

## 11. Audit Logging

Security-sensitive activities must be recorded.

Examples:
- Successful login.
- Failed login.
- User creation.
- Role changes.
- Alert rule modifications.
- Security configuration changes.

Requirements:
- Never log passwords or tokens.
- Record timestamps.
- Record relevant user and action information.
- Restrict access to audit logs.
- Keep audit records append-only for application users.

## 12. Backup Security

- Protect database backups.
- Restrict backup file permissions.
- Avoid committing backups to Git.
- Keep backup credentials secure.
- Verify backup integrity.
- Test restoration procedures.
- Define a retention policy.

## 13. Security Testing

Testing must include:

- Invalid authentication attempts.
- Expired JWT tokens.
- Unauthorized API requests.
- Role permission violations.
- SQL injection testing.
- Input validation testing.
- Rate limiting.
- Container security inspection.
- Secret exposure checks.
- Database access restrictions.

## 14. Incident Response

If a security incident occurs:

1. Identify the affected component.
2. Restrict compromised access.
3. Rotate affected credentials.
4. Preserve relevant logs.
5. Restore from verified backups if necessary.
6. Document the incident.
7. Apply corrective measures.

## 15. Security Principles

OpsPulse will follow:

- Least privilege.
- Defense in depth.
- Secure defaults.
- Data minimization.
- Separation of responsibilities.
- Regular security updates.
- Controlled access.
- Secure recovery procedures.

## 16. Future Security Improvements

- Multi-factor authentication.
- Centralized security monitoring.
- Automated vulnerability scanning.
- Advanced audit reporting.
- External secrets management.
- Multiple administrator approval for sensitive operations.
