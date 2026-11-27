import psutil


def collect_metrics() -> dict:
    """
    Collect CPU, memory, disk, and network metrics
    directly from the EC2 host.
    """

    cpu_usage = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()

    return {
        "cpu_usage": round(cpu_usage, 2),
        "memory_usage": round(memory.percent, 2),
        "disk_usage": round(disk.percent, 2),
        "network_bytes_sent": network.bytes_sent,
        "network_bytes_received": network.bytes_recv,
    }
