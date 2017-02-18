import celery
import redis


def get_redis_client():
    conf = celery.current_app.conf
    url = conf.get('CUBICWEB_CELERYTASK_REDIS_URL')
    if url:
        return redis.Redis.from_url(url)
