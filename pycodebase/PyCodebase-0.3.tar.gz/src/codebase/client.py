import ConfigParser
import logging
import os

import notrequests

from . import rsrc
from . import utils


CODEBASE_API_URL = 'https://api3.codebasehq.com'
logger = logging.getLogger(__file__)


class Client(object):
    """Codebase API client class."""
    def __init__(self, (username, key)):
        self.projects = rsrc._ProjectController(_client=self)
        self.auth = (username, key)
        self.base_url = CODEBASE_API_URL

        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def _api_method(self, method, path, params=None, json=None):
        url = self.base_url + path
        headers = {'Accept': 'application/json'}

        logger.debug('%r %r params:%r', method, url, params)
        response = notrequests.request(
            method,
            url,
            auth=self.auth,
            params=params,
            headers=headers,
            json=json,
            timeout=30,
        )

        try:
            response.raise_for_status()
        except notrequests.HTTPError:
            msg = 'Response %r for %r. Content: %r'
            logger.info(msg, response.status_code, url, response.content)
            raise

        return response

    def _api_post(self, path, params=None, json=None):
        return self._api_method('POST', path, params=params, json=json)

    def _api_get(self, path, params=None):
        return self._api_method('GET', path, params=params)

    def _api_get_generator(self, path, params=None):
        """Yields pages of results, until a request gets a 404 response."""
        params = dict(params) if params else {}
        params['page'] = 1

        while True:
            try:
                response = self._api_get(path, params=params)
            except notrequests.HTTPError:
                break
            else:
                yield response

                params['page'] += 1

    def _get_activity(self, path, raw=True, since=None):
        # This is used for both /activity and /foo/activity APIs.

        params = {}

        if raw:
            params['raw'] = 'true'

        if since:
            params['since'] = utils.format_since_dt(since)

        for response in self._api_get_generator(path, params=params):
            data = response.json()

            # /:project/activity returns an empty list, status 200 when there
            # are no more events.
            if not data:
                break

            for obj in data:
                yield obj

    def get_users(self):
        """Returns a generator of all users for this account."""
        path = 'users'
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def get_activity(self, raw=True, since=None):
        """Returns a generator of events on the account."""
        path = 'activity'

        return self._get_activity(path, raw=raw, since=since)

    def get_projects(self):
        """Returns a generator of all projects."""
        # The API for projects is not paginated, all projects in one request.

        path = 'projects'
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def get_project_users(self, project):
        """Returns a generator of users assigned to a project."""
        path = '%s/assignments' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def get_project_activity(self, project, raw=True, since=None):
        """Returns a generator of events for a project.

        This will keep making requests through the entire project history, if
        the caller consumes the entire generator.
        """
        path = '%s/activity' % project

        return self._get_activity(path, raw=raw, since=since)

    def get_repositories(self, project):
        """Returns a generator of configured repos for a project."""
        path = '%s/repositories' % (project,)
        response = self._api_get(path)
        data = response.json()

        for obj in data:
            yield obj

    def get_deployments(self, project, repo):
        path = '%s/%s/deployments' % (project, repo)

        for response in self._api_get_generator(path):
            data = response.json()

            # The API is supposed to 404 when there are no more pages, but
            # /:project/:repo/deployments returns an empty list, status 200.
            if not data:
                break

            for obj in data:
                yield obj

    def create_deployment(self, project, repo, branch, revision, environment, servers):
        """Creates a new deployment."""
        path = '%s/%s/deployments' % (project, repo)

        payload = {
            'deployment': {
                'branch': branch,
                'revision': revision,
                'environment': environment,
                'servers': servers,
            },
        }

        response = self._api_post(path, json=payload)
        data = response.json()

        return data

    def get_tickets(self, project, assignee=None, status=None, category=None,
            type=None, priority=None, milestone=None):
        """Returns a generator of ticket objects.

        Search terms can be a string, or a list of strings.
        """
        path = '%s/tickets' % project

        query = utils.build_ticket_search_query(
            assignee=assignee,
            status=status,
            category=None,
            type=type,
            priority=priority,
            milestone=milestone,
        )

        params = {'query': query} if query else {}

        for response in self._api_get_generator(path, params=params):
            data = response.json()

            for obj in data:
                yield obj

    def create_ticket(self, project, assignee_id=None, category_id=None,
            description=None, milestone_id=None, priority_id=None,
            reporter_id=None, status_id=None, summary=None, type=None,
            upload_tokens=None):
        """Create a new ticket."""
        # https://support.codebasehq.com/kb/tickets-and-milestones

        path = '%s/tickets' % project

        payload = {
            'ticket': {
                'summary': summary,
                'ticket_type': type,
                'reporter_id': reported_id,
                'assignee_id': assignee_id,
                'category_id': category_id,
                'priority_id': priority_id,
                'status_id': status_id,
                'milestone_id': milestone_id,
                'upload_tokens': upload_tokens,
                'description': description,
            },
        }

        response = self._api_post(path, json=payload)
        data = response.json()

        return data

    def get_ticket_notes(self, project, ticket_id):
        """Returns a generator of ticket notes."""
        # The API returns all notes in a single response. Not paginated.

        path = '%s/tickets/%s/notes' % (project, ticket_id)
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def create_ticket_note(self, project, ticket_id, assignee_id=None,
            category_id=None, content=None, milestone_id=None, priority_id=None,
            private=None, status_id=None, summary=None, time_added=None,
            upload_tokens=None):
        """Create a new note on a ticket in a project.

        https://support.codebasehq.com/kb/tickets-and-milestones/updating-tickets
        """
        # You can change a ticket's properties by creating a note.
        path = '%s/tickets/%s/notes' % (project, ticket_id)

        note_data = utils.build_create_note_payload(
            assignee_id=assignee_id,
            category_id=category_id,
            content=content,
            milestone_id=milestone_id,
            priority_id=priority_id,
            private=private,
            status_id=status_id,
            summary=summary,
            time_added=time_added,
            upload_tokens=upload_tokens,
        )
        payload = {'ticket_note': note_data}

        data = self._api_post(path, json=payload).json()

        return data

    def get_ticket_statuses(self, project):
        """Returns a generator of ticket status objects."""
        path = '%s/tickets/statuses' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def get_ticket_categories(self, project):
        """Returns a generator of ticket category objects."""
        path = '%s/tickets/categories' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def get_ticket_types(self, project):
        """Returns a generator of ticket type objects."""
        path = '%s/tickets/types' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    def get_ticket_priorities(self, project):
        """Returns a generator of ticket priority objects."""
        path = '%s/tickets/priorities' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj

    @classmethod
    def with_secrets(cls, filename):
        return new_client_with_secrets_from_filename(cls, filename)


def new_client_with_secrets_from_filename(cls, filename):
    """Returns a new instance of codebase.Client. The username / key are read
    from the filename which must be in INI format. A filename like '~/.secrets'
    is expanded to the current user's home directory.
    """
    config = ConfigParser.SafeConfigParser()

    filename = os.path.expanduser(filename)

    with open(filename) as fh:
        config.readfp(fh)

    username = config.get('api', 'username')
    key = config.get('api', 'key')

    return cls((username, key))
