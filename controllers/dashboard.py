from flask import Blueprint, request, session, render_template, redirect
from database.schema import ExpeditionBase, ExpeditionLog, Wanderer, db
from datetime import datetime

dash_bp = Blueprint('dash', __name__, url_prefix='/dash')

@dash_bp.route('/overseer')
def overseer_dash():
    if session.get('role') != 'overseer': return redirect('/login')
    
    search_q = request.args.get('q', '').strip()
    
    # Build filtered queries based on search
    if search_q:
        exps = ExpeditionBase.query.filter(
            db.or_(
                ExpeditionBase.title.ilike(f'%{search_q}%'),
                ExpeditionBase.locale.ilike(f'%{search_q}%'),
                ExpeditionBase.eid.ilike(f'%{search_q}%')
            )
        ).all()
        users = Wanderer.query.filter(
            Wanderer.role_type != 'overseer',
            db.or_(
                Wanderer.alias.ilike(f'%{search_q}%'),
                Wanderer.id.ilike(f'%{search_q}%')
            )
        ).all()
    else:
        exps = ExpeditionBase.query.all()
        users = Wanderer.query.filter(Wanderer.role_type != 'overseer').all()
    
    masters = Wanderer.query.filter_by(role_type='master').all()
    all_logs = ExpeditionLog.query.all()
    
    # Summary stats (always total, not filtered)
    total_treks = ExpeditionBase.query.count()
    total_users = Wanderer.query.filter_by(role_type='explorer').count()
    total_staff = Wanderer.query.filter_by(role_type='master').count()
    total_bookings = ExpeditionLog.query.count()
    
    return render_template('overseer_dash.html',
        expeditions=exps, users=users, masters=masters, all_logs=all_logs,
        total_treks=total_treks, total_users=total_users, total_staff=total_staff,
        total_bookings=total_bookings, search_q=search_q)

@dash_bp.route('/add_expedition', methods=['POST'])
def add_expedition():
    if session.get('role') != 'overseer': return redirect('/login')
    dur = request.form.get('duration')
    e = ExpeditionBase(
        title=request.form.get('title'),
        locale=request.form.get('locale'),
        challenge=request.form.get('challenge'),
        max_wanderers=int(request.form.get('max')),
        current_slots=int(request.form.get('max')),
        duration=int(dur) if dur else None,
        launch_date=datetime.strptime(request.form.get('launch'), '%Y-%m-%d'),
        end_date=datetime.strptime(request.form.get('end'), '%Y-%m-%d'),
        current_phase='Open',
        master_id=request.form.get('master_id') or None
    )
    db.session.add(e)
    db.session.commit()
    return redirect('/dash/overseer')

@dash_bp.route('/edit_expedition/<int:eid>', methods=['GET', 'POST'])
def edit_expedition(eid):
    if session.get('role') != 'overseer': return redirect('/login')
    e = ExpeditionBase.query.get_or_404(eid)
    if request.method == 'POST':
        e.title = request.form.get('title')
        e.locale = request.form.get('locale')
        e.challenge = request.form.get('challenge')
        e.max_wanderers = int(request.form.get('max'))
        e.current_slots = int(request.form.get('current_slots'))
        dur = request.form.get('duration')
        e.duration = int(dur) if dur else None
        e.launch_date = datetime.strptime(request.form.get('launch'), '%Y-%m-%d')
        e.end_date = datetime.strptime(request.form.get('end'), '%Y-%m-%d')
        e.current_phase = request.form.get('phase')
        e.master_id = request.form.get('master_id') or None
        db.session.commit()
        return redirect('/dash/overseer')
    masters = Wanderer.query.filter_by(role_type='master').all()
    return render_template('edit_expedition.html', expedition=e, masters=masters)

@dash_bp.route('/delete_expedition/<int:eid>', methods=['POST'])
def delete_expedition(eid):
    if session.get('role') != 'overseer': return redirect('/login')
    e = ExpeditionBase.query.get_or_404(eid)
    # Delete associated logs first
    ExpeditionLog.query.filter_by(expedition_id=eid).delete()
    db.session.delete(e)
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
    # Load participants for each expedition
    exp_participants = {}
    for e in exps:
        logs = ExpeditionLog.query.filter_by(expedition_id=e.eid).all()
        exp_participants[e.eid] = logs
    return render_template('master_dash.html', expeditions=exps, exp_participants=exp_participants)

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
    challenge = request.args.get('challenge', '')
    
    # Base query: show treks that are Open
    query = ExpeditionBase.query.filter(ExpeditionBase.current_phase == 'Open')
    
    # Filter by location search
    if q:
        query = query.filter(ExpeditionBase.locale.ilike(f'%{q}%'))
    
    # Filter by difficulty/challenge
    if challenge:
        query = query.filter(ExpeditionBase.challenge == challenge)
    
    exps = query.all()
    
    logs = ExpeditionLog.query.filter_by(wanderer_id=session['w_id']).all()
    log_ids = [l.expedition_id for l in logs]
    return render_template('explorer_dash.html', expeditions=exps, logs=logs, q=q, challenge=challenge, log_ids=log_ids)

@dash_bp.route('/join/<int:eid>', methods=['POST'])
def join(eid):
    if session.get('role') != 'explorer': return redirect('/login')
    e = ExpeditionBase.query.get(eid)
    if e and e.current_slots > 0 and e.current_phase == 'Open':
        e.current_slots -= 1
        l = ExpeditionLog(wanderer_id=session['w_id'], expedition_id=eid, status='Booked')
        db.session.add(l)
        db.session.commit()
    return redirect('/dash/explorer')
