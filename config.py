import os 
import dotenv

if not ".env" in os.listdir():
    with open(".env", "w") as f:
        for key, value in os.environ.items():
            if ")" in value:
                continue
            f.write(f"{key}={value}\n")

dotenv.load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
URL_BOT = os.environ.get("URL_BOT")
if os.environ.get("ADMIN"):
    ADMINS_ID = list(map(int, [os.environ.get("ADMIN")]))

class Config(object):
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    SECRET_KEY = os.getenv('SECRET_KEY')

    MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
    MYSQL_ROOT = os.getenv('MYSQL_ROOT')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True if os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') else False


class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}[os.getenv('FLASK_CONFIG')]


api_key = os.getenv('KUCOIN_API_KEY')
api_secret = os.getenv('KUCOIN_API_SECRET')
api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')

assert api_key and api_secret and api_passphrase 