from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    repo_dir: str = os.getenv("REPO_DIR", "./workspace")
    compose_file: str = os.getenv("COMPOSE_FILE", "docker-compose.test.yml")
    webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "change-me")
    port: int = int(os.getenv("PORT", "8080"))
