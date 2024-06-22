# Arachnarium

## Manual installation
`python -m pip install .`

## Usage
Run a single experiment with a web app
`arachnarium run CRAWLER_PATH APP_PATH CRAWLER_ARGS`

Example:
`arachnarium run examples/crawlers/simplecrawler examples/apps/simplewebapp -t 1 http://web/`

Run a single experiment with a website
`arachnarium run CRAWLER_PATH WEBSITE_URL CRAWLER_ARGS`

Example:
`arachnarium run examples/crawlers/simplecrawler https://cispa.de -t 1 -n 5 https://cispa.de`

Run a batch experiment with a website
`arachnarium run -w NUM_WORKERS BATCH_FILE`

Example:
`arachnarium batch -w 4 examples/batch.yml`

Then check `experiments/` directory to see the generated data -- each experiment would be at `/<app>/<crawler>/<id>/` and contain the following dir structure:
- `coverage/` -- code coverage files collected (if applicable)
- `report/` -- crawler's report files
- `command.txt` -- crawler command line arguments
- `runtime.txt` -- time spent on an experiment
- `stderr.txt` -- stderr output
- `stdout.txt` -- stdout output
