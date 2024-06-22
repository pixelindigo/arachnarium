from pathlib import Path
import subprocess


class Crawler:

    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.name  # could be empty
        self.config = self.path / 'docker-compose.yml'
        if self.config.exists():
            return
        self.config = self.path / 'docker-compose.yaml'
        if self.config.exists():
            return
        raise ValueError(f"No docker-compose.yml/yaml at {self.path}")

    def build(self):
        subprocess.run(['docker-compose',
            '-f', str(self.config),
            'build'],
            env={
                'CRAWLER_DOCKER_DIR': str(self.path.absolute()),
                'CRAWLER_REPORT_DIR': '/tmp/nonexistent',
                },
            check=True)
