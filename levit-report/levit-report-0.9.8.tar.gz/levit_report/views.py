import mimetypes
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from zipfile import ZipFile

from django.views.generic.detail import BaseDetailView
from django.utils.translation import activate
from django.http import HttpResponse
from django.conf import settings

from relatorio.templates.opendocument import Template

from .models import Document


class BaseDocumentFileView(BaseDetailView):

    model = Document

    def get_file(self, document, obj_id):
        document.source.open()

        klass = document.content_type.model_class()
        obj = klass.objects.get(pk=obj_id)

        if hasattr(obj, 'print_str'):
          object_name = obj.print_str()
        else:
          object_name = '{}'.format(obj.pk)

        if hasattr(obj, 'output_lang') and obj.output_lang(self.request):
          activate(obj.output_lang(self.request))

        tpl = Template(source=None, filepath=document.source)
        generated = tpl.generate(o=obj).render()

        if document.convert_to is None or document.convert_to == '':
          extension = document.source.path.split('.')[-1]

          output = generated.getvalue()

        else:
          extension = document.convert_to

          import subprocess
          import shlex
          import tempfile
          import os

          input = tempfile.NamedTemporaryFile(delete=False)
          input.write(generated.getvalue())
          input.close()

          command_line = '/usr/bin/loffice --headless --convert-to {} --outdir {} {}'.format(extension, os.path.dirname(input.name), input.name)
          subprocess.call(shlex.split(command_line))

          output_filename = '{}.{}'.format(input.name, extension)
          if document.merge_with_tos and extension == 'pdf':
            final_name = os.path.join('/tmp','{}_{}.{}'.format(document.name, object_name, extension))
            command_line = 'pdfunite {} {} {}'.format(output_filename, settings.TOS_FILE, final_name)
            print(command_line)
            subprocess.call(shlex.split(command_line))
            os.unlink(output_filename)
            output_filename = final_name

          output_stream = open(output_filename, 'rb')
          output = output_stream.read()
          os.unlink(input.name)
          os.unlink(output_filename)


        type = mimetypes.guess_type('brol.{}'.format(extension))

        return output, type[0], object_name, extension


class DocumentFileView(BaseDocumentFileView):

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        obj_id = kwargs.get('object_id')
        output, type, object_name, extension = self.get_file(document, obj_id)
        rv = HttpResponse(output, content_type=type)
        rv['Content-Disposition'] = 'attachment; filename={}_{}.{}'.format(document.name, object_name, extension)

        return rv


class BulkDocumentFileView(BaseDocumentFileView):

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        obj_ids = self.request.GET.getlist('ids[]', [])
        zf = StringIO()
        zip_file = ZipFile(zf, 'w')

        for obj_id in obj_ids:
            output, type, object_name, extension = self.get_file(document, obj_id)
            zip_file.writestr(
                '{}_{}.{}'.format(document.name, object_name, extension),
                output
            )
        zip_file.close()

        type = mimetypes.guess_type('brol.zip')
        rv = HttpResponse(zf.getvalue(), content_type=type[0])
        rv['Content-Disposition'] = 'attachment; filename={}.zip'.format(document.name)

        return rv
