from flask import Flask
import os

app = Flask(__name__)

def gen_links(n):
    return '\n'.join(f'<a href="/{os.urandom(32).hex()}"/>' for _ in range(n))


@app.route("/")
def index():
    return gen_links(3) 

@app.route("/<nonce>")
def foobar(nonce):
    return gen_links(3)
