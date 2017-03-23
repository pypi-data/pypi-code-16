#!/usr/bin/env python3
"""
Created on Mar 22, 2017

@author: arnon
"""

import os
from projenv.common import get_environ


def get_projname(project, virtual_env, environ):
    prefix=environ.get('PROJENV_PREFIX')
    projname_env="%sPROJ_NAME" % prefix
    projname=environ.get(projname_env)
    if projname is None: raise Exception('ERROR: cannot find %s, "%s" may be invalid projenv' % (projname_env,project,))
    return projname


def get_hook_dir(project, virtual_env):
    default_dir=os.path.join(virtual_env, 'bin', 'projenv')
    projenv_dir=os.environ.get('PROJENV_VIRTUALENV_HOOK_DIR', default_dir)
    os.makedirs(projenv_dir, exist_ok=True)
    return projenv_dir 


def get_hook(project, virtual_env, projname):
    hook_name="projenv_%s.sh" %(projname)
    projenv_dir=get_hook_dir(project, virtual_env)
    result=os.path.join(projenv_dir, hook_name)
    return result


def check_if_exists(project, virtual_env, environ, hook):
    result=False
    if os.path.isfile(hook):
        result= True
    return result


import subprocess as sp

def get_hook_version(project, virtual_env, postactivate):
    ''' get setproj version out of postactivate
    
    source postactivate and run setproj --version
    '''
    cmd="source %s; setproj --version" % postactivate
    try:
        result=sp.check_output([cmd], stderr=sp.STDOUT, shell=True)
        result=result.decode()
    except:
        result=None
    return result
    
    
def  create_postactivate_hook(project, postactivate, version="0.1.0"):
    print("installing postactivate hook.")
    prefix=environ.get('PROJENV_PREFIX')
    hook_str="""
    
setproj() {
    name=$1
    if [[ $name == "--version" ]]; then
        printf "%s"
        return 0
    fi
    
    if [[ -n $PROJENV_NAME ]]; then
         # removing env of previous project
         for e in $(env | grep %s); do
             unset $e
         done
    fi
    
    hook_dir=${PROJENV_VIRTUALENV_HOOK_DIR}
    if [[ -z "$hook_dir" ]]; then
        hook_dir="${VIRTUAL_ENV}/bin/projenv"
    fi

    proj_hook="${hook_dir}/projenv_${name}.sh"
    if [[ ! -f $proj_hook ]]; then
        echo "ERROR: project hook for $name not found: $proj_hook"
        return 1
    fi
    
    export PROJENV_NAME=$name
    
    source export_projenv.sh %s
    
    source $proj_hook
}

unsetproj() {
    if [[ -n $PROJENV_NAME ]]; then
         # removing env of previous project
         for e in $(env | grep %s); do
             unset $(echo $e | cut -d '=' -f 1) 2> /dev/null 
         done
         unset PROJENV_NAME
    fi
}

"""  % (version, prefix, project, prefix)
    
    with open(postactivate, 'a') as f:
        f.write(hook_str)
    

    
def  create_postdeactivate_hook(postdeactivate, ):
    print("installing postdeactivate hook.")
    hook_str="""

typeset -f unsetproj  
if [[ $? -eq 0 ]]; then
    unsetproj
fi

"""  
    
    with open(postdeactivate, 'a') as f:
        f.write(hook_str)
    

def create_project_hook(project, virtual_env, environ, projname, hook):
    prefix=environ.get('PROJENV_PREFIX')
    hook_str="""
cdproj() {{
    if [[ -n $1 ]]; then
        tag=$(echo ${{1}} | tr "[a-z]" "[A-Z]")_
    else 
        tag=""
    fi
    name="{prefix}PROJ_${{tag}}LOC"
    cmd="echo \$$name"
    loc=$($cmd)
    eval cd $loc
}}

cdvar() {{
    if [[ -n $1 ]]; then
        tag=$(echo ${{1}} | tr "[a-z]" "[A-Z]")_
    else 
        tag="VAR_"
    fi
    name="{prefix}${{tag}}LOC"
    cmd="echo \$$name"
    loc=$($cmd)
    eval cd $loc
}}
    """ .format(prefix=prefix)
    
    with open(hook, 'w') as f:
        f.write(hook_str)
    return True
    
def addproj2virtualenv(project, virtual_env, environ):
    projname=get_projname(project=project, virtual_env=virtual_env, environ=environ)
    hook=get_hook(project=project, virtual_env=virtual_env, projname=projname)
    exists=check_if_exists(project=project, virtual_env=virtual_env, environ=environ, hook=hook)
    if exists:
        raise Exception('hook for %s already exits: %s' % (projname, hook))
    postactivate=os.path.join(virtual_env, 'bin', 'postactivate')
    postdeactivate=os.path.join(virtual_env, 'bin', 'postdeactivate')
    if not os.path.isfile(postactivate): 
        raise Exception('cannot find postactivate, virtualenv is invalid: %s' % (virtual_env, ))
    
    hook_version=get_hook_version(project=project, virtual_env=virtual_env, postactivate=postactivate)
    if hook_version is None:
        create_postactivate_hook(postactivate=postactivate, project=project)
        create_postdeactivate_hook(postdeactivate=postdeactivate,)
    else:
        print("found postactivate hook.")
    result=create_project_hook(project=project, virtual_env=virtual_env, environ=environ, projname=projname, hook=hook)
    return result
    
if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()

    parser.add_argument('-p', '--project', type=str, nargs='?', metavar='PATH', default=os.getcwd(),
                        help='path to project location. Root envpackage.xml is expected.  Default: $PWD', )

    args = parser.parse_args()
    
    virtual_env=os.environ.get('VIRTUAL_ENV')
    if virtual_env is None:
        raise Exception("No active virtualenv found. \nMake sure virtualenv is active before running this command.")
    environ=get_environ(args.project, osenv=False)
    status=addproj2virtualenv(project=args.project, virtual_env=virtual_env, environ=environ)
    if status:
        print('project %s added to virtualenv.' % (args.project))
    else:
        raise Exception('project not added to virtual env.')
