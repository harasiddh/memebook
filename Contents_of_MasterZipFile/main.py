import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig  # TestingConfig
from application.database import db
from flask_security import Security, SQLAlchemyUserDatastore, SQLAlchemySessionUserDatastore
from application.models import User
from flask_migrate import Migrate

app = None
api = None


def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', 'development') == 'production':
        app.logger.info("Currently no production environment is setup")
        raise Exception("Currently no production environment is setup")
    # '''elif os.getenv('ENV', 'development') == 'testing':
    #   app.logger.info("Starting Testing")
    #   print("Starting Testing")
    #   app.config.from_object(TestingConfig)'''
    else:
        app.logger.info("Starting Local Development")
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    # migrate = Migrate(app)
    api = Api(app)
    app.app_context().push()
    '''user_datastore = SQLAlchemyUserDatastore(db.session, User)
    security = Security(app, user_datastore)
    app.logger.info("App setup complete")'''
    return app, api


app, api = create_app()
# app, api = create_app()


# Import all controllers so that they are loaded
from application.controllers import *

# Add all restful controllers
from application.api import UserAPI, MemeAPI
api.add_resource(UserAPI, "/api/user/<string:username>", "/api/user")
api.add_resource(MemeAPI, "/api/meme/<int:id>", "/api/meme")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
