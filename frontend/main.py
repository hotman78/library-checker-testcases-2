#!/usr/bin/env python3

from re import A
from jinja2 import Template, Environment, FileSystemLoader
import subprocess
import shutil
from pathlib import Path
import toml
import json
import sys
import os

params = {'problems':{}}
env = Environment(loader=FileSystemLoader('frontend', encoding='utf8'))
is_local = "--local" in sys.argv

def make_problem_page(category,name):
    params['problems'].setdefault(category,[])
    params['problems'][category].append(name)
    path=category+"/"+name
    problem_params={"dir":"{0}".format(path),"testcases":[]}
    tomls=toml.load("./library-checker-problems/{0}/info.toml".format(path))
    for cases in tomls["tests"]:
        casename='.'.join(cases["name"].split('.')[:-1])
        for i in range(0,int(cases["number"])):
            problem_params["testcases"].append("{:s}_{:02d}".format(casename,i))
    tmpl = env.get_template('templates/problem.html')
    if not Path("build/{}".format(category)).exists():
        os.makedirs("build/{}".format(category))
    with open('build/{0}.html'.format(path), 'w') as f:
        f.write(tmpl.render(problem_params))

def make_toppage():
    tmpl = env.get_template('templates/index.html')
    with open('build/index.html', 'w') as f:
        f.write(tmpl.render(params))

# def dump_hashlist():
#     with open('.cache.json','w') as f:
#         json.dump(hashlist, f, indent=4)

# def no_diff(preSHA,SHA,path):
#     res=subprocess.run("git diff {} {} --name-only  --relative={}".format(preSHA,SHA,path),shell=True,cwd="./library-checker-problems",stdout=subprocess.PIPE).stdout.decode()
#     return res==''

def test():
    make_problem_page("graph","tree_diameter")
    make_problem_page("datastructure","unionfind")
    make_problem_page("datastructure","associative_array")
    make_toppage()

def main():
    tomls = list(filter(lambda p: not p.match('test/**/info.toml'),
                            Path('.').glob('**/info.toml')))
    tomls = sorted(tomls, key=lambda x: x.parent.name)
    for x in tomls:
        problem=x.parent
        make_problem_page(problem.parent.name,problem.name)
    make_toppage()

if __name__ == '__main__':
    if is_local:test()
    else:main()

