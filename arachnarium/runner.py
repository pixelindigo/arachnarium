from arachnarium.app import App
from arachnarium.crawler import Crawler
from arachnarium.experiment import Experiment
from arachnarium.manager import Manager
import asyncio
import logging
import signal
import traceback
import shlex

from rich.logging import RichHandler
logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])

import yaml
from yaml import Loader, Dumper

def run_all(args):
    data = yaml.load(args.file, Loader)
    apps = {}
    crawlers = {}
    for experiment in data['experiments']:
        app = experiment['app']
        crawler = experiment['crawler']
        if app not in apps:
            apps[app] = App(app)
            apps[app].build()
        if crawler not in crawlers:
            crawlers[crawler] = Crawler(crawler)
            crawlers[crawler].build()

    experiments = []
    for experiment in data['experiments']:
        app = apps[experiment['app']]
        crawler = crawlers[experiment['crawler']]
        experiments.append(Experiment(app,
                                      crawler,
                                      shlex.split(experiment['args']),
                                      args.out))

    main_loop(experiments, args.workers, args.app_limit)

def run(args):
    app = App(args.app)
    crawler = Crawler(args.crawler)
    app.build()
    crawler.build()

    main_loop([Experiment(app, crawler, args.args, args.out)],
              1, -1)

def main_loop(experiments, workers, app_limit):
    loop = asyncio.new_event_loop()

    manager = Manager(workers=workers, app_limit=app_limit)

    for experiment in experiments:
        manager.add_experiment(experiment)

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(manager.shutdown()))


    try:
        manager.start(loop)
        loop.run_until_complete(manager.run())
        loop.run_until_complete(manager.shutdown())
        loop.stop()
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        logging.info("Bye!")
