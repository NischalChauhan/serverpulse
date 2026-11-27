import psutil

from app.schemas.metrics import MetricSnapshotCreate


def collect_system_metrics(server_id: int) -> MetricSnapshotCreate:
    """
    Collect system resource metrics.

    Note: When executed inside Docker, psutil reports
    container-visible resource information, not necessarily
    the complete EC2 host metrics.
    """

    cpu_usage = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    network = psutil.net_io_counters()

    return MetricSnapshotCreate(
        server_id=server_id,
        cpu_usage=cpu_usage,
        memory_usage=memory.percent,
        disk_usage=disk.percent,
        network_bytes_sent=network.bytes_sent,
        network_bytes_received=network.bytes_recv,
    )
