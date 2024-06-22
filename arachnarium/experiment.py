from pathlib import Path
from importlib.resources import files, as_file
import asyncio
import uuid
import logging
import time
import subprocess
import os


class Experiment:

    def __init__(self, app, crawler, crawler_args, out):
        self.id = str(uuid.uuid4()) 
        self.logger = logging.getLogger(self.id)

        self.app = app
        self.crawler = crawler
        self.crawler_args = crawler_args

        self.time_start = 0

        # init directories        
        self.out = Path(out) / self.app.name / self.crawler.name / self.id
        self.coverage_dir = self.out / 'coverage'
        self.report_dir = self.out / 'report'
        self.coverage_dir.mkdir(parents=True, exist_ok=False)
        self.report_dir.mkdir(parents=True, exist_ok=False)

        # otherwise the webapp can't write the files
        self.coverage_dir.chmod(0o777)

        with open(self.out / 'command.txt', 'w') as f:
            f.write(' '.join(crawler_args))

    def __repr__(self):
        return f'Experiment {self.id}: ({self.crawler.name}, {self.app.name}) {self.crawler_args}'

    async def start(self):
        self.logger.info(f'running experiment with args {self.crawler_args}')
        self.time_start = time.time()
        docker_env = os.environ.copy()

        with open(self.out / 'stdout.txt', 'w') as stdout, \
             open(self.out / 'stderr.txt', 'w') as stderr, \
             as_file(files('arachnarium').joinpath(
                'resources/docker-compose.base.yml')) as base_config:
                if self.app.is_docker:
                    docker_cmd = ['docker-compose', '-p', self.id,
                        '-f', str(self.app.config),
                        '-f', str(base_config),
                        '-f', str(self.crawler.config),
                        'run',
                        '--rm', 'crawler'] + self.crawler_args
                    docker_env.update({
                        'APP_DOCKER_DIR': str(self.app.path.absolute()),
                        'CRAWLER_DOCKER_DIR': str(self.crawler.path.absolute()),
                        'APP_COVERAGE_DIR': str(self.coverage_dir.absolute()),
                        'CRAWLER_REPORT_DIR': str(self.report_dir.absolute()),
                        'EXPERIMENT_ID': self.id
                    })
                else:
                    docker_cmd = ['docker-compose', '-p', self.id,
                        '-f', str(self.crawler.config),
                        'run',
                        '--rm', 'crawler'] + self.crawler_args
                    docker_env.update({
                        'CRAWLER_DOCKER_DIR': str(self.crawler.path.absolute()),
                        'CRAWLER_REPORT_DIR': str(self.report_dir.absolute()),
                        'EXPERIMENT_ID': self.id
                    })
                self.process = await asyncio.create_subprocess_exec(
                    *docker_cmd,
                    env=docker_env,
                    stdout=stdout,
                    stderr=stderr)

    async def terminate(self):
        self.logger.info('terminating')
        await self.process.terminate()
        self.logger.info('terminated')
        await self.shutdown()
    
    async def wait(self):
        await self.process.wait()

    async def shutdown(self):
        self.logger.info('shutting down')
        self.process = await asyncio.create_subprocess_exec(
                *['docker-compose', '-p', self.id,
                'down', '-v'],
                stdout=subprocess.DEVNULL,  # maybe we need a debug mode in which we log the shutdown 
                stderr=subprocess.DEVNULL,
                )
        await self.process.wait()
        with open(self.out / 'runtime.txt', 'w') as f:
            f.write(str(time.time() - self.time_start))
        self.logger.info('shutdown complete')
