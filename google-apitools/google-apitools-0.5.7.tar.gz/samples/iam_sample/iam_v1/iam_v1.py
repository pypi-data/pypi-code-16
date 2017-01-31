#!/usr/bin/env python
"""CLI for iam, version v1."""
# NOTE: This file is autogenerated and should not be edited by hand.

import code
import os
import platform
import sys

from apitools.base.protorpclite import message_types
from apitools.base.protorpclite import messages

from google.apputils import appcommands
import gflags as flags

import apitools.base.py as apitools_base
from apitools.base.py import cli as apitools_base_cli
import iam_v1_client as client_lib
import iam_v1_messages as messages


def _DeclareIamFlags():
  """Declare global flags in an idempotent way."""
  if 'api_endpoint' in flags.FLAGS:
    return
  flags.DEFINE_string(
      'api_endpoint',
      u'https://iam.googleapis.com/',
      'URL of the API endpoint to use.',
      short_name='iam_url')
  flags.DEFINE_string(
      'history_file',
      u'~/.iam.v1.history',
      'File with interactive shell history.')
  flags.DEFINE_multistring(
      'add_header', [],
      'Additional http headers (as key=value strings). '
      'Can be specified multiple times.')
  flags.DEFINE_string(
      'service_account_json_keyfile', '',
      'Filename for a JSON service account key downloaded'
      ' from the Developer Console.')
  flags.DEFINE_enum(
      'f__xgafv',
      u'_1',
      [u'_1', u'_2'],
      u'V1 error format.')
  flags.DEFINE_string(
      'access_token',
      None,
      u'OAuth access token.')
  flags.DEFINE_enum(
      'alt',
      u'json',
      [u'json', u'media', u'proto'],
      u'Data format for response.')
  flags.DEFINE_string(
      'bearer_token',
      None,
      u'OAuth bearer token.')
  flags.DEFINE_string(
      'callback',
      None,
      u'JSONP')
  flags.DEFINE_string(
      'fields',
      None,
      u'Selector specifying which fields to include in a partial response.')
  flags.DEFINE_string(
      'key',
      None,
      u'API key. Your API key identifies your project and provides you with '
      u'API access, quota, and reports. Required unless you provide an OAuth '
      u'2.0 token.')
  flags.DEFINE_string(
      'oauth_token',
      None,
      u'OAuth 2.0 token for the current user.')
  flags.DEFINE_boolean(
      'pp',
      'True',
      u'Pretty-print response.')
  flags.DEFINE_boolean(
      'prettyPrint',
      'True',
      u'Returns response with indentations and line breaks.')
  flags.DEFINE_string(
      'quotaUser',
      None,
      u'Available to use for quota purposes for server-side applications. Can'
      u' be any arbitrary string assigned to a user, but should not exceed 40'
      u' characters.')
  flags.DEFINE_string(
      'trace',
      None,
      'A tracing token of the form "token:<tokenid>" to include in api '
      'requests.')
  flags.DEFINE_string(
      'uploadType',
      None,
      u'Legacy upload protocol for media (e.g. "media", "multipart").')
  flags.DEFINE_string(
      'upload_protocol',
      None,
      u'Upload protocol for media (e.g. "raw", "multipart").')


FLAGS = flags.FLAGS
apitools_base_cli.DeclareBaseFlags()
_DeclareIamFlags()


def GetGlobalParamsFromFlags():
  """Return a StandardQueryParameters based on flags."""
  result = messages.StandardQueryParameters()
  if FLAGS['f__xgafv'].present:
    result.f__xgafv = messages.StandardQueryParameters.FXgafvValueValuesEnum(FLAGS.f__xgafv)
  if FLAGS['access_token'].present:
    result.access_token = FLAGS.access_token.decode('utf8')
  if FLAGS['alt'].present:
    result.alt = messages.StandardQueryParameters.AltValueValuesEnum(FLAGS.alt)
  if FLAGS['bearer_token'].present:
    result.bearer_token = FLAGS.bearer_token.decode('utf8')
  if FLAGS['callback'].present:
    result.callback = FLAGS.callback.decode('utf8')
  if FLAGS['fields'].present:
    result.fields = FLAGS.fields.decode('utf8')
  if FLAGS['key'].present:
    result.key = FLAGS.key.decode('utf8')
  if FLAGS['oauth_token'].present:
    result.oauth_token = FLAGS.oauth_token.decode('utf8')
  if FLAGS['pp'].present:
    result.pp = FLAGS.pp
  if FLAGS['prettyPrint'].present:
    result.prettyPrint = FLAGS.prettyPrint
  if FLAGS['quotaUser'].present:
    result.quotaUser = FLAGS.quotaUser.decode('utf8')
  if FLAGS['trace'].present:
    result.trace = FLAGS.trace.decode('utf8')
  if FLAGS['uploadType'].present:
    result.uploadType = FLAGS.uploadType.decode('utf8')
  if FLAGS['upload_protocol'].present:
    result.upload_protocol = FLAGS.upload_protocol.decode('utf8')
  return result


def GetClientFromFlags():
  """Return a client object, configured from flags."""
  log_request = FLAGS.log_request or FLAGS.log_request_response
  log_response = FLAGS.log_response or FLAGS.log_request_response
  api_endpoint = apitools_base.NormalizeApiEndpoint(FLAGS.api_endpoint)
  additional_http_headers = dict(x.split('=', 1) for x in FLAGS.add_header)
  credentials_args = {
      'service_account_json_keyfile': os.path.expanduser(FLAGS.service_account_json_keyfile)
  }
  try:
    client = client_lib.IamV1(
        api_endpoint, log_request=log_request,
        log_response=log_response,
        credentials_args=credentials_args,
        additional_http_headers=additional_http_headers)
  except apitools_base.CredentialsError as e:
    print 'Error creating credentials: %s' % e
    sys.exit(1)
  return client


class PyShell(appcommands.Cmd):

  def Run(self, _):
    """Run an interactive python shell with the client."""
    client = GetClientFromFlags()
    params = GetGlobalParamsFromFlags()
    for field in params.all_fields():
      value = params.get_assigned_value(field.name)
      if value != field.default:
        client.AddGlobalParam(field.name, value)
    banner = """
           == iam interactive console ==
                 client: a iam client
          apitools_base: base apitools module
         messages: the generated messages module
    """
    local_vars = {
        'apitools_base': apitools_base,
        'client': client,
        'client_lib': client_lib,
        'messages': messages,
    }
    if platform.system() == 'Linux':
      console = apitools_base_cli.ConsoleWithReadline(
          local_vars, histfile=FLAGS.history_file)
    else:
      console = code.InteractiveConsole(local_vars)
    try:
      console.interact(banner)
    except SystemExit as e:
      return e.code


class IamPoliciesGetPolicyDetails(apitools_base_cli.NewCmd):
  """Command wrapping iamPolicies.GetPolicyDetails."""

  usage = """iamPolicies_getPolicyDetails"""

  def __init__(self, name, fv):
    super(IamPoliciesGetPolicyDetails, self).__init__(name, fv)
    flags.DEFINE_string(
        'fullResourcePath',
        None,
        u'REQUIRED: The full resource path of the current policy being '
        u'requested, e.g., `//dataflow.googleapis.com/projects/../jobs/..`.',
        flag_values=fv)
    flags.DEFINE_integer(
        'pageSize',
        None,
        u'Limit on the number of policies to include in the response. Further'
        u' accounts can subsequently be obtained by including the '
        u'GetPolicyDetailsResponse.next_page_token in a subsequent request. '
        u'If zero, the default page size 20 will be used. Must be given a '
        u'value in range [0, 100], otherwise an invalid argument error will '
        u'be returned.',
        flag_values=fv)
    flags.DEFINE_string(
        'pageToken',
        None,
        u'Optional pagination token returned in an earlier '
        u'GetPolicyDetailsResponse.next_page_token response.',
        flag_values=fv)

  def RunWithArgs(self):
    """Returns the current IAM policy and the policies on the inherited
    resources that the user has access to.

    Flags:
      fullResourcePath: REQUIRED: The full resource path of the current policy
        being requested, e.g.,
        `//dataflow.googleapis.com/projects/../jobs/..`.
      pageSize: Limit on the number of policies to include in the response.
        Further accounts can subsequently be obtained by including the
        GetPolicyDetailsResponse.next_page_token in a subsequent request. If
        zero, the default page size 20 will be used. Must be given a value in
        range [0, 100], otherwise an invalid argument error will be returned.
      pageToken: Optional pagination token returned in an earlier
        GetPolicyDetailsResponse.next_page_token response.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.GetPolicyDetailsRequest(
        )
    if FLAGS['fullResourcePath'].present:
      request.fullResourcePath = FLAGS.fullResourcePath.decode('utf8')
    if FLAGS['pageSize'].present:
      request.pageSize = FLAGS.pageSize
    if FLAGS['pageToken'].present:
      request.pageToken = FLAGS.pageToken.decode('utf8')
    result = client.iamPolicies.GetPolicyDetails(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsCreate(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.Create."""

  usage = """projects_serviceAccounts_create <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsCreate, self).__init__(name, fv)
    flags.DEFINE_string(
        'createServiceAccountRequest',
        None,
        u'A CreateServiceAccountRequest resource to be passed as the request '
        u'body.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Creates a ServiceAccount and returns it.

    Args:
      name: Required. The resource name of the project associated with the
        service accounts, such as `projects/my-project-123`.

    Flags:
      createServiceAccountRequest: A CreateServiceAccountRequest resource to
        be passed as the request body.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsCreateRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['createServiceAccountRequest'].present:
      request.createServiceAccountRequest = apitools_base.JsonToMessage(messages.CreateServiceAccountRequest, FLAGS.createServiceAccountRequest)
    result = client.projects_serviceAccounts.Create(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsDelete(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.Delete."""

  usage = """projects_serviceAccounts_delete <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsDelete, self).__init__(name, fv)

  def RunWithArgs(self, name):
    """Deletes a ServiceAccount.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`. Using `-` as a
        wildcard for the project will infer the project from the account. The
        `account` value can be the `email` address or the `unique_id` of the
        service account.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsDeleteRequest(
        name=name.decode('utf8'),
        )
    result = client.projects_serviceAccounts.Delete(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsGet(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.Get."""

  usage = """projects_serviceAccounts_get <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsGet, self).__init__(name, fv)

  def RunWithArgs(self, name):
    """Gets a ServiceAccount.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`. Using `-` as a
        wildcard for the project will infer the project from the account. The
        `account` value can be the `email` address or the `unique_id` of the
        service account.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsGetRequest(
        name=name.decode('utf8'),
        )
    result = client.projects_serviceAccounts.Get(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsGetIamPolicy(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.GetIamPolicy."""

  usage = """projects_serviceAccounts_getIamPolicy <resource>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsGetIamPolicy, self).__init__(name, fv)

  def RunWithArgs(self, resource):
    """Returns the IAM access control policy for specified IAM resource.

    Args:
      resource: REQUIRED: The resource for which the policy is being
        requested. `resource` is usually specified as a path, such as
        `projects/*project*/zones/*zone*/disks/*disk*`.  The format for the
        path specified in this value is resource specific and is specified in
        the `getIamPolicy` documentation.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsGetIamPolicyRequest(
        resource=resource.decode('utf8'),
        )
    result = client.projects_serviceAccounts.GetIamPolicy(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsList(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.List."""

  usage = """projects_serviceAccounts_list <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsList, self).__init__(name, fv)
    flags.DEFINE_integer(
        'pageSize',
        None,
        u'Optional limit on the number of service accounts to include in the '
        u'response. Further accounts can subsequently be obtained by '
        u'including the ListServiceAccountsResponse.next_page_token in a '
        u'subsequent request.',
        flag_values=fv)
    flags.DEFINE_string(
        'pageToken',
        None,
        u'Optional pagination token returned in an earlier '
        u'ListServiceAccountsResponse.next_page_token.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'removeDeletedServiceAccounts',
        None,
        u'Do not list service accounts deleted from Gaia. <b><font '
        u'color="red">DO NOT INCLUDE IN EXTERNAL DOCUMENTATION</font></b>.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Lists ServiceAccounts for a project.

    Args:
      name: Required. The resource name of the project associated with the
        service accounts, such as `projects/my-project-123`.

    Flags:
      pageSize: Optional limit on the number of service accounts to include in
        the response. Further accounts can subsequently be obtained by
        including the ListServiceAccountsResponse.next_page_token in a
        subsequent request.
      pageToken: Optional pagination token returned in an earlier
        ListServiceAccountsResponse.next_page_token.
      removeDeletedServiceAccounts: Do not list service accounts deleted from
        Gaia. <b><font color="red">DO NOT INCLUDE IN EXTERNAL
        DOCUMENTATION</font></b>.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsListRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['pageSize'].present:
      request.pageSize = FLAGS.pageSize
    if FLAGS['pageToken'].present:
      request.pageToken = FLAGS.pageToken.decode('utf8')
    if FLAGS['removeDeletedServiceAccounts'].present:
      request.removeDeletedServiceAccounts = FLAGS.removeDeletedServiceAccounts
    result = client.projects_serviceAccounts.List(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsSetIamPolicy(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.SetIamPolicy."""

  usage = """projects_serviceAccounts_setIamPolicy <resource>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsSetIamPolicy, self).__init__(name, fv)
    flags.DEFINE_string(
        'setIamPolicyRequest',
        None,
        u'A SetIamPolicyRequest resource to be passed as the request body.',
        flag_values=fv)

  def RunWithArgs(self, resource):
    """Sets the IAM access control policy for the specified IAM resource.

    Args:
      resource: REQUIRED: The resource for which the policy is being
        specified. `resource` is usually specified as a path, such as
        `projects/*project*/zones/*zone*/disks/*disk*`.  The format for the
        path specified in this value is resource specific and is specified in
        the `setIamPolicy` documentation.

    Flags:
      setIamPolicyRequest: A SetIamPolicyRequest resource to be passed as the
        request body.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsSetIamPolicyRequest(
        resource=resource.decode('utf8'),
        )
    if FLAGS['setIamPolicyRequest'].present:
      request.setIamPolicyRequest = apitools_base.JsonToMessage(messages.SetIamPolicyRequest, FLAGS.setIamPolicyRequest)
    result = client.projects_serviceAccounts.SetIamPolicy(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsSignBlob(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.SignBlob."""

  usage = """projects_serviceAccounts_signBlob <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsSignBlob, self).__init__(name, fv)
    flags.DEFINE_string(
        'signBlobRequest',
        None,
        u'A SignBlobRequest resource to be passed as the request body.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Signs a blob using a service account's system-managed private key.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`. Using `-` as a
        wildcard for the project will infer the project from the account. The
        `account` value can be the `email` address or the `unique_id` of the
        service account.

    Flags:
      signBlobRequest: A SignBlobRequest resource to be passed as the request
        body.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsSignBlobRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['signBlobRequest'].present:
      request.signBlobRequest = apitools_base.JsonToMessage(messages.SignBlobRequest, FLAGS.signBlobRequest)
    result = client.projects_serviceAccounts.SignBlob(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsSignJwt(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.SignJwt."""

  usage = """projects_serviceAccounts_signJwt <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsSignJwt, self).__init__(name, fv)
    flags.DEFINE_string(
        'signJwtRequest',
        None,
        u'A SignJwtRequest resource to be passed as the request body.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Signs a JWT using a service account's system-managed private key.  If
    no `exp` (expiry) time is contained in the claims, we will provide an
    expiry of one hour in the future. If an expiry of more than one hour in
    the future is requested, the request will fail.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`. Using `-` as a
        wildcard for the project will infer the project from the account. The
        `account` value can be the `email` address or the `unique_id` of the
        service account.

    Flags:
      signJwtRequest: A SignJwtRequest resource to be passed as the request
        body.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsSignJwtRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['signJwtRequest'].present:
      request.signJwtRequest = apitools_base.JsonToMessage(messages.SignJwtRequest, FLAGS.signJwtRequest)
    result = client.projects_serviceAccounts.SignJwt(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsTestIamPermissions(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.TestIamPermissions."""

  usage = """projects_serviceAccounts_testIamPermissions <resource>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsTestIamPermissions, self).__init__(name, fv)
    flags.DEFINE_string(
        'testIamPermissionsRequest',
        None,
        u'A TestIamPermissionsRequest resource to be passed as the request '
        u'body.',
        flag_values=fv)

  def RunWithArgs(self, resource):
    """Tests the specified permissions against the IAM access control policy
    for the specified IAM resource.

    Args:
      resource: REQUIRED: The resource for which the policy detail is being
        requested. `resource` is usually specified as a path, such as
        `projects/*project*/zones/*zone*/disks/*disk*`.  The format for the
        path specified in this value is resource specific and is specified in
        the `testIamPermissions` documentation.

    Flags:
      testIamPermissionsRequest: A TestIamPermissionsRequest resource to be
        passed as the request body.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsTestIamPermissionsRequest(
        resource=resource.decode('utf8'),
        )
    if FLAGS['testIamPermissionsRequest'].present:
      request.testIamPermissionsRequest = apitools_base.JsonToMessage(messages.TestIamPermissionsRequest, FLAGS.testIamPermissionsRequest)
    result = client.projects_serviceAccounts.TestIamPermissions(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsUpdate(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts.Update."""

  usage = """projects_serviceAccounts_update <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsUpdate, self).__init__(name, fv)
    flags.DEFINE_string(
        'description',
        None,
        u'Optional. A user-specified opaque description of the service '
        u'account.',
        flag_values=fv)
    flags.DEFINE_string(
        'displayName',
        None,
        u'Optional. A user-specified description of the service account.  '
        u'Must be fewer than 100 UTF-8 bytes.',
        flag_values=fv)
    flags.DEFINE_string(
        'email',
        None,
        u'@OutputOnly The email address of the service account.',
        flag_values=fv)
    flags.DEFINE_string(
        'etag',
        None,
        u'Used to perform a consistent read-modify-write.',
        flag_values=fv)
    flags.DEFINE_string(
        'oauth2ClientId',
        None,
        u'@OutputOnly. The OAuth2 client id for the service account. This is '
        u'used in conjunction with the OAuth2 clientconfig API to make three '
        u'legged OAuth2 (3LO) flows to access the data of Google users.',
        flag_values=fv)
    flags.DEFINE_string(
        'projectId',
        None,
        u'@OutputOnly The id of the project that owns the service account.',
        flag_values=fv)
    flags.DEFINE_string(
        'uniqueId',
        None,
        u'@OutputOnly The unique and stable id of the service account.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Updates a ServiceAccount.  Currently, only the following fields are
    updatable: `display_name` . The `etag` is mandatory.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`.  Requests using `-` as
        a wildcard for the project will infer the project from the `account`
        and the `account` value can be the `email` address or the `unique_id`
        of the service account.  In responses the resource name will always be
        in the format `projects/{project}/serviceAccounts/{email}`.

    Flags:
      description: Optional. A user-specified opaque description of the
        service account.
      displayName: Optional. A user-specified description of the service
        account.  Must be fewer than 100 UTF-8 bytes.
      email: @OutputOnly The email address of the service account.
      etag: Used to perform a consistent read-modify-write.
      oauth2ClientId: @OutputOnly. The OAuth2 client id for the service
        account. This is used in conjunction with the OAuth2 clientconfig API
        to make three legged OAuth2 (3LO) flows to access the data of Google
        users.
      projectId: @OutputOnly The id of the project that owns the service
        account.
      uniqueId: @OutputOnly The unique and stable id of the service account.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.ServiceAccount(
        name=name.decode('utf8'),
        )
    if FLAGS['description'].present:
      request.description = FLAGS.description.decode('utf8')
    if FLAGS['displayName'].present:
      request.displayName = FLAGS.displayName.decode('utf8')
    if FLAGS['email'].present:
      request.email = FLAGS.email.decode('utf8')
    if FLAGS['etag'].present:
      request.etag = FLAGS.etag
    if FLAGS['oauth2ClientId'].present:
      request.oauth2ClientId = FLAGS.oauth2ClientId.decode('utf8')
    if FLAGS['projectId'].present:
      request.projectId = FLAGS.projectId.decode('utf8')
    if FLAGS['uniqueId'].present:
      request.uniqueId = FLAGS.uniqueId.decode('utf8')
    result = client.projects_serviceAccounts.Update(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsKeysCreate(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts_keys.Create."""

  usage = """projects_serviceAccounts_keys_create <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsKeysCreate, self).__init__(name, fv)
    flags.DEFINE_string(
        'createServiceAccountKeyRequest',
        None,
        u'A CreateServiceAccountKeyRequest resource to be passed as the '
        u'request body.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Creates a ServiceAccountKey and returns it.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`. Using `-` as a
        wildcard for the project will infer the project from the account. The
        `account` value can be the `email` address or the `unique_id` of the
        service account.

    Flags:
      createServiceAccountKeyRequest: A CreateServiceAccountKeyRequest
        resource to be passed as the request body.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsKeysCreateRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['createServiceAccountKeyRequest'].present:
      request.createServiceAccountKeyRequest = apitools_base.JsonToMessage(messages.CreateServiceAccountKeyRequest, FLAGS.createServiceAccountKeyRequest)
    result = client.projects_serviceAccounts_keys.Create(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsKeysDelete(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts_keys.Delete."""

  usage = """projects_serviceAccounts_keys_delete <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsKeysDelete, self).__init__(name, fv)

  def RunWithArgs(self, name):
    """Deletes a ServiceAccountKey.

    Args:
      name: The resource name of the service account key in the following
        format: `projects/{project}/serviceAccounts/{account}/keys/{key}`.
        Using `-` as a wildcard for the project will infer the project from
        the account. The `account` value can be the `email` address or the
        `unique_id` of the service account.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsKeysDeleteRequest(
        name=name.decode('utf8'),
        )
    result = client.projects_serviceAccounts_keys.Delete(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsKeysGet(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts_keys.Get."""

  usage = """projects_serviceAccounts_keys_get <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsKeysGet, self).__init__(name, fv)
    flags.DEFINE_enum(
        'publicKeyType',
        u'TYPE_NONE',
        [u'TYPE_NONE', u'TYPE_X509_PEM_FILE', u'TYPE_RAW_PUBLIC_KEY'],
        u'The output format of the public key requested. X509_PEM is the '
        u'default output format.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Gets the ServiceAccountKey by key id.

    Args:
      name: The resource name of the service account key in the following
        format: `projects/{project}/serviceAccounts/{account}/keys/{key}`.
        Using `-` as a wildcard for the project will infer the project from
        the account. The `account` value can be the `email` address or the
        `unique_id` of the service account.

    Flags:
      publicKeyType: The output format of the public key requested. X509_PEM
        is the default output format.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsKeysGetRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['publicKeyType'].present:
      request.publicKeyType = messages.IamProjectsServiceAccountsKeysGetRequest.PublicKeyTypeValueValuesEnum(FLAGS.publicKeyType)
    result = client.projects_serviceAccounts_keys.Get(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class ProjectsServiceAccountsKeysList(apitools_base_cli.NewCmd):
  """Command wrapping projects_serviceAccounts_keys.List."""

  usage = """projects_serviceAccounts_keys_list <name>"""

  def __init__(self, name, fv):
    super(ProjectsServiceAccountsKeysList, self).__init__(name, fv)
    flags.DEFINE_enum(
        'keyTypes',
        u'KEY_TYPE_UNSPECIFIED',
        [u'KEY_TYPE_UNSPECIFIED', u'USER_MANAGED', u'SYSTEM_MANAGED'],
        u'Filters the types of keys the user wants to include in the list '
        u'response. Duplicate key types are not allowed. If no key type is '
        u'provided, all keys are returned.',
        flag_values=fv)

  def RunWithArgs(self, name):
    """Lists ServiceAccountKeys.

    Args:
      name: The resource name of the service account in the following format:
        `projects/{project}/serviceAccounts/{account}`.  Using `-` as a
        wildcard for the project, will infer the project from the account. The
        `account` value can be the `email` address or the `unique_id` of the
        service account.

    Flags:
      keyTypes: Filters the types of keys the user wants to include in the
        list response. Duplicate key types are not allowed. If no key type is
        provided, all keys are returned.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.IamProjectsServiceAccountsKeysListRequest(
        name=name.decode('utf8'),
        )
    if FLAGS['keyTypes'].present:
      request.keyTypes = [messages.IamProjectsServiceAccountsKeysListRequest.KeyTypesValueValuesEnum(x) for x in FLAGS.keyTypes]
    result = client.projects_serviceAccounts_keys.List(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


class RolesQueryGrantableRoles(apitools_base_cli.NewCmd):
  """Command wrapping roles.QueryGrantableRoles."""

  usage = """roles_queryGrantableRoles"""

  def __init__(self, name, fv):
    super(RolesQueryGrantableRoles, self).__init__(name, fv)
    flags.DEFINE_string(
        'fullResourceName',
        None,
        u'Required. The full resource name to query from the list of '
        u'grantable roles.  The name follows the Google Cloud Platform '
        u'resource format. For example, a Cloud Platform project with id `my-'
        u'project` will be named '
        u'`//cloudresourcemanager.googleapis.com/projects/my-project`.',
        flag_values=fv)

  def RunWithArgs(self):
    """Queries roles that can be granted on a particular resource.

    Flags:
      fullResourceName: Required. The full resource name to query from the
        list of grantable roles.  The name follows the Google Cloud Platform
        resource format. For example, a Cloud Platform project with id `my-
        project` will be named `//cloudresourcemanager.googleapis.com/projects
        /my-project`.
    """
    client = GetClientFromFlags()
    global_params = GetGlobalParamsFromFlags()
    request = messages.QueryGrantableRolesRequest(
        )
    if FLAGS['fullResourceName'].present:
      request.fullResourceName = FLAGS.fullResourceName.decode('utf8')
    result = client.roles.QueryGrantableRoles(
        request, global_params=global_params)
    print apitools_base_cli.FormatOutput(result)


def main(_):
  appcommands.AddCmd('pyshell', PyShell)
  appcommands.AddCmd('iamPolicies_getPolicyDetails', IamPoliciesGetPolicyDetails)
  appcommands.AddCmd('projects_serviceAccounts_create', ProjectsServiceAccountsCreate)
  appcommands.AddCmd('projects_serviceAccounts_delete', ProjectsServiceAccountsDelete)
  appcommands.AddCmd('projects_serviceAccounts_get', ProjectsServiceAccountsGet)
  appcommands.AddCmd('projects_serviceAccounts_getIamPolicy', ProjectsServiceAccountsGetIamPolicy)
  appcommands.AddCmd('projects_serviceAccounts_list', ProjectsServiceAccountsList)
  appcommands.AddCmd('projects_serviceAccounts_setIamPolicy', ProjectsServiceAccountsSetIamPolicy)
  appcommands.AddCmd('projects_serviceAccounts_signBlob', ProjectsServiceAccountsSignBlob)
  appcommands.AddCmd('projects_serviceAccounts_signJwt', ProjectsServiceAccountsSignJwt)
  appcommands.AddCmd('projects_serviceAccounts_testIamPermissions', ProjectsServiceAccountsTestIamPermissions)
  appcommands.AddCmd('projects_serviceAccounts_update', ProjectsServiceAccountsUpdate)
  appcommands.AddCmd('projects_serviceAccounts_keys_create', ProjectsServiceAccountsKeysCreate)
  appcommands.AddCmd('projects_serviceAccounts_keys_delete', ProjectsServiceAccountsKeysDelete)
  appcommands.AddCmd('projects_serviceAccounts_keys_get', ProjectsServiceAccountsKeysGet)
  appcommands.AddCmd('projects_serviceAccounts_keys_list', ProjectsServiceAccountsKeysList)
  appcommands.AddCmd('roles_queryGrantableRoles', RolesQueryGrantableRoles)

  apitools_base_cli.SetupLogger()
  if hasattr(appcommands, 'SetDefaultCommand'):
    appcommands.SetDefaultCommand('pyshell')


run_main = apitools_base_cli.run_main

if __name__ == '__main__':
  appcommands.Run()
