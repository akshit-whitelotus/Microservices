from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parents[2]


class ServiceRegistry:

    def __init__(self):
        file = BASE_DIR / "app" / "core" / "services.yaml"

        with open(file, "r") as f:
            self.data = yaml.safe_load(f)

    def get_services(self):
        return self.data["services"]

    def get(self, name):
        return self.data["services"][name]