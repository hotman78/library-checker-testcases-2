#!/usr/bin/env python3
from flask import Flask
from os.path import dirname, basename
from problem import check_call_to_file, casename, execcmd, compile, Problem
from pathlib import Path
from logging import Logger, basicConfig, getLogger, INFO
import shutil

logger = getLogger(__name__)
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "please access /api/<name>"

@app.route("/api/<path:problem_name>")
def main(problem_name):
    rootdir="."
    if basename(dirname(problem_name)) == 'in':
        make_input(Path(dirname(dirname(problem_name))),basename(problem_name))
    else:
        make_output(Path(dirname(dirname(problem_name))),basename(problem_name))
    f = open(problem_name, 'r')
    data = f.read()
    f.close()
    return data, 200, {'Content-Type': 'text/plain; charset=utf-8'}

        
def make_input(basedir, casename):
    prob = Problem(Path('.'), basedir)
    indir = basedir / 'in'
    gendir = basedir / 'gen'

    if indir.exists():
        shutil.rmtree(str(indir))
    indir.mkdir()

    name = casename[0:-6]
    num = int(casename[-5:-3])
    logger.debug(num)
    inpath = indir / casename
    if (gendir / casename).exists():
        gen_path = gendir / (name + '.in' )
    else :
        gen_path = gendir / (name +'.cpp')
        prob.generate_params_h()
        compile(gen_path, Path("."))
    check_call_to_file(execcmd(gen_path, [str(num)]), inpath)

def make_output(basedir, casename):
    make_input(basedir, casename[:-4] + ".in")
    prob = Problem(Path('.'), basedir)
    
    outdir = basedir / 'out'
    soldir = basedir / 'sol'
    indir = basedir / 'in'
    infile = indir / ( casename[:-4] + ".in" )

    logger.info('clear output {}'.format(outdir))

    if outdir.exists():
        shutil.rmtree(str(outdir))
    outdir.mkdir()

    compile(soldir / 'correct.cpp', Path("."))
    expected = outdir / casename
    check_call_to_file(execcmd(soldir / 'correct.cpp'),
                        expected, stdin=open(str(infile), 'r'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)