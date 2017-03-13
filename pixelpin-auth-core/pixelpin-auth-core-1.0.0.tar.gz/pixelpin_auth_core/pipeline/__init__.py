DEFAULT_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'pixelpin_auth_core.pipeline.pixelpin_auth.pixelpin_auth_details',

    # Get the pixelpin_auth uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'pixelpin_auth_core.pipeline.pixelpin_auth.pixelpin_auth_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'pixelpin_auth_core.pipeline.pixelpin_auth.auth_allowed',

    # Checks if the current pixelpin_auth-account is already associated in the site.
    'pixelpin_auth_core.pipeline.pixelpin_auth.pixelpin_auth_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'pixelpin_auth_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # 'pixelpin_auth_core.pipeline.mail.mail_validation',

    # Associates the current pixelpin_auth details with another user account with
    # a similar email address.
    'pixelpin_auth_core.pipeline.pixelpin_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'pixelpin_auth_core.pipeline.user.create_user',

    # Create the record that associated the pixelpin_auth account with this user.
    'pixelpin_auth_core.pipeline.pixelpin_auth.associate_user',

    # Populate the extra_data field in the pixelpin_auth record with the values
    # specified by settings (and the default ones like access_token, etc).
    'pixelpin_auth_core.pipeline.pixelpin_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'pixelpin_auth_core.pipeline.user.user_details'
)

DEFAULT_DISCONNECT_PIPELINE = (
    # Verifies that the pixelpin_auth association can be disconnected from the current
    # user (ensure that the user login mechanism is not compromised by this
    # disconnection).
    'pixelpin_auth_core.pipeline.disconnect.allowed_to_disconnect',

    # Collects the pixelpin_auth associations to disconnect.
    'pixelpin_auth_core.pipeline.disconnect.get_entries',

    # Revoke any access_token when possible.
    'pixelpin_auth_core.pipeline.disconnect.revoke_tokens',

    # Removes the pixelpin_auth associations.
    'pixelpin_auth_core.pipeline.disconnect.disconnect'
)
