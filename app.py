from flask import Flask  # type: ignore[import]
from database.schema import db, Wanderer
import os

def build_app():
    app = Flask(__name__, template_folder='frontend_views', static_folder='public_assets')
    
    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, 'alpha_store_v2.sqlite3')}"
    app.config['SECRET_KEY'] = 'alpha_glassmorphism_secret'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register controllers (Blueprints)
    from controllers.auth import auth_bp
    from controllers.dashboard import dash_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)

    return app

if __name__ == '__main__':
    app = build_app()
    with app.app_context():
        db.create_all()
        # Ensure Overseer (Admin) exists
        if not Wanderer.query.filter_by(alias='overseer').first():
            admin = Wanderer(alias='overseer', role_type='overseer', contact_email='admin@alpha.net')
            admin.hash_secret('overseer')
            db.session.add(admin)
            db.session.commit()
            
    print("Project Alpha Server Booting on port 8111...")
    app.run(debug=True, port=8111)
