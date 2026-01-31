import os
from app import create_app, db

# Use a local SQLite database for dev run to avoid MySQL setup
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///dev.db')

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Initialized SQLite database at', app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(debug=True)
