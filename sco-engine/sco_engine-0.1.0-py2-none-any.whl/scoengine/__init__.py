"""Standard Cortical Observer - Workflow Engine API.

The workflow engine is used to run predictive models for experiments that are
defined in the SCO Data Store. The classes in this module define client
interfaces to the engine. The actual workflow is executed by workers that are
defined in the workflow module. These workers may run locally on the same
machine as the engine client (and the web server) or on remote machines.

The SCO Engine package is intended to decouple the web server code from the
predictive model code.
"""

from abc import abstractmethod
import json
import pika
import socket


# ------------------------------------------------------------------------------
#
# Client
#
# ------------------------------------------------------------------------------

class SCOEngineClient(object):
    """Client for SCO engine. Communicates with workflow backend via simple
    messages. Different implementations of this client-server architecture
    are possible.
    """
    @abstractmethod
    def run_model(self, model_run):
        """Execute the given model run.

        Throws a EngineException if running the model fails.

        Parameters
        ----------
        model_run : ModelRunHandle
            Handle to model run
        """
    pass


class RabbitMQClient(SCOEngineClient):
    """SCO Workflow Engine client using RabbitMQ. Sends Json messages containing
    run identifier (and experiment identifier) to run model.
    """
    def __init__(self, host, queue, reference_factory):
        """Initialize the client by providing host name and queue identifier
        for message queue. In addition, requires a HATEOAS reference factory
        to generate resource URLs.

        Parameters
        ----------
        host : string
            Name of host that runs RabbitMQ
        queue : string
            Identifier of message queue to communicate with workers
        reference_factory : hateoas.HATEOASReferenceFactory
            Factory for resource URL's
        """
        self.host = host
        self.queue = queue
        self.request_factory = RequestFactory(reference_factory)

    def run_model(self, model_run):
        """Run model by sending message to RabbitMQ queue containing the
        run end experiment identifier. Messages are persistent to ensure that
        a worker will process process the run request at some point.

        Throws a EngineException if communication with the server fails.

        Parameters
        ----------
        model_run : ModelRunHandle
            Handle to model run
        """
        # Open connection to RabbitMQ server. Will raise an exception if the
        # server is not running. In this case we raise an EngineException to
        # allow caller to delete model run.
        try:
            con = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
            channel = con.channel()
            channel.queue_declare(queue=self.queue, durable=True)
        except pika.exceptions.AMQPError as ex:
            raise EngineException(str(ex), 500)
        # Create model run request
        request = self.request_factory.get_request(model_run)
        # Send request
        channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=json.dumps(request.to_json()),
            properties=pika.BasicProperties(
                delivery_mode = 2, # make message persistent
            )
        )


class DefaultSCOEngineClient(SCOEngineClient):
    """Default Client for SCO engine. Communicate with server via sockets."""
    def __init__(self, server_host, server_port, reference_factory):
        """Initialize the servers host name and port for socket communication.

        Raises socket.gaierror if host name cannot be resolved.

        Parameters
        ----------
        server_host : string
            Name of host running the SCO engine
        server_port : int
            Port SCO engine is listening on
        reference_factory : hateoas.HATEOASReferenceFactory
            Factory for resource URL's
        """
        self.host = socket.gethostbyname(server_host)
        self.port = server_port
        self.request_factory = RequestFactory(reference_factory)

    def run_model(self, model_run):
        """Execute the given model run. Comminicates with the SCO engine to run
        the model.

        Throws a EngineException if running the model fails.

        Parameters
        ----------
        model_run : ModelRunHandle
            Handle to model run
        """
        # Connect to server
        try:
            s = socket.create_connection((self.host , self.port), timeout=10)
        except socket.error as ex:
            raise EngineException(str(ex), 500)
        # Communication protocoll uses Json. Create and send run request
        # containing run identifier and experiment identifier.
        request = self.request_factory.get_request(model_run)
        try:
            s.sendall(json.dumps(request.to_json()))
        except socket.error as ex:
            raise EngineException(str(ex), 500)
        # Read response from server. Expect Json object with at least status
        # field. If status code is not equal to 200 an exception occurred and
        # the server response is expected to contain an additional message field
        try:
            reply = json.loads(s.recv(4096))
        except Exception as ex:
            raise EngineException(str(ex), 500)
        if reply[RESPONSE_STATUS] != 200:
            raise EngineException(
                reply[RESPONSE_MESSAGE],
                reply[RESPONSE_STATUS]
            )
        s.close()


# ------------------------------------------------------------------------------
#
# Request Factory
#
# ------------------------------------------------------------------------------

class RequestFactory(object):
    """Helper class to generate request object for model runs. The requests are
    interpreted by different worker implementations to run the predictive model.
    """
    def __init__(self, reference_factory):
        """Initialize the HATEOAS reference factory for resource URL's.

        Parameters
        ----------
        reference_factory : hateoas.HATEOASReferenceFactory
            Factory for resource URL's
        """
        self.reference_factory = reference_factory

    def get_request(self, model_run):
        """Create request object to run model. Requests are handled by SCO
        worker implementations.

        Parameters
        ----------
        model_run : ModelRunHandle
            Handle to model run

        Returns
        -------
        ModelRunRequest
            Object representing model run request
        """
        return ModelRunRequest(
            model_run.identifier,
            model_run.experiment,
            self.reference_factory.experiments_prediction_reference(
                model_run.experiment,
                model_run.identifier
            )
        )

class ModelRunRequest(object):
    """Object capturing information to run predictive model. Contains run and
    experiment identifier (used primarily by local workers) as well as resource
    Url (for remote worker that use SCO Client).

    Attributes
    ----------
    run_id : string
        Unique model run identifier
    experiment_id : string
        Unique experiment identifier
    resource_url : string
        Url for model run instance
    """
    def __init__(self, run_id, experiment_id, resource_url):
        """Initialize request attributes.

        Parameters
        ----------
        run_id : string
            Unique model run identifier
        experiment_id : string
            Unique experiment identifier
        resource_url : string
            Url for model run instance
        """
        self.run_id = run_id
        self.experiment_id = experiment_id
        self.resource_url = resource_url

    @staticmethod
    def from_json(json_obj):
        """Create model run request from Json object.

        Parameters
        ----------
        json_obj : Json Object
            Json dump for object representing the model run request.

        Returns
        -------
        ModelRunRequest
        """
        return ModelRunRequest(
            json_obj['run_id'],
            json_obj['experiment_id'],
            json_obj['href']
        )

    def to_json(self):
        """Return Json representation of the run request.

        Returns
        -------
        Json Object
            Json dump for object representing the model run request.
        """
        return {
            'run_id' : self.run_id,
            'experiment_id' : self.experiment_id,
            'href' : self.resource_url
        }


# ------------------------------------------------------------------------------
#
# Exception
#
# ------------------------------------------------------------------------------

class EngineException(Exception):
    """Base class for SCO engine exceptions."""
    def __init__(self, message, status_code):
        """Initialize error message and status code.

        Parameters
        ----------
        message : string
            Error message.
        status_code : int
            Http status code.
        """
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """Dictionary representation of the exception.

        Returns
        -------
        Dictionary
        """
        return {'message' : self.message}
