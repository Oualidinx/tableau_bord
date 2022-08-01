from flask import flash, redirect, render_template, url_for, request, jsonify, session, abort
from main_app import database
from flask_login import current_user, login_required
from main_app.admin import admin_bp
from werkzeug.security import generate_password_hash
from main_app.forms import RegisterForm, ServiceForm, EditEmpForm, AggregateForm
from main_app.models import User, Service, Aggregate
from sqlalchemy.sql import or_


@admin_bp.before_request
def admin_before_request():
    session['actual_role'] = "Master"
    if not current_user.is_authenticated or current_user.role != "Master":
        return render_template('401.html')


@admin_bp.get('/')
@login_required
def index():
    return render_template("master_dashboard.html")


""""""""""""""""""""
#   LES EMPLOYEES  #
""""""""""""""""""""


@admin_bp.get('/employees')
@admin_bp.post('/employees')
@login_required
def employees():
    form_add = RegisterForm()
    form_add.service.choices = [(-1, 'Sélectionner le service ...')] + [(x.id, x.label) for x in
                                                                        Service.query.filter_by(is_deleted=0).all()]
    if form_add.validate_on_submit():
        user = User()
        user.username = form_add.username.data
        user.password_hash = generate_password_hash(form_add.password.data, "sha256")
        user.role = "employee" if int(form_add.role.data) == 1 else "Master"
        user.service_id = int(form_add.service.data) if int(form_add.service.data) != -1 else None
        database.session.add(user)
        database.session.commit()
        flash("utilisateur ajouté avec succès", "success")
        return redirect(url_for("admin_bp.employees"))
    print(form_add.errors)
    return render_template('employees.html', form=form_add)


@admin_bp.route('/employees/data', methods=['POST'])
def edit_emp(_id):
    _data = request.get_json()
    if 'id' not in _data:
        abort(400)
    srv = User.query.get(_data['id'])
    setattr(srv, 'label', _data['label'])
    database.session.commit()
    return '', 204


@admin_bp.get('/employees/delete/<int:_id>')
@login_required
def delete_emp(_id):
    user = User.query.get(_id)
    if not _id or not user:
        return render_template('404.html')
    user.is_deleted = 1
    database.session.add(user)
    database.session.commit()
    return redirect(url_for('admin_bp.employees'))


@admin_bp.route('/employees/data')
@login_required
def get_emps():
    query = User.query.filter_by(is_deleted=0)
    search = request.args.get('search')
    if search:
        query = query.filter(or_(User.role.like(f'%{search}%'), User.username.like(f'%{search}%')))
    total = query.count()
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            # name = 'label'
            col = getattr(Service, name)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    return {
               'data': [srv.to_dict() for srv in query],
               'total': total,
           }, 200


""""""""""""""""""""
#   LES SERVICES   #
""""""""""""""""""""


@admin_bp.post('/services/add')
@admin_bp.get('/services/add')
def add_service():
    form_add = ServiceForm()
    if form_add.validate_on_submit():
        srv = Service()
        srv.label = form_add.label.data
        database.session.add(srv)
        database.session.commit()
        flash("Service ajouté avec succès", "success")
        return redirect(url_for("admin_bp.services"))
    # @admin_bp.post('/services/edit/<int:_id')admin_bp.services", page=1))
    return render_template('services.html', form=form_add)


@admin_bp.route('/services')
@login_required
def services():
    return render_template('services.html', form=ServiceForm())


@admin_bp.route('/data')
@login_required
def get_data():
    # print('executed!')
    query = Service.query.filter_by(is_deleted=0)
    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(Service.label.like(f'%{search}%'))
    total = query.count()
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            # name = s[1:]
            name = 'label'
            col = getattr(Service, name)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    # print({
    #     'data': [srv.to_dict() for srv in query],
    #     'total': total,
    # })
    return {
               'data': [srv.to_dict() for srv in query],
               'total': total,
           }, 200


@admin_bp.route('/services/data', methods=['POST'])
@login_required
def update_data():
    _data = request.get_json()
    if 'id' not in _data:
        abort(400)
    srv = Service.query.get(_data['id'])
    setattr(srv, 'label', _data['label'])
    database.session.commit()
    return '', 204


@admin_bp.get('/services/delete/<int:_id>')
@login_required
def delete_service(_id):
    service = Service.query.get(_id)
    if not _id or not service:
        return render_template('404.html')
    service.is_deleted = 1
    database.session.add(service)
    database.session.commit()
    flash(f'service {service.label} supprimé', 'success')
    return redirect(url_for('admin_bp.services', page=1))


""""""""""""""""""
#   AGGREGATES   #
""""""""""""""""""


@admin_bp.route('/aggregates/data')
@login_required
def get_aggregates():
    query = Aggregate.query.filter_by(is_deleted=0)
    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(or_(Aggregate.label.like(f'%{search}%'), Aggregate.code == int(search)))
    total = query.count()
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            # name = 'label'
            col = getattr(Aggregate, name)
            if direction == '-':
                col = col.desc()
            order.append(col)
        if order:
            query = query.order_by(*order)

    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    # print({
    #     'data': [srv.to_dict() for srv in query],
    #     'total': total,
    # })
    return {
               'data': [obj.to_dict() for obj in query],
               'total': total,
           }, 200


@admin_bp.route('/aggregates/data', methods=['POST'])
@login_required
def update_aggregate():
    _data = request.get_json()
    if 'id' not in _data:
        abort(400)
    agg = Aggregate.query.get(_data['id'])
    setattr(agg, 'label', _data['label'])
    setattr(agg, 'code', _data['code'])
    database.session.commit()
    return '', 204


@admin_bp.get('/aggregates')
@admin_bp.post('/aggregates')
@login_required
def aggregates():
    print('add_aggregate')
    form_add = AggregateForm()
    form_add.service.choices = [(-1, 'Choisir un service')] + [(srv.id, srv.label) for srv in
                                                               Service.query.filter_by(is_deleted=0).all()]
    if form_add.validate_on_submit():
        agg = Aggregate()
        agg.label = form_add.label.data
        agg.code = int(form_add.code.data)
        agg.service_id = int(form_add.service.data)
        database.session.add(agg)
        database.session.commit()
        flash("Aggregat ajouté avec succès", "success")
        return redirect(url_for("admin_bp.aggregates"))
    return render_template('aggregates.html', form=form_add)


#
# @admin_bp.get('/aggregates/add')
# @login_required
# def add_aggregate():
#     print('add_aggregate')
#     form_add = AggregateForm()
#     form_add.service.choices = [(-1, 'Choisir un service')] + [(srv.id, srv.label) for srv in
#                                                                Service.query.filter_by(is_deleted=0).all()]
#     if form_add.validate_on_submit():
#         agg = Aggregate()
#         agg.label = form_add.label.data
#         agg.code = int(form_add.code.data)
#         agg.service_id = int(form_add.service.data)
#         database.session.add(agg)
#         database.session.commit()
#         flash("Aggregat ajouté avec succès", "success")
#         return redirect(url_for("admin_bp.aggregates"))
#     return render_template('aggregates.html', form=form_add)


@admin_bp.get('/aggregates/delete/<int:_id>')
@login_required
def delete_aggregate(_id):
    aggregat = Aggregate.query.get(_id)
    if not _id or not aggregat:
        return render_template('404.html')
    aggregat.is_deleted = 1
    database.session.add(aggregat)
    database.session.commit()
    flash(f'aggregat {aggregat.label} supprimé', 'success')
    return redirect(url_for('admin_bp.aggregates'))


@admin_bp.get("/hashes/username")
@login_required
def generate_username():
    import secrets
    _hash = secrets.token_hex(10)
    user = User.query.filter_by(username=_hash).first()
    if user:
        return {"error": 409}
    return {"hash": _hash}


@admin_bp.get("/hashes/password")
@login_required
def generate_password():
    import secrets
    return {"hash": secrets.token_hex(10)}
