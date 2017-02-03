def build_grid_job(process,attributes):
    myattrs = attributes.copy()
    myattrs['outds'] = myattrs['outds_template'].format(DSID = myattrs['DSID'])
    pathena_cmd = 'pathena --trf "{}" {}'.format(process['transform'],process['io_options'])
    fmt_pathena = pathena_cmd.format(**myattrs)
    job = {'local_files':[], 'pathena_cmd':fmt_pathena}
    for x in process.get('local_files',[]):
        target,source = x.split(':')
        job['local_files'] += [(target,source.format(**myattrs))]
    return job

import os
import submit_panda
import shutil
def execute_grid_job(environment,context,job):
    fullpathena_cmd = '{} {}'.format(job['pathena_cmd'],environment['extra_options'])
    workdir = context['readwrite'][0]
    for x in job['local_files']:
        shutil.copyfile(x[1],'{}/{}'.format(workdir,x[0]))
    submit_panda.submit_panda(fullpathena_cmd,environment['asetup'],workdir)

def publish_grid_job(publisher,attributes,context):
    outds = attributes['outds_template'].format(DSID = attributes['DSID'])
    return {k: '{}_{}/'.format(outds.rstrip('/'),v) for k,v in dict(x.split(':') for x in publisher['publish']).iteritems()}
