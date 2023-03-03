#!/usr/bin/env python3
from flask import Flask, request, send_from_directory, abort, Response, stream_with_context, redirect
from werkzeug.exceptions import NotFound
from os.path import dirname, basename
from problem import check_call_to_file, casename, execcmd, compile, Problem
import generate
from pathlib import Path
from logging import Logger, basicConfig, getLogger, INFO
import shutil
import subprocess
logger = getLogger(__name__)
app = Flask(__name__)

app.errorhandler(NotFound)
def not_found(e):
    return "handling NotFound"
app.route('/test/abort/notfound')
def abort_not_found():
    abort(404)

@app.route("/")
def hello_world():
    return "please access /api/<name><br><a href='/api/sample/aplusb/in/example_00.in'>(example)</a>"

def make_case(problem_name):
    rootdir="."
    if basename(dirname(problem_name)) == 'in':
        make_input(Path(dirname(dirname(problem_name))),basename(problem_name))
    else:
        make_output(Path(dirname(dirname(problem_name))),basename(problem_name))

CHUNK_SIZE = 8192
def read_file_chunks(path):
    with open(path, 'rb') as fd:
        while 1:
            buf = fd.read(CHUNK_SIZE)
            if buf:
                yield buf
            else:
                break

@app.route("/api/<path:problem_name>")
def view(problem_name):
    dl = request.args.get('dl','false')
    commit = request.args.get('commit','master')
    if commit == 'master':
        proc = subprocess.run('git rev-parse master'.split(), stdout = subprocess.PIPE)
        master_hash = proc.stdout.decode("utf8").split()[0]
        if dl=='true':
            return redirect(f'/api/{problem_name}?commit={master_hash}&dl=true')
        else:
            return redirect(f'/api/{problem_name}?commit={master_hash}')
    subprocess.run('git checkout {}'.format(commit).split())
    make_case(problem_name)
    fp = Path(problem_name)
    if fp.exists():
        return stream_with_context(read_file_chunks(fp)), 200, {
            'Content-Disposition': f'attachment; filename={basename(problem_name)}' if dl=='true' else 'inline',
            'Content-Type': 'text/plain; charset=utf-8',
            'Strict-Transport-Security': 'max-age=31536000',
            'Cache-Control': 'public, max-age={}'.format(3600 if commit == 'master' else 86400),
            'Access-Control-Allow-Origin': '*'
        }
    else:
        raise NotFound


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