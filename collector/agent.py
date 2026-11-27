
import json
import logging
import time
import urllib.error
import urllib.request

from collector.config import (
    API_URL,
    COLLECTION_INTERVAL,
    SERVER_ID,
    load_agent_key,
)
from collector.metrics import collect_metrics


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("opspulse-agent")


def send_metrics(agent_key: str, metrics: dict) -> None:
    payload = {
        "server_id": SERVER_ID,
        **metrics,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {agent_key}",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status not in (200, 201):
            raise RuntimeError(
                f"Unexpected API status: {response.status}"
            )


def main() -> None:
    agent_key = load_agent_key()

    logger.info("OpsPulse monitoring agent started")
    logger.info("Monitoring server ID: %s", SERVER_ID)
    logger.info("Collection interval: %s seconds", COLLECTION_INTERVAL)

    while True:
        try:
            metrics = collect_metrics()
            send_metrics(agent_key, metrics)

            logger.info(
                "Metrics successfully sent | CPU: %.2f%% | "
                "Memory: %.2f%% | Disk: %.2f%%",
                metrics["cpu_usage"],
                metrics["memory_usage"],
                metrics["disk_usage"],
            )

        except urllib.error.HTTPError as exc:
            logger.error("API rejected metrics: HTTP %s", exc.code)

        except urllib.error.URLError as exc:
            logger.error("API connection failed: %s", exc.reason)

        except Exception:
            logger.exception("Monitoring cycle failed")

        time.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    main()
