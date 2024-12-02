import os
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_MEMES_DIR = None
    ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif'}

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, '../db_directory')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "testdb.sqlite3")
    UPLOADED_MEMES_DIR = os.path.join(basedir, '../static/uploaded_memes')
    print(UPLOADED_MEMES_DIR)
    DEBUG = True

