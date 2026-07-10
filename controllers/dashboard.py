from flask import Blueprint, request, session, render_template, redirect
from database.schema import ExpeditionBase, ExpeditionLog, Wanderer, db
from datetime import datetime

dash_bp = Blueprint('dash', __name__, url_prefix='/dash')

@dash_bp.route('/overseer')
def overseer_dash():
    if session.get('role') != 'overseer': return redirect('/login')
    exps = ExpeditionBase.query.all()
    users = Wanderer.query.filter(Wanderer.role_type != 'overseer').all()
    masters = Wanderer.query.filter_by(role_type='master').all()
    return render_template('overseer_dash.html', expeditions=exps, users=users, masters=masters)

@dash_bp.route('/add_expedition', methods=['POST'])
def add_expedition():
    if session.get('role') != 'overseer': return redirect('/login')
    e = ExpeditionBase(
        title=request.form.get('title'),
        locale=request.form.get('locale'),
        challenge=request.form.get('challenge'),
        max_wanderers=int(request.form.get('max')),
        current_slots=int(request.form.get('max')),
        launch_date=datetime.strptime(request.form.get('launch'), '%Y-%m-%d'),
        end_date=datetime.strptime(request.form.get('end'), '%Y-%m-%d'),
        current_phase='Open',
        master_id=request.form.get('master_id') or None
    )
    db.session.add(e)
    db.session.commit()
    return redirect('/dash/overseer')

@dash_bp.route('/approve/<int:wid>', methods=['POST'])
def approve(wid):
    if session.get('role') != 'overseer': return redirect('/login')
    w = Wanderer.query.get(wid)
    if w:
        w.is_approved = True
        db.session.commit()
    return redirect('/dash/overseer')

@dash_bp.route('/ban/<int:wid>', methods=['POST'])
def ban(wid):
    if session.get('role') != 'overseer': return redirect('/login')
    w = Wanderer.query.get(wid)
    if w:
        w.active = False
        db.session.commit()
    return redirect('/dash/overseer')

@dash_bp.route('/master')
def master_dash():
    if session.get('role') != 'master': return redirect('/login')
    exps = ExpeditionBase.query.filter_by(master_id=session['w_id']).all()
    return render_template('master_dash.html', expeditions=exps)

@dash_bp.route('/update_exp/<int:eid>', methods=['POST'])
def update_exp(eid):
    if session.get('role') != 'master': return redirect('/login')
    e = ExpeditionBase.query.get(eid)
    if e and e.master_id == session['w_id']:
        e.current_phase = request.form.get('phase')
        e.current_slots = int(request.form.get('slots'))
        db.session.commit()
    return redirect('/dash/master')

@dash_bp.route('/explorer')
def explorer_dash():
    if session.get('role') != 'explorer': return redirect('/login')
    q = request.args.get('q', '')
    if q:
        exps = ExpeditionBase.query.filter(ExpeditionBase.current_phase == 'Open', ExpeditionBase.locale.ilike(f'%{q}%')).all()
    else:
        exps = ExpeditionBase.query.filter_by(current_phase='Open').all()
    logs = ExpeditionLog.query.filter_by(wanderer_id=session['w_id']).all()
    log_ids = [l.expedition_id for l in logs]
    return render_template('explorer_dash.html', expeditions=exps, logs=logs, q=q, log_ids=log_ids)

@dash_bp.route('/join/<int:eid>', methods=['POST'])
def join(eid):
    if session.get('role') != 'explorer': return redirect('/login')
    e = ExpeditionBase.query.get(eid)
    if e and e.current_slots > 0 and e.current_phase == 'Open':
        e.current_slots -= 1
        l = ExpeditionLog(wanderer_id=session['w_id'], expedition_id=eid)
        db.session.add(l)
        db.session.commit()
    return redirect('/dash/explorer')
