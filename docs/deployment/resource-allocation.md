
# OpsPulse – EC2 Resource Allocation & Performance Plan

**Project:** OpsPulse  
**Version:** 1.0.0  
**Cloud:** AWS EC2 – US East (Ohio)  
**Operating System:** Ubuntu 24.04 LTS  
**Status:** Design Phase

---

## 1. EC2 Infrastructure

Current server specifications:

| Resource | Available |
|---|---|
| vCPU | 2 |
| RAM | Approximately 909 MiB |
| Root Storage | 19 GB available filesystem capacity |
| Operating System | Ubuntu 24.04.5 LTS |

## 2. Resource Management Objectives

- Keep the application operational on a low-memory EC2 instance.
- Prevent excessive memory consumption.
- Avoid unnecessary background services.
- Monitor CPU, RAM and disk utilization.
- Maintain sufficient memory for Ubuntu.
- Avoid unexpected out-of-memory failures.

## 3. Memory Allocation Strategy

Initial estimated memory targets:

| Component | Planning Target |
|---|---:|
| Ubuntu and system services | 350–450 MiB |
| Docker daemon | Included in system overhead |
| PostgreSQL | 100–150 MiB |
| FastAPI | 80–120 MiB |
| Nginx | 15–30 MiB |
| Remaining memory | Safety headroom |

These are provisional targets, not guaranteed limits.

Actual memory consumption must be measured before configuring container limits.

## 4. CPU Management

The EC2 instance provides two vCPUs.

Requirements:
- Start FastAPI with one worker.
- Avoid unnecessary background processes.
- Keep metric collection intervals configurable.
- Avoid CPU-intensive database queries.
- Monitor CPU utilization during testing.

## 5. Swap Strategy

Evaluate a small swap allocation if required.

Requirements:
- Measure memory pressure first.
- Consider 1 GB swap as a fallback.
- Monitor swap usage.
- Do not treat swap as a replacement for physical RAM.
- Avoid excessive swapping.

## 6. Disk Management

The root filesystem provides approximately 19 GB of capacity.

Monitor:
- Docker image storage.
- Container writable layers.
- PostgreSQL database growth.
- Application logs.
- Backup files.
- Operating system updates.

Requirements:
- Remove unused Docker images carefully.
- Configure log rotation.
- Apply database retention policies.
- Avoid storing unnecessary build artifacts on EC2.

## 7. PostgreSQL Optimization

Initial configuration should prioritize low memory usage.

Requirements:
- Conservative shared buffer allocation.
- Limited maximum connections.
- Appropriate work memory.
- Controlled maintenance operations.
- Regular database cleanup.
- Monitor database size.

Final PostgreSQL settings must be selected after deployment testing.

## 8. Application Optimization

Backend:
- One initial API worker.
- Efficient database queries.
- Connection pooling.
- Avoid unnecessary background tasks.

Frontend:
- Build React into static assets.
- Do not run the development server in production.
- Serve assets through Nginx.

Nginx:
- Lightweight reverse proxy.
- Static asset caching.
- Controlled worker configuration.

## 9. Docker Resource Monitoring

Monitor:

- Container memory consumption.
- Container CPU usage.
- Container restarts.
- Container health.
- Docker storage usage.

Use Docker resource reporting during validation.

## 10. Performance Testing

Test scenarios:

1. Normal dashboard usage.
2. Repeated metrics requests.
3. Historical metrics queries.
4. Database insert operations.
5. Multiple concurrent users.
6. Container restart.
7. EC2 reboot and recovery.

Record CPU, memory and response times.

## 11. Alert Thresholds

Initial application monitoring targets:

| Metric | Warning | Critical |
|---|---:|---:|
| CPU usage | 70% | 90% |
| Memory usage | 75% | 90% |
| Disk usage | 75% | 90% |

Thresholds must be configurable.

## 12. Upgrade Criteria

Consider increasing EC2 resources when:

- Memory remains consistently above 85%.
- Swap usage becomes persistent.
- CPU utilization remains high.
- Application response times deteriorate.
- Database workload increases significantly.

A 4 GB RAM instance is a potential future upgrade target.

## 13. Cost Optimization

- Use existing AWS credits.
- Avoid unnecessary managed services.
- Stop unused development instances.
- Monitor EBS storage.
- Review Elastic IP usage.
- Monitor AWS billing and credit consumption.

## 14. Operational Maintenance

- Review system memory.
- Review disk usage.
- Monitor Docker health.
- Verify database backups.
- Review application logs.
- Apply security updates.
- Test recovery procedures.

## 15. Success Criteria

OpsPulse should:

- Run reliably on the initial EC2 instance.
- Preserve database data across container restarts.
- Collect host-level metrics accurately.
- Avoid uncontrolled memory consumption.
- Recover after service failures.
- Support future infrastructure upgrades.
