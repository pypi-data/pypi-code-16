# Different kinds of resource.
import collections

from . import utils


class _ResourceController(object):
    def __init__(self, _client=None, _project=None, _repository=None):
        self._client = _client
        self._project = _project
        self._repository = _repository
        self._items = collections.OrderedDict()
        self._loaded = False

    ################################
    # Container-type special methods.
    #
    # Python bypasses __getattr__ for these methods, so we need to declare
    # them explicitly.

    def __len__(self):
        self._check()

        return self._items.__len__()

    def __getitem__(self, key):
        self._check()

        return self._items.__getitem__(key)

    def __missing__(self, key):
        self._check()

        return self._items.__missing__(key)

    def __setitem__(self, key, value):
        self._check()

        return self._items.__setitem__(key, value)

    def __delitem__(self, key):
        self._check()

        return self._items.__delitem__(key)

    def __iter__(self):
        self._check()

        return self._items.__iter__()

    def __contains__(self, item):
        self._check()

        return self._items.__contains__(item)

    def __reversed__(self):
        self._check()

        return self._items.__reversed__()
    # End of container-type special methods.
    ########################################

    def __getattr__(self, name):
        # Every other access is forwarded to the _items dict, so we can support
        # `items()`, `values()`, etc.
        self._check()

        return getattr(self._items, name)

    def _check(self):
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self):
        raise NotImplementedError


class _ProjectController(_ResourceController):
    def _load(self):
        projects = self._client.get_projects()

        for data in projects:
            proj = Project(_client=self._client, **data['project'])
            self._items[proj.permalink] = proj


class _TicketController(_ResourceController):
    def _load(self):
        slug = self._project.permalink
        tickets = list(self._client.get_tickets(slug))

        for data in tickets:
            ticket = Ticket(_client=self._client, _project=self._project, **data['ticket'])
            self._items[ticket.ticket_id] = ticket


class _NoteController(_ResourceController):
    def __init__(self, *args, **kwargs):
        self._ticket = kwargs.pop('_ticket')
        super(_NoteController, self).__init__(*args, **kwargs)

    def _load(self):
        slug = self._project.permalink
        notes = self._client.get_ticket_notes(slug, self._ticket.ticket_id)

        for data in notes:
            kwargs = data['ticket_note']
            note = Note(**kwargs)
            self._items[note.id] = note


class _RepositoryController(_ResourceController):
    def _load(self):
        slug = self._project.permalink
        repos = list(self._client.get_repositories(slug))

        for data in repos:
            kwargs = data['repository']
            kwargs['_client'] = self._client
            kwargs['_project'] = self._project
            repo = Repository(**kwargs)
            self._items[repo.permalink] = repo


class _DeploymentController(_ResourceController):
    def _load(self):
        proj = self._project.permalink
        repo = self._repository.permalink
        deployments = list(self._client.get_deployments(proj, repo))

        for idx, data in enumerate(deployments):
            kwargs = data['deployment']
            kwargs['_client'] = self._client
            kwargs['_project'] = self._project
            kwargs['_repository'] = self._repository
            deployment = Deployment(**kwargs)
            # Deployments don't have a permalink or anything. So just use the
            # order as an index. This could be a list, but let's keep this as
            # a mapping so it works like the other controllers.
            self._items[idx] = deployment


class _StatusController(_ResourceController):
    def _load(self):
        proj = self._project.permalink
        objects = list(self._client.get_ticket_statuses(proj))

        for data in objects:
            kwargs = data['ticketing_status']
            obj = Status(**kwargs)

            self._items[obj.id] = obj


class _PriorityController(_ResourceController):
    def _load(self):
        proj = self._project.permalink
        objects = list(self._client.get_ticket_priorities(proj))

        for data in objects:
            kwargs = data['ticketing_priority']
            obj = Priority(**kwargs)

            self._items[obj.id] = obj


class _TypeController(_ResourceController):
    def _load(self):
        proj = self._project.permalink
        objects = list(self._client.get_ticket_types(proj))

        for data in objects:
            kwargs = data['ticketing_type']
            obj = Type(**kwargs)

            self._items[obj.id] = obj


class _CategoryController(_ResourceController):
    def _load(self):
        proj = self._project.permalink
        objects = list(self._client.get_ticket_categories(proj))

        for data in objects:
            kwargs = data['ticketing_category']
            obj = Category(**kwargs)

            self._items[obj.id] = obj


class _UserController(_ResourceController):
    def _load(self):
        proj = self._project.permalink
        objects = self._client.get_project_users(proj)

        for data in objects:
            kwargs = data['user']
            obj = User(**kwargs)

            self._items[obj.id] = obj


class Project(object):
    """A project is a core part of your Codebase account. Each project can
    contain repositories, tickets, milestones, wikis and many other objects.
    """

    def __init__(self, project_id=None, account_name=None, group_id=None,
            icon=None, name=None, overview=None, start_page=None, status=None,
            permalink=None, disk_usage=None, total_tickets=None,
            open_tickets=None, closed_tickets=None, _client=None):
        self._client = _client
        self.tickets = _TicketController(_project=self, _client=_client)
        self.repositories = _RepositoryController(_project=self, _client=_client)
        self.statuses = _StatusController(_project=self, _client=_client)
        self.priorities = _PriorityController(_project=self, _client=_client)
        self.types = _TypeController(_project=self, _client=_client)
        self.categories = _CategoryController(_project=self, _client=_client)
        self.users = _UserController(_project=self, _client=_client)

        self.project_id = project_id
        self.account_name = account_name
        self.group_id = group_id
        self.icon = icon
        self.name = name
        self.overview = overview
        self.start_page = start_page
        self.status = status
        self.permalink = permalink
        self.disk_usage = disk_usage
        self.total_tickets = total_tickets
        self.open_tickets = open_tickets
        self.closed_tickets = closed_tickets

    def __repr__(self):
        name = repr(self.name)

        return '%s(project_id=%s, name=%s)' % (self.__class__.__name__, self.project_id, name)


class Repository(object):
    """A repository has a large number of moving parts. Over time, you'll be
    able to access all of these using the API as well as the web interface. At
    present, you can access a list of all available repositories for any project
    within your account with various properties (as shown below).
    """
    def __init__(self, default_branch=None, disk_usage=None,
            last_commit_ref=None, clone_url=None, name=None, permalink=None,
            description=None, scm=None, _client=None, _project=None,
            _repository=None):
        self._client = _client
        self._project = _project
        self.deployments = _DeploymentController(
            _project=_project,
            _client=_client,
            _repository=self,
        )

        self.clone_url = clone_url
        self.default_branch = default_branch
        self.description = description
        self.disk_usage = disk_usage
        self.last_commit_ref = last_commit_ref
        self.name = name
        self.permalink = permalink
        self.scm = scm

    def __repr__(self):
        return '%s(clone_url=%r)' % (self.__class__.__name__, self.clone_url)


class Deployment(object):
    def __init__(self, branch=None, environment=None, revision=None,
            servers=None, _client=None, _project=None, _repository=None):
        self._client = _client
        self._project = _project
        self._repository = _repository

        self.branch = branch
        self.environment = environment
        self.revision = revision
        self.servers = servers


class Ticket(object):
    def __init__(self, assignee=None, assignee_id=None, category=None,
            category_id=None, created_at=None, deadline=None,
            estimated_time=None, milestone=None, milestone_id=None,
            priority=None, priority_id=None, project_id=None, reporter=None,
            reporter_id=None, start_on=None, status=None, status_id=None,
            summary=None, tags=None, ticket_id=None, ticket_type=None,
            total_time_spent=None, type=None, type_id=None, updated_at=None,
            _client=None, _project=None):
        self._client = _client
        self._project = _project
        self.notes = _NoteController(_client=_client, _project=_project, _ticket=self)

        self.assignee = assignee
        self.assignee_id = assignee_id
        self.category = category
        self.category_id = category_id
        self.created_at = utils.parse_date(created_at)
        self.deadline = deadline
        self.estimated_time = estimated_time
        self.milestone = milestone
        self.milestone_id = milestone_id
        self.priority = priority
        self.priority_id = priority_id
        self.project_id = project_id
        self.reporter = reporter
        self.reporter_id = reporter_id
        self.start_on = start_on
        self.status = status
        self.status_id = status_id
        self.summary = summary
        self.tags = tags
        self.ticket_id = ticket_id
        self.ticket_type = ticket_type
        self.total_time_spent = total_time_spent
        self.type = type
        self.type_id = type_id
        self.updated_at = utils.parse_date(updated_at)

    def __repr__(self):
        return '%s(ticket_id=%s)' % (self.__class__.__name__, self.ticket_id)


class Note(object):
    """A note on a ticket."""
    def __init__(self, attachments=None, content=None, created_at=None, id=None,
            updated_at=None, updates=None, user_id=None, _client=None):
        self.attachments = attachments
        self.content = content
        self.created_at = utils.parse_date(created_at)
        self.id = id
        self.updated_at = utils.parse_date(updated_at)
        self.updates = updates
        self.user_id = user_id


class Status(object):
    def __init__(self, colour=None, id=None, name=None, order=None,
            treat_as_closed=None, _client=None):
        self._client = _client

        self.colour = colour
        self.id = id
        self.name = name
        self.order = order
        self.treat_as_closed = treat_as_closed


class Category(object):
    def __init__(self, id=None, name=None, _client=None):
        self._client = _client

        self.id = id
        self.name = name


class Type(object):
    def __init__(self, icon=None, id=None, name=None, _client=None):
        self._client = _client

        self.icon = icon
        self.id = id
        self.name = name


class Priority(object):
    def __init__(self, colour=None, default=None, id=None, name=None,
            position=None, _client=None):
        self._client = _client

        self.colour = colour
        self.default = default
        self.id = id
        self.name = name
        self.position = position


class User(object):
    # The all users API returns some more attributes like 'enabled' and
    # 'last_activity_at', but this is the subset returned by the project
    # assignments API.

    def __init__(self, company=None, email_address=None, email_addresses=None,
            first_name=None, id=None, last_name=None, username=None,
            _client=None):
        self._client = _client

        self.company = company
        self.email_address = email_address
        self.email_addresses = email_addresses
        self.first_name = first_name
        self.id = id
        self.last_name = last_name
        self.username = username
