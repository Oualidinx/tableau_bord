from flask import url_for, request, session, render_template, flash, redirect
from flask_login import current_user, login_required
from main_app import database
from main_app.employee import employee_bp
from main_app.models import Aggregate, Value
from main_app.forms import ValueForm
from sqlalchemy.sql import or_, and_


@employee_bp.before_request
def admin_before_request():
    session['actual_role'] = 'employee'
    if not current_user.is_authenticated or current_user.role != "employee":
        return render_template('401.html')


@employee_bp.get('/index')
@login_required
def index():
    return render_template('employee_dashboard.html')


""""""""""""""""""
#   AGGREGATES   #
""""""""""""""""""


@employee_bp.get('/aggregates')
@employee_bp.post('/aggregates')
@login_required
def aggregates():
    form_add = ValueForm()
    form_add.aggregates.choices = [(-1, 'Choisir un aggrégat')] + [(agg.id, agg.label) for agg in
                                                                   Aggregate.query.filter(
                                                                       and_(Aggregate.is_deleted == 0,
                                                                            Aggregate.service_id == current_user.service_id)).all()]
    if form_add.validate_on_submit():
        agg = Value()
        agg.value = float(form_add.value.data)
        agg.aggregate_id = int(form_add.aggregates.data)
        agg.created_by = current_user.id
        database.session.add(agg)
        database.session.commit()
        flash("valeur ajoutée avec succès", "success")
        return redirect(url_for("employee_bp.aggregates"))
    return render_template('values.html', form=form_add)


@employee_bp.get('/aggregates/data')
@login_required
def get_aggregates():
    query = Aggregate.query.filter(and_(Aggregate.is_deleted == 0, Aggregate.service_id == current_user.service_id))
    print(current_user.service_id)
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
