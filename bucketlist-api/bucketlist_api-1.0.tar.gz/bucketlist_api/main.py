"""
Main bucketlist module
"""

from datetime import timedelta
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt import JWT
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from bucketlist_api.models import User
from bucketlist_api.resources.bucketlist_resource \
    import BucketListsAPI, BucketListItemAPI, BucketItemsAPI, BucketItemAPI
from bucketlist_api.resources.user_resource \
    import RegisterUserAPI, LoginUserAPI
import config

# create the app
def create_app(config_env):
    """
    Creates the application
    """
    app = Flask(__name__)
    # Configure the application to run on the set environmnent
    app.config['SECRET_KEY'] = config_env.SECRET_KEY
    app.config['JWT_EXPIRATION_DELTA'] = config_env.JWT_EXPIRATION_DELTA
    app.config['JWT_AUTH_USERNAME_KEY'] = config_env.JWT_AUTH_USERNAME_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config_env.SQLALCHEMY_DATABASE_URI
    return app

# create app based on the environment, default is production
environment = os.getenv('ENV_SETUP', None)
if environment == 'config.DevelopmentConfig':
    APP = create_app(config.DevelopmentConfig)
elif environment == 'config.TestingConfig':
    APP = create_app(config.TestingConfig)
else:
    APP = create_app(config.ProductionConfig)
@APP.errorhandler(500)
def resource_not_found(e):
    return {
        'error': {'message': 'Resource not found'}
    }, 404

BCRYPT = Bcrypt(APP)
API = Api(APP)

def authenticate(email, password):
    """
    Performs verification on provided credentials
    """
    user = User.query.filter_by(email=email).first()
    return user if user.confirm_password(password) else False

def identify(payload):
    """
    Gets the user id
    """
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first()

jwt = JWT(APP, authenticate, identify)

# Add routes to resources
API.add_resource(LoginUserAPI, '/auth/login', endpoint='login')
API.add_resource(RegisterUserAPI, '/auth/register', endpoint='register')
API.add_resource(BucketListsAPI, '/bucketlists/', endpoint='bucketlists')
API.add_resource(BucketListItemAPI, '/bucketlists/<int:bucketlist_id>', endpoint='bucketlist')
API.add_resource(BucketItemsAPI, '/bucketlists/<int:bucketlist_id>/items/', endpoint='items')
API.add_resource(BucketItemAPI, '/bucketlists/<int:bucketlist_id>/items/<int:item_id>', endpoint='item')

if __name__ == "__main__":
    APP.run()
