from flask import Blueprint, request, session, render_template, redirect
from database.schema import Wanderer, db

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/')
def index():
    return redirect('/login')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        alias = request.form.get('alias')
        sec = request.form.get('secret')
        user = Wanderer.query.filter_by(alias=alias).first()
        if user and user.verify_secret(sec):
            if not user.active: return render_template('login.html', error='Account banned')
            if user.role_type == 'master' and not user.is_approved: return render_template('login.html', error='Not approved')
            session['w_id'] = user.id
            session['role'] = user.role_type
            if user.role_type == 'overseer': return redirect('/dash/overseer')
            elif user.role_type == 'master': return redirect('/dash/master')
            else: return redirect('/dash/explorer')
        return render_template('login.html', error='Invalid')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        alias = request.form.get('alias')
        sec = request.form.get('secret')
        role = request.form.get('role')
        if Wanderer.query.filter_by(alias=alias).first():
            return render_template('register.html', error='Exists')
        w = Wanderer(alias=alias, role_type=role, active=True, is_approved=(role=='explorer'))
        w.hash_secret(sec)
        db.session.add(w)
        db.session.commit()
        if role == 'explorer':
            session['w_id'] = w.id
            session['role'] = role
            return redirect('/dash/explorer')
        return redirect('/login')
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')