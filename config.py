import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'ssshare_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # ssshare config
    APP_ALG = 'HS256'
    DEFAUT_PORT = 8383
    AUTH_EXP = 30 * 60
    DEFAULT_IP = '127.0.0.1'

    @staticmethod
    def init_app(app):
        pass


class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATA_BASE') or \
        'sqlite:////' + os.path.join(basedir, 'data/ssshare.db')


class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATA_BASE') or \
        'sqlite:////' + os.path.join(basedir, 'data/ssshare.db')

config = {
    'product': ProductConfig,
    'develop': DevelopConfig,
    'default': DevelopConfig
}
