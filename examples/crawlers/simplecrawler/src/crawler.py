from urllib.parse import urljoin
import requests
import re
import time
import argparse

RE_HREF = re.compile(r'href="(/\w+)"')

parser = argparse.ArgumentParser(prog='a simple crawler')
parser.add_argument('url')
parser.add_argument('-t', '--timelimit', type=int,
                    help='time limit in minutes',
                    default=5)
parser.add_argument('-n', type=int,
                    help='how many links to visit',
                    default=100)
args = parser.parse_args()

start_time = time.time()

url = args.url
for _ in range(args.n):
    print(f'going to {url}')
    res = requests.get(url, timeout=(5.0, 5.0))
    next_url = RE_HREF.findall(res.text)  
    url = urljoin(args.url, next_url[0])
    time.sleep(5)
    if time.time() - start_time > args.timelimit * 60:
        break
