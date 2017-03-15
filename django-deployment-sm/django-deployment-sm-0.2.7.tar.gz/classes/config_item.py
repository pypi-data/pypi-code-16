from classes.exceptions import DeploymentException


class ConfigItem(object):
    """

    A deployment item describe a deployment type in the django-deploy.json

    Example:
        {
    --->  "prod": {
            "host": "google.com",
            "deploy_dir": "/var/www/test",
            "branch": "master"
          }
        }

    """

    def __init__(self, deployment_type, values):
        """
        Init the object with all values in the deployment type
        So the values like in the example from above would be:
        - host
        - deploy_dir
        - branch
        if the value is another dictionary it will be treated as another configitem with values

        :param deployment_type: the deployment type of current config item
        :param values: the dictionary of values
        """
        self.deployment_type = deployment_type
        for key, value in values.items():
            if isinstance(value, dict):
                setattr(self, key, ConfigItem(key, value))
            else:
                setattr(self, key, value)

    def __getattribute__(self, item):
        """
        Overwrite the getattribute function to raise the DeploymentException if an item wasn't found

        :param item:
        :return:
        """
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            raise DeploymentException(
                'Item \"{item}\" was not found in your django-deploy.json\n'
                'Please define the attribute in your deployment type: {deployment_type}'.format(
                    item=item,
                    deployment_type=self.deployment_type,
                )
            )

    def get_services_list(self):
        services_list = []
        for service in self.services.__dict__.keys():
            if service not in ['None', 'deployment_type']:
                services_list.append(service)
        return services_list
