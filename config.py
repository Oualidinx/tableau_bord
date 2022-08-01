class Config:
    SECRET_KEY = '43be06758c598379d184b0dccfa1968cd5444c608c7cb8dfb4298dcf56febd75'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Development(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI="postgresql://oualid:1091eb5a6c62@localhost/tableau_bord"
    # SQLALCHEMY_DATABASE_URI = "sqlite:///dev.sqlite"


config = {
    "development": Development
}
