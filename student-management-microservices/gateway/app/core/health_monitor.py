import asyncio
import logging
import httpx
from app.core.service_registry import ServiceRegistry

logging=logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.registry=ServiceRegistry()
        self.status={}
        for name in self.registry.get_services():
            self.status[name]=False
    async def check_service(self,client,service_name,service):
        url=(
            f"http://{service['host']}:{service['port']}"
            f"{service['health']}"
        )
        try:
            response= await client.get(url)
            if response.status_code == 200 :
                self.status[service_name]=True
            else:
                self.status[service_name]=False
        except Exception:
            self.status[service_name]=False
    async def monitor(self):
        while True:
            async with httpx.AsyncClient(timeout=3)as client:
                tasks=[]
                for name ,service in self.repository.get_services().items():
                    tasks.append(self.check_service(client,name,service))
                await asyncio.gather(*tasks)
            await asyncio.sleep(5)
    def is_healthy(self,service):
        return self.status.get(service,False)
    def all_status(self):
        return self.status.copy()
    