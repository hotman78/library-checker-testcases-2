#!/usr/bin/env python3
from flask import Flask, request, send_from_directory, abort, Response, stream_with_context
from werkzeug.exceptions import NotFound
from os.path import dirname, basename
from problem import check_call_to_file, casename, execcmd, compile, Problem
import generate
from pathlib import Path
from logging import Logger, basicConfig, getLogger, INFO
import shutil

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
    return "please access /api/<name>"

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

@app.route("/api/view/<path:problem_name>")
def view(problem_name):
    make_case(problem_name)
    fp = Path(problem_name)
    if fp.exists():
        return stream_with_context(read_file_chunks(fp)), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        raise NotFound

@app.route("/api/dl/<path:problem_name>")
def download(problem_name):
    make_case(problem_name)
    fp = Path(problem_name)
    if fp.exists():
        return stream_with_context(read_file_chunks(fp)), 200, {'Content-Disposition': f'attachment; filename={basename(problem_name)}','Content-Type': 'text/plain; charset=utf-8'}
    else:
        raise NotFound

@app.route("/api/dlall/<path:problem_name>")
def all_download(problem_name):
    generate.main(['-p', problem_name])
    output = Path(problem_name) / basename(problem_name)
    build = Path('./build')
    if build.exists():
        shutil.rmtree(str(build))
    build.mkdir()
    if output.exists():
        shutil.rmtree(str(output))
    output.mkdir()
    shutil.move( Path(problem_name) / 'in', output / 'in' )
    shutil.move( Path(problem_name) / 'out', output / 'out' )

    shutil.make_archive( build / basename(problem_name) , 'zip', root_dir=output )
    fp = build / ( basename(problem_name) + '.zip' )
    filename = basename(problem_name)+'.zip'
    if fp.exists():
        return stream_with_context(read_file_chunks(fp)), 200, {'Content-Disposition': f'attachment; filename={filename}','Content-Type': 'text/plain; charset=utf-8'}
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