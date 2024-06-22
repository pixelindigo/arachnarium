from arachnarium.runner import run, run_all

def main(args=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description='Crawler benchmarking framework')

    subparsers = parser.add_subparsers(title='Commands')

    run_cmd = subparsers.add_parser('run', help='run experiment')
    run_cmd.add_argument('-o', '--out',
                         default='experiments/',
                         help='The output dir')
    run_cmd.add_argument('crawler')
    run_cmd.add_argument('app')
    run_cmd.add_argument('args', nargs=argparse.REMAINDER)
    run_cmd.set_defaults(func=run)
    batch_cmd = subparsers.add_parser('batch', help='batch run experiment')
    batch_cmd.add_argument('-o', '--out',
                         default='experiments/',
                         help='The output dir')
    batch_cmd.add_argument('-w', '--workers',
                         default=1,
                         type=int,
                         help='The number of workers')
    batch_cmd.add_argument('-l', '--app-limit',
                         default=-1,
                         type=int,
                         help='How many instances of the same app can run at once')
    batch_cmd.add_argument('file', type=argparse.FileType('r'))
    batch_cmd.set_defaults(func=run_all)

    pargs = parser.parse_args(args)
    pargs.func(pargs)
