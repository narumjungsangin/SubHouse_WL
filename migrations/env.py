import logging
from logging.config import fileConfig

from alembic import context
from app import create_app
from models import db

# Flask 앱 인스턴스 생성
app = create_app()

# Alembic이 Flask 앱 컨텍스트 내에서 실행되도록 설정
with app.app_context():

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    fileConfig(config.config_file_name)
    logger = logging.getLogger('alembic.env')








    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    target_metadata = db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.





    def run_migrations_offline():
        """Run migrations in 'offline' mode."""
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url, target_metadata=target_metadata, literal_binds=True
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
