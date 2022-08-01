import datetime

from main_app import database as db
from flask_login import UserMixin
from main_app import login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True)
    role = db.Column(db.String(20))
    is_deleted = db.Column(db.SmallInteger, default=0)
    password_hash = db.Column(db.String(256), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    values = db.relationship('Value', backref="value_user", lazy="subquery")

    def to_dict(self):
        return dict(
            id=self.id,
            username=self.username,
            role=self.role,
            service=Service.query.get(self.service_id).label if self.service_id else None
        )


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(10))
    is_deleted = db.Column(db.SmallInteger, default=0)
    users = db.relationship('User', backref="user_services", lazy="subquery")
    aggregates = db.relationship('Aggregate', backref="aggregate_service", lazy="subquery")

    def to_dict(self):
        return dict(
            id=self.id,
            label=self.label
        )


class Aggregate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=True)
    label = db.Column(db.String(200))
    is_deleted = db.Column(db.SmallInteger, default=0)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

    def __repr__(self):
        return f'Aggregat: id={self.id}, code = {self.code}, label={self.label}, is_deleted = {self.is_deleted}, ' \
               f'service = {Service.query.get(self.service_id).label}'

    def to_dict(self):
        return dict(
            id=self.id,
            label=self.label,
            code=self.code,
            service=Service.query.get(self.service_id).label
        )


class Value(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    created_at = db.Column(db.DATETIME, default=datetime.datetime.utcnow())
    aggregate_id = db.Column(db.Integer, db.ForeignKey('aggregate.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return dict(
            id=self.id,
            create_at=self.created_at,
            aggregate=f"{Aggregate.query.get(self.aggregate_id).code}, {Aggregate.query.get(self.aggregate_id).code}"
        )


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)
