import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from app.core.service_registry import ServiceRegistry

logger = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.processes: dict[str, subprocess.Popen] = {}

        # gateway/
        self.gateway_root = Path(__file__).resolve().parents[2]

        # student-management/
        self.project_root = self.gateway_root.parent



    def start_all(self):
        services = self.registry.get_services()

        for service_key, service in services.items():

            service_path = (self.project_root / service["path"]).resolve()

            command = [
                sys.executable,
                "-m",
                "uvicorn",
                service["app"],
                "--host",
                service["host"],
                "--port",
                str(service["port"]),
            ]

            logger.info("=" * 80)
            logger.info(f"Starting {service['name']}")
            logger.info(f"Directory : {service_path}")
            logger.info(f"Exists    : {service_path.exists()}")
            logger.info(f"Command   : {' '.join(command)}")

            process = subprocess.Popen(
                command,
                cwd=service_path,
                stdout=sys.stdout,
                stderr=sys.stderr,
                start_new_session=True,
            )
            time.sleep(2)

            if process.poll() is not None:
                stdout, stderr = process.communicate()

                logger.error(f"{service['name']} crashed!")
                logger.error(f"Exit code: {process.returncode}")
                logger.error(stdout)
                logger.error(stderr)
                continue

            logger.info(f"{service['name']} running (PID={process.pid})")

            self.processes[service_key] = process

    def stop_all(self):
        logger.info("Stopping all microservices...")
        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"Stopping {name}")
                try:
                    os.killpg(os.getpgid(process.pid),signal.SIGTERM,)
                except Exception as e:
                    logger.error(e)
        self.processes.clear()

    def is_running(self, service_name: str) -> bool:
        process = self.processes.get(service_name)
        if process is None:
            return False
        return process.poll() is None

    def running_services(self):
        return {name: self.is_running(name) for name in self.processes}

    async def monitor(self):
        while True:
            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    logger.warning(f"{name} stopped unexpectedly.")
            await asyncio.sleep(5)