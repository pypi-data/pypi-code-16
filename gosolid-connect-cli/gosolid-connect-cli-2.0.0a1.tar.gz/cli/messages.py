AWS_INCORRECT_CONFIGURATION = 'Your AWS CLI is configured incorrectly. Please run "aws configure" and '\
    're-enter your credentials. If you do not have an access'
ERR_DOCKER_LAUNCH = 'Docker failed to start. If the error states "port is already allocated", check Kitematic for'\
    'other environments that may already be running on that port / IP'
ERR_INIT_ERROR_EXISTS = 'Development environment already exists at this location. Exiting.'
ERR_INVALID_ENVIRONMENT = 'Invalid environment. Please try again.'
ERR_MUST_STOP_BOX = 'Your environment is running. Stop it by running "connect docker stop" before attempting to remove.'
ERR_NO_ENVIRONMENT = 'Environment not yet built. Please run "connect init -p %s" to create one.'
SUCCESS_INIT = 'Congratulations! Your %s dev environment is built! Starting...'
SUCCESS_START = 'Your development environment has started and is now accessible at %s'
SUCCESS_STOP = 'Docker environment stopped successfully.'