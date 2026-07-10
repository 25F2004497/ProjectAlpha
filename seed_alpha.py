import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import build_app
from database.schema import db, Wanderer

app = build_app()
with app.app_context():
    if not Wanderer.query.filter_by(alias='john_explorer').first():
        w1 = Wanderer(alias='john_explorer', role_type='explorer')
        w1.hash_secret('password123')
        
        m1 = Wanderer(alias='mike_master', role_type='master')
        m1.hash_secret('password123')
        
        m2= Wanderer (alias='treklord', role_type='master')
        m2.hash_secret('password123')
        
        db.session.add_all([w1, m1])
        db.session.commit()
        print("Alpha Seeded.")
    else:
        print("Alpha Already Seeded.")
