from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Wanderer(db.Model):
    __tablename__ = 'wanderers'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(80), unique=True, nullable=False)
    secret = db.Column(db.String(255), nullable=False)
    role_type = db.Column(db.String(20), default='explorer') # 'explorer', 'master', 'overseer'
    contact_email = db.Column(db.String(150), nullable=True)
    active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=True)

    def hash_secret(self, raw_secret):
        self.secret = generate_password_hash(raw_secret, method='scrypt')
    
    def verify_secret(self, raw_secret):
        return check_password_hash(self.secret, raw_secret)

class ExpeditionBase(db.Model):
    __tablename__ = 'expeditions'
    eid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    locale = db.Column(db.String(100), nullable=False)
    challenge = db.Column(db.String(50), nullable=False)
    max_wanderers = db.Column(db.Integer, nullable=False)
    current_slots = db.Column(db.Integer, nullable=False)
    launch_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    current_phase = db.Column(db.String(50), default='Planning') # Planning, Open, Closed, Finished
    master_id = db.Column(db.Integer, db.ForeignKey('wanderers.id'), nullable=True)
    
    master = db.relationship('Wanderer', backref='managed_expeditions', foreign_keys=[master_id])

class ExpeditionLog(db.Model):
    __tablename__ = 'expedition_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    wanderer_id = db.Column(db.Integer, db.ForeignKey('wanderers.id', ondelete='CASCADE'))
    expedition_id = db.Column(db.Integer, db.ForeignKey('expeditions.eid', ondelete='CASCADE'))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    wanderer = db.relationship('Wanderer', backref=db.backref('logs', cascade='all, delete-orphan'), foreign_keys=[wanderer_id])
    expedition = db.relationship('ExpeditionBase', backref=db.backref('logs', cascade='all, delete-orphan'))
