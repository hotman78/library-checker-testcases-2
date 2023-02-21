#!/usr/bin/env python3
from flask import Flask
from os.path import dirname
import generate


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "please access /api/<name>"

@app.route("/api/<path:problem>")
def main(problem):
    generate.main(["-p", dirname(dirname(problem))] )
    f = open(problem, 'r')
    data = f.read()
    f.close()
    return data, 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)