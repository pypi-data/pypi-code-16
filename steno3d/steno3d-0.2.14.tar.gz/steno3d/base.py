"""resource.py contains the base resource classes that user-created
resources depend on in steno3d
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
from pprint import pformat
from six import string_types

from traitlets import All, observe, Undefined, validate

from .client import Comms, needs_login, pause, plot
from .traits import (_REGISTRY, HasSteno3DTraits, KeywordInstance, Repeated,
                     String)


class classproperty(property):
    """class decorator to enable property behavior in classmethods"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class UserContent(HasSteno3DTraits):
    """Base class for everything user creates and uploads in steno3d"""
    title = String(
        help='Title of the model.',
        default_value='',
        allow_none=True
    )
    description = String(
        help='Description of the model.',
        default_value='',
        allow_none=True
    )
    _sync = False
    _upload_data = None

    @classproperty
    @classmethod
    def _resource_class(cls):
        """name of the class of resource"""
        if getattr(cls, '__resource_class', None) is None:
            cls.__resource_class = cls.__name__.lower()
        return cls.__resource_class

    @classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/{className}'.format(
                className=cls._resource_class
            )
        return cls.__model_api_location

    def _upload(self, sync=False, verbose=True, tab_level=''):
        if getattr(self, '_uploading', False):
            return
        try:
            if verbose:
                print(
                    tab_level + ('Uploading '
                                 if getattr(self, '_upload_data', None) is None
                                 else 'Updating ') +
                    self._resource_class + ': ' + self.title
                )
            self._uploading = True
            pause()
            assert self.validate()
            self._upload_dirty(sync, verbose, tab_level + '    ')
            if getattr(self, '_upload_data', None) is None:
                self._post(
                    self._get_dirty_data(force=True),
                    self._get_dirty_files(force=True)
                )
            else:
                dirty_data = self._get_dirty_data()
                dirty_files = self._get_dirty_files()
                if len(dirty_data) > 0 or len(dirty_files) > 0:
                    self._put(dirty_data, dirty_files)
            self._mark_clean(recurse=False)
            self._sync = sync
            if verbose:
                print(tab_level + '... Complete!')
        except Exception as err:
            if self._sync:
                print('Upload failed, turning off syncing. To restart '
                      'syncing, upload() again.')
                self._sync = False
            else:
                raise err
        finally:
            self._uploading = False

    def _get_dirty_data(self, force=False):
        dirty = self._dirty_traits
        datadict = dict()
        if 'title' in dirty or force:
            datadict['title'] = self.title
        if 'description' in dirty or force:
            datadict['description'] = self.description
        return datadict

    def _get_dirty_files(self, force=False):
        return {}

    def _upload_dirty(self, sync=False, verbose=True, tab_level=''):
        pass

    @observe(All)
    def _on_property_change(self, change):
        if getattr(self, '_sync', False):
            self._upload(self._sync)

    def _post(self, datadict=None, files=None):
        self._client_upload(Comms.post, 'api/' + self._model_api_location,
                            datadict, files)

    def _put(self, datadict=None, files=None):
        pause()
        api_uid = 'api/{mapi}/{uid}'.format(mapi=self._model_api_location,
                                            uid=self._upload_data['uid'])
        self._client_upload(Comms.put, api_uid, datadict, files)

    def _client_upload(self, request_fcn, url,
                       datadict=None, files=None):
        req = request_fcn(
            url,
            data=datadict if datadict else tuple(),
            files=files if files else tuple(),
        )
        if isinstance(req, list):
            for rq in req:
                if rq['status_code'] != 200:
                    try:
                        resp = pformat(rq['json'])
                    except ValueError:
                        resp = rq

                    raise Exception(
                        'Upload failed: {location}'.format(
                            location=url,
                        ) +
                        '\ndata: {datadict}\nfiles: {filedict}'.format(
                            datadict=pformat(datadict),
                            filedict=pformat(files),
                        ) +
                        '\nresponse: {response}'.format(
                            response=resp,
                        )
                    )
            self._upload_data = [rq['json'] for rq in req]
        else:
            if req['status_code'] != 200:
                raise Exception(
                    'Upload failed: {location}'.format(
                        location=url,
                    ) +
                    '\ndata: {datadict}\nfiles: {filedict}'.format(
                        datadict=pformat(datadict),
                        filedict=pformat(files),
                    ) +
                    '\nresponse: {response}'.format(
                        response=req['json'],
                    )
                )
            self._upload_data = req['json']

    @property
    def _json(self):
        """Return a JSON representation of the object"""
        json = getattr(self, '_upload_data', None)
        if json is None:
            raise ValueError('JSON not available: Data not uploaded')
        return json

    @classmethod
    def _json_from_uid(cls, uid):
        if not isinstance(uid, string_types) or len(uid) != 20:
            raise ValueError('{}: invalid uid'.format(uid))
        resp = Comms.get('api/{mapi}/{uid}'.format(
            mapi=cls._model_api_location,
            uid=uid
        ))
        if resp['status_code'] != 200:
            raise ValueError('{uid}: {cls} query failed'.format(
                uid=uid,
                cls=cls._resource_class
            ))
        return resp['json']

    @classmethod
    def _build(cls, src, copy=True, tab_level='', **kwargs):
        if isinstance(src, HasSteno3DTraits):
            raise NotImplementedError('Copying instances not supported')
        print('{tl}Downloading {cls}'.format(
            tl=tab_level,
            cls=cls._resource_class
        ), end=': ')
        if isinstance(src, string_types):
            json = cls._json_from_uid(src)
        else:
            json = src
        title = '' if json['title'] is None else json['title']
        desc = '' if json['description'] is None else json['description']
        print(title)
        res = cls._build_from_json(json, copy=copy, tab_level=tab_level,
                                   title=title, description=desc, **kwargs)
        if not copy:
            res._upload_data = json
        print('{}...Complete!'.format(tab_level))
        return res

    @classmethod
    def _build_from_json(cls, json, copy=True, tab_level='', **kwargs):
        raise NotImplementedError('Cannot build raw UserContent from json')


class BaseResource(UserContent):
    """Base class for all resources that are added to projects and
    uploaded to steno3d
    """

    def _get_dirty_data(self, force=False):
        datadict = super(BaseResource, self)._get_dirty_data(force)
        dirty = self._dirty
        if 'opts' in dirty or (force and hasattr(self, 'opts')):
            datadict['meta'] = self.opts._json
        return datadict


    def _validate_file_size(self, name, arr):
        if Comms.user.logged_in:
            file_limit = Comms.user.file_size_limit
            if self._nbytes(arr) > file_limit:
                raise ValueError(
                    '{name} file size ({file} bytes) exceeds limit: '
                    '{lim} bytes'.format(name=name,
                                         file=self._nbytes(arr),
                                         lim=file_limit)
                )
        return True


class CompositeResource(BaseResource):
    """A composite resource that stores references to lower-level objects."""
    project = Repeated(
        help='Project',
        trait=KeywordInstance(klass='Project')
    )

    def __init__(self, project=None, **kwargs):
        if project is None:
            raise TypeError('Resource must be constructed with its '
                            'containing project(s)')
        super(CompositeResource, self).__init__(**kwargs)
        self.project = project

    @classmethod
    def _url_view_from_uid(cls, uid):
        """Get full url from a uid"""
        url = '{base}{mapi}/{uid}'.format(
            base=Comms.base_url,
            mapi=cls._model_api_location,
            uid=uid)
        return url

    @validate('project')
    def _validate_proj(self, proposal):
        for proj in proposal['value']:
            if self not in proj.resources:
                raise ValueError('Project/resource pointers misaligned: '
                                 'Ensure that projects contain all the '
                                 'resources that point to them.')
        return True

    @needs_login
    def upload(self, sync=False, verbose=True, print_url=True):
        """Upload the resource through its containing project(s)"""
        for proj in self.project:
            proj.upload(sync, verbose, False)
        if print_url:
            print(self._url)
        return self._url



    def _get_dirty_data(self, force=False):
        datadict = super(CompositeResource, self)._get_dirty_data(force)
        dirty = self._dirty_traits
        if 'mesh' in dirty or force:
            datadict['mesh'] = dumps({
                'uid': self.mesh._json['longUid']
            })
        if 'data' in dirty or force:
            datadict['data'] = dumps([
                {
                    'location': d.location,
                    'uid': d.data._json['longUid']
                } for d in self.data
            ])
        if 'textures' in dirty or (force and hasattr(self, 'textures')):
            datadict['textures'] = dumps([
                {
                    'uid': t._json['longUid']
                } for t in self.textures
            ])
        return datadict

    def _upload_dirty(self, sync=False, verbose=True, tab_level=''):
        dirty = self._dirty
        if 'mesh' in dirty:
            self.mesh._upload(sync, verbose, tab_level)
        if 'data' in dirty:
            [d.data._upload(sync, verbose, tab_level) for d in self.data]
        if 'textures' in dirty:
            [t._upload(sync, verbose, tab_level) for t in self.textures]

    @observe('project')
    def _fix_proj_res(self, change):
        before = change['old']
        after = change['new']
        if before in (None, Undefined):
            before = []
        if after in (None, Undefined):
            after = []
        for proj in after:
            if proj not in before and self not in proj.resources:
                proj.resources += [self]
        for proj in before:
            if proj not in after and self in proj.resources:
                proj.resources = [r for r in proj.resources
                                  if r is not self]
        if len(set(after)) != len(after):
            post_post = []
            for p in after:
                if p not in post_post:
                    post_post += [p]
            self.project = post_post

    @property
    def _url(self):
        if getattr(self, '_upload_data', None) is not None:
            return self._url_view_from_uid(self._upload_data['uid'])

    @property
    @needs_login
    def url(self):
        """steno3d.com url of project if uploaded"""
        if getattr(self, '_upload_data', None) is None:
            print('Resource not uploaded: Please upload() '
                  'before accessing the URL.')
        return self._url

    @needs_login
    def plot(self):
        """Display the 3D representation of the content"""
        if getattr(self, '_upload_data', None) is None:
            print('Resource not uploaded: Please upload() '
                  'before plotting.')
            return
        return plot(self._url)

    @classmethod
    def _build_from_json(cls, json, copy=True, tab_level='', **kwargs):
        if 'project' not in kwargs:
            raise KeyError('Building CompositeResource from json requires '
                           'project input.')
        res = cls(
            project=kwargs['project'],
            title=kwargs['title'],
            description=kwargs['description'],
            opts=json['meta']
        )
        (mesh_string, mesh_uid) = (
            json['mesh']['uid'].split('Resource')[-1].split(':')
        )
        mesh_class = _REGISTRY[mesh_string]

        res.mesh = mesh_class._build(mesh_uid, copy, tab_level + '    ')

        if 'textures' in json:
            res.textures = []
            for t in json['textures']:
                (tex_string, tex_uid) = (
                    t['uid'].split('Resource')[-1].split(':')
                )
                tex_class = _REGISTRY[tex_string]
                res.textures += [tex_class._build(
                    tex_uid, copy, tab_level + '    '
                )]

        if 'data' in json:
            res.data = []
            for d in json['data']:
                (data_string, data_uid) = (
                    d['uid'].split('Resource')[-1].split(':')
                )
                data_class = _REGISTRY[data_string]
                res.data += [dict(
                    location=d['location'],
                    data=data_class._build(
                        data_uid, copy, tab_level + '    '
                    )
                )]

        return res

    @classmethod
    def _build_from_omf(cls, omf_element, omf_project, project):
        mesh_map = {
            'PointSetGeometry': 'Mesh0D',
            'LineSetGeometry': 'Mesh1D',
            'SurfaceGeometry': 'Mesh2D',
            'SurfaceGridGeometry': 'Mesh2DGrid',
            'VolumeGridGeometry': 'Mesh3DGrid'
        }
        mesh_class = _REGISTRY[mesh_map[
            omf_element.geometry.__class__.__name__
        ]]
        res = cls(
            project=project,
            title=omf_element.name,
            description=omf_element.description,
            mesh=mesh_class._build_from_omf(omf_element.geometry, omf_project),
            opts={'color': omf_element.color}
        )
        if hasattr(omf_element, 'textures'):
            res.textures = []
            for tex in omf_element.textures:
                res.textures += [
                    _REGISTRY['Texture2DImage']._build_from_omf(tex,
                                                                omf_project)
                ]
        if hasattr(omf_element, 'data'):
            res.data = []
            for dat in omf_element.data:
                if dat.__class__.__name__ not in ('ScalarData', 'MappedData'):
                    print('Data of class {} ignored'.format(
                        dat.__class__.__name__
                    ))
                    continue
                res.data += [
                    _REGISTRY['DataArray']._build_from_omf(dat)
                ]
        return res



class BaseMesh(BaseResource):
    """Base class for all mesh resources. These are contained within
    each composite resources and define its structure
    """


class BaseData(BaseResource):
    """Base class for all data resources. These can be contained within
    each composite resource and define data corresponding to the mesh
    """
    @classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for texture resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/data/{class_name}'.format(
                class_name=cls._resource_class)
        return cls.__model_api_location


class BaseTexture2D(BaseResource):
    """Base class for all texture resources. These can be contained
    within some composite resources and define data in space that gets
    mapped to the mesh.
    """
    @classproperty
    @classmethod
    def _model_api_location(cls):
        """api destination for texture resource"""
        if getattr(cls, '__model_api_location', None) is None:
            cls.__model_api_location = 'resource/texture2d/{cls_name}'.format(
                cls_name=cls._resource_class)
        return cls.__model_api_location
