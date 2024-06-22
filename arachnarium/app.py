from pathlib import Path
import subprocess
import os


class App:

    def __init__(self, path):
        if path.startswith('http://') or path.startswith('https://'):
            self.is_docker = False
            self.name = path.replace('://', '-')
            return

        self.is_docker = True
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
        if self.is_docker:
            env = os.environ.copy()
            env.update({
                    'APP_DOCKER_DIR': str(self.path.absolute()),
                    'APP_COVERAGE_DIR': '/tmp/nonexistent',
            })
            subprocess.run(['docker-compose',
                '-f', str(self.config),
                'build'],
                env=env,
                check=True)
