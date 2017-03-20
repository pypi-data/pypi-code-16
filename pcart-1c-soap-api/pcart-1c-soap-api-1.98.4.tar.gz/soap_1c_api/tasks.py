from celery import task
# from django.conf import settings


@task(bind=True)
def import_goods(self, xmlfile_id):
    from .lxml_import import import_goods_from_xml
    from .models import XMLFile

    try:
        t = XMLFile.objects.get(pk=xmlfile_id)
        self.update_state(state='PROGRESS')
        result = import_goods_from_xml(None, t.filename, task_instance=self)
        self.update_state(state='SUCCESS')
        return result
    except XMLFile.DoesNotExist as exc:
        raise self.retry(countdown=10, max_retries=2, exc=exc)
