import os
from flask import Flask, redirect, request
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, login_manager, oauth
from routes.core import core_bp
from routes.auth import auth_bp
from routes.billing import billing_bp
from models import User

def create_app() -> Flask:
    # Ukazujeme Flasku na složku templates o úroveň výš
    app = Flask(__name__, template_folder='../templates')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.json.ensure_ascii = False
    
    # Configuration loading
    app.config.update(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(os.getcwd(), 'temp_uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        ALLOWED_EXTENSIONS={'pdf'}
    )

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def handle_redirects():
        if request.host.startswith('www.'):
            return redirect(request.url.replace('www.', '', 1), code=301)

    # Register Blueprints with logic
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(billing_bp)

    return app

app = create_app()

# Tohle se teď spustí vždycky, i na produkci pod Gunicornem
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)