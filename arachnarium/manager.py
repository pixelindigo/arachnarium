from rich.progress import Progress, SpinnerColumn, TextColumn
from enum import Enum
from collections import defaultdict
import asyncio
import logging
import traceback


class Worker:

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.status = 'Initialized' 

    async def run(self, in_queue, out_queue):
        running = True
        self.logger.info(f"started")
        while running:
            self.status = f'Waiting for a new task'
            e = await in_queue.get()
            try:
                self.status = f'Starting {e}'
                await e.start() 
                self.status = f'Running {e}'
                await e.wait()
            except asyncio.CancelledError:
                self.status = f'Terminating {e}'
                await e.terminate()
                running = False
            except Exception:
                logging.error(f"Task failed with exception: {traceback.format_exc()}")
                running = False
            finally:
                self.status = f'Shutting down {e}'
                await e.shutdown()
                in_queue.task_done()
                await out_queue.put(e)
                self.status = f'Done'


class Manager:

    def __init__(self, workers: int, app_limit=-1):
        self.logger = logging.getLogger('Manager')
        # Pending experiments
        self.pending_queue = asyncio.Queue()
        # Completed experiments
        self.done_queue = asyncio.Queue()
        
        # Limits how many instances of an app can be started
        self.app_limit = app_limit
        self.app_count = defaultdict(lambda: app_limit)

        self.experiments = []
        self.tasks = []
        self.workers = []
        for i in range(workers):
            w = Worker(f'worker-{i}')
            self.workers.append(w)

    def _next_experiment(self):
        if len(self.experiments) == 0:
            return None

        if self.app_limit == -1:
            return self.experiments.pop(0)

        for idx, experiment in enumerate(self.experiments):
            if self.app_count[experiment.app.name] > 0:
                self.experiments.pop(idx)
                self.app_count[experiment.app.name] -= 1
                return experiment
        return None
    
    def _release_app_counter(self, app):
        if self.app_limit != -1:
            self.app_count[app.name] += 1

    def start(self, loop):
        for worker in self.workers:
            task = loop.create_task(worker.run(self.pending_queue,
                                               self.done_queue))
            self.tasks.append(task)
        self.producer = loop.create_task(self.produce())
        self.monitor_task = loop.create_task(self.monitor())

    async def produce(self):
        while len(self.experiments) > 0:
            while True:
                next_experiment = self._next_experiment()
                if next_experiment is None:
                    break
                await self.pending_queue.put(next_experiment)
            finished_experiment = await self.done_queue.get()
            self._release_app_counter(finished_experiment.app.name)
            self.done_queue.task_done()

    async def shutdown(self):
        self.logger.info(f"shutting down")

        self.producer.cancel()
        [task.cancel() for task in self.tasks]

        self.logger.info(f"cancelling {len(self.tasks)} outstanding tasks")
        await asyncio.gather(self.producer, *self.tasks, return_exceptions=True)

        self.logger.info(f"stopping monitor")
        self.monitor_task.cancel()
        #await asyncio.gather(self.monitor_task, return_exceptions=True)
        await self.monitor_task
        self.logger.info(f"shutdown complete")

    def add_experiment(self, experiment):
        self.experiments.append(experiment)

    async def run(self):
        await self.pending_queue.join()

    async def monitor(self):
        with Progress(SpinnerColumn(),
                      TextColumn("[progress.description]{task.description}")) as progress:
            p_tasks = []
            for worker in self.workers:
                p_tasks.append((worker, progress.add_task(worker.status)))

            while not progress.finished:
                for worker, task in p_tasks:
                    progress.update(task, description=worker.status)
                await asyncio.sleep(1)
