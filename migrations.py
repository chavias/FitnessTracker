import subprocess
import os
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def run_migrations():

    db_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///fitness.db')
    
    # Check if we need to run migrations
    engine = create_engine(db_url)
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    
    if context.get_current_revision() is None:
        # No migrations have been run, so run initial migration
        print('Running initial migration')
        subprocess.run(['flask', 'db', 'init'])
        subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration'])
        subprocess.run(['flask', 'db', 'upgrade'])
    else:
        # Check if we need to run new migrations
        print('Running migrations')
        subprocess.run(['flask', 'db', 'migrate', '-m', 'Auto-migration'])
        subprocess.run(['flask', 'db', 'upgrade'])
    
    conn.close()

if __name__ == '__main__':
    run_migrations()