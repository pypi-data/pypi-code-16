"""
HTTP endpoint.

"""
from six.moves.urllib.parse import urlparse, urlunparse
from sys import stderr

from click import echo, progressbar
from requests import Session
from requests.exceptions import ConnectionError, HTTPError

from microcosm_resourcesync.batching import batched
from microcosm_resourcesync.endpoints.base import Endpoint
from microcosm_resourcesync.formatters import Formatters


class HTTPEndpoint(Endpoint):
    """
    Read and write resources for an HTTP URI.

    """
    def __init__(self, uri):
        self.uri = uri
        self.session = Session()

    def __repr__(self):
        return "{}('{}')".format(
            self.__class__.__name__,
            self.uri,
        )

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.uri == other.uri

    @property
    def default_formatter(self):
        return Formatters.JSON.name

    def read(self, schema_cls, follow_mode, **kwargs):
        """
        Read all YAML documents from the file.

        """
        stack, seen = [self.uri], set()

        while stack:
            uri = stack.pop()

            # avoid processing resources cyclically
            if uri in seen:
                continue

            resource_data = self.read_resource_data(uri, **kwargs)

            for resource in self.iter_resources(resource_data, schema_cls):
                seen.add(resource.uri)

                # ignore resources that do not have identifiers (e.g. collections)
                # (but still follow their links)
                if hasattr(resource, "id"):
                    yield resource

                stack.extend(resource.links(follow_mode))

    def read_resource_data(self, uri, verbose, limit, **kwargs):
        """
        Read resource data from a URI.

        """
        if verbose:
            echo("Fetching resource(s) from: {}".format(uri), err=True)

        response = self.session.get(
            uri,
            headers={
                "X-Request-Limit": str(limit),
            },
        )
        # NB: if resources have broken hyperlinks, we can get a 404 here
        if response.status_code >= 400 and verbose:
            echo("Failed fetching resource(s) from: {}: {}".format(uri, response.text))
        response.raise_for_status()
        content_type = response.headers["Content-Type"]
        formatter = Formatters.for_content_type(content_type).value
        return formatter.load(response.text)

    def write(self, resources, **kwargs):
        """
        Write resources as YAML to an HTTP endpoint.

        """
        with progressbar(length=len(resources), file=stderr) as progress_bar:
            for resource_batch in batched(resources, **kwargs):
                self.write_resource_batch(resource_batch, **kwargs)
                progress_bar.update(len(resource_batch))

    def write_resource_batch(self, resource_batch, **kwargs):
        """
        Write resources in a batch.

        NB: batch support via the BulkUpdate convention (PATCH) not implemented yet
        """
        for resource in resource_batch:
            self.write_resource(resource, **kwargs)

    def write_resource(self, resource, formatter, max_attempts, **kwargs):
        """
        Write a single resource via Replace conntetion (PUT).

        """
        uri = self.join_uri(resource.uri)
        data = formatter.value.dump(resource)

        # NB: verbose logging the message content is obnoxius and interferes with the
        # progressbar; if we need more information here, we probably need more levels
        # of verbosity and a more traditional progress bar

        response = self.retry(
            self.session.put,
            uri=uri,
            data=data,
            headers={
                "Content-Type": formatter.value.preferred_mime_type,
            },
            max_attempts=max_attempts,
        )
        response.raise_for_status()

    def join_uri(self, uri):
        """
        Construct a URL using the configured base URL's scheme and netloc and the remainder of the resource's URI.

        This is what `urljoin` ought to do...

        """
        parsed_base_uri = urlparse(self.uri)
        parsed_uri = urlparse(uri)
        return urlunparse(parsed_uri._replace(
            scheme=parsed_base_uri.scheme,
            netloc=parsed_base_uri.netloc,
        ))

    def iter_resources(self, resource_data, schema_cls):
        """
        Iterate over resources in a resource.

        """
        resource = schema_cls(resource_data)

        yield resource

        # process embedded resources (e.g. collections)
        for embedded_resource in resource.embedded:
            yield schema_cls(embedded_resource)

    def retry(self, func, uri, max_attempts, **kwargs):
        """
        Retry HTTP operations on connection failures.

        """
        last_error = None
        for attempt in range(max_attempts):
            try:
                return func(uri, **kwargs)
            except ConnectionError as error:
                echo("Connection error for uri: {}: {}".format(uri, error), err=True)
                last_error = error
                continue
            except HTTPError as error:
                if error.response.status_code in (504, 502):
                    echo("HTTP error for uri: {}: {}".format(uri, error), err=True)
                    last_error = error
                    continue
                raise
            else:
                break
        else:
            # If we reached here, all attempts were unsuccessful - raise last error encountered
            raise last_error
