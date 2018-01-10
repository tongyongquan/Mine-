# encoding: utf-8
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from Mine import app,db
from models import *

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
