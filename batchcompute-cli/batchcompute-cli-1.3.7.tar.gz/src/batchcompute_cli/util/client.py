from batchcompute import Client
from ..const import IT_MAP
from .config import getConfigs,COMMON
from batchcompute.utils import set_log_level
from . import formater

set_log_level("ERROR")

def _get_endpoint(region):
    domain = 'batchcompute.%s.aliyuncs.com' % region
    Client.register_region(region, domain)
    return domain


def _get_client(opt=None):
    opt = opt or getConfigs(COMMON, ['region', 'accesskeyid','accesskeysecret','version','ssl'])
    if not opt or not opt.get('accesskeyid'):
        raise Exception('You need to login first')

    c = Client(_get_endpoint(opt.get('region')),
        opt.get('accesskeyid'), opt.get('accesskeysecret'),security_conn=not opt.get('ssl'))

    if opt.get('version'):
        c.version = opt.get('version')
    return c

def check_client(opt):
    client = _get_client(opt)
    client.list_jobs("",1)


def list_clusters():
    client = _get_client()
    arr = __list_clusters(client)
    return {'Items':arr,'Marker':''}

def __list_clusters(client, marker='', maxItemCount=100):
    t = []
    result = client.list_clusters(marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_clusters(client,result.NextMarker,maxItemCount)
        t = t + arr
    return t

def get_cluster(cluster_id):
    client = _get_client()
    return client.get_cluster(cluster_id)

def delete_cluster(cluster_id):
    client = _get_client()
    return client.delete_cluster(cluster_id)

def create_cluster(clusterDesc):
    client = _get_client()
    return client.create_cluster(clusterDesc)

def change_cluster_vmcount(cluster_id, groupName, vmCount):
    client = _get_client()
    return client.change_cluster_desired_vm_count(cluster_id, **{groupName: int(vmCount)})




def list_jobs():
    client = _get_client()
    arr = __list_jobs(client)
    return {'Items':arr,'Marker':''}

def __list_jobs(client, marker='', maxItemCount=100):
    t = []
    result = client.list_jobs(marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_jobs(client, result.NextMarker, maxItemCount)
        t = t + arr
    return t




def get_job(job_id):
    client = _get_client()
    return client.get_job(job_id)

def get_job_description(job_id):
    client = _get_client()
    return client.get_job_description(job_id)

def list_tasks(job_id):
    client = _get_client()
    arr = __list_tasks(client, job_id)
    return {'Items':arr,'Marker':''}

def __list_tasks(client,job_id, marker='', maxItemCount=100):
    t = []
    result = client.list_tasks(job_id, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_tasks(client, job_id, result.NextMarker, maxItemCount)
        t = t + arr
    return t



def list_instances(job_id, task_name):
    client = _get_client()
    arr = __list_instances(client, job_id, task_name)
    return {'Items':arr,'Marker':''}

def __list_instances(client, job_id, task_name, marker='', maxItemCount=100):
    t = []
    result = client.list_instances(job_id, task_name, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_instances(client, job_id, task_name, result.NextMarker, maxItemCount)
        t = t + arr
    return t


def get_task(job_id, task_name):
    client = _get_client()
    return client.get_task(job_id, task_name)


def get_instance(job_id, task_name, instance_id):
    client = _get_client()
    return client.get_instance(job_id, task_name, instance_id)




def change_job_priority(job_id, priority):
    client = _get_client()
    return client.change_job_priority(job_id, priority)


def start_job(job_id):
    client = _get_client()
    return client.start_job(job_id)


def stop_job(job_id):
    client = _get_client()
    return client.stop_job(job_id)

def delete_job(job_id):
    client = _get_client()
    return client.delete_job(job_id)

def create_job(jobDesc):
    client = _get_client()
    return client.create_job(jobDesc)

def list_images():
    client = _get_client()

    sysArr = __list_images(client,'',100,type_='System')
    arr = __list_images(client)
    return {'Items': sysArr + arr,'Marker':''}

def __list_images(client, marker='', maxItemCount=100, type_=''):
    t = []
    result = client.list_images(marker, maxItemCount, type_)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_images(client,result.NextMarker,maxItemCount,type_)
        t = t + arr
    return t


def get_image(image_id):
    client = _get_client()
    return client.get_image(image_id)

def delete_image(image_id):
    client = _get_client()
    return client.delete_image(image_id)

def create_image(imageDesc):
    client = _get_client()
    return client.create_image(imageDesc)

def get_quotas():
    client = _get_client()
    return client.get_quotas()

def list_instance_types():
    quotas = get_quotas()
    arr = quotas.AvailableClusterInstanceType
    t=[]
    for n in arr:
        t.append( IT_MAP[n] if IT_MAP.get(n) else {'name':str(n),'cpu': '','memory':''} )
    t = formater.order_by(t, ['cpu','memory'],False)
    return t


def __items2list(items):
    t=[]
    for item in items:
        m = {}
        for k in item.keys():
            m[k] = item.get(k)
        t.append(m)
    return t