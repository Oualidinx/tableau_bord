from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError
from wtforms import SubmitField, StringField, PasswordField, SelectField
from main_app.models import User, Service, Aggregate


class LoginForm(FlaskForm):
    username = StringField('Pseudonyme: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

    def validate_email(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('Veuillez vérifier les informations fournits')


class RegisterForm(FlaskForm):
    # user_id = StringField('ID :')
    username = StringField('Pseudonyme: ', validators=[DataRequired()])
    password = PasswordField('Mot de passe:', validators=[DataRequired()])
    service = SelectField('Service: ', validate_choice=False)
    role = SelectField('Rôle: ', choices=[(-1, "Veuillez choisir le role"), (1, 'employee'), (2, 'Master')])
    submit = SubmitField('Ajouter')

    def validate_role(self, role):
        if int(role.data) == -1:
            raise ValidationError('Choix érroné, veuillez selectionner le bon choix ("employee" ou "master")')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).filter_by(is_deleted=0).first()
        if user:
            raise ValidationError('Ce pseudonyme est déjà utilisé')

    # def validate_user_id(self, user_id):
    #     if user_id:
    #         user = User.query.get(int(user_id))
    #         if not user:
    #             raise ValidationError('Utilisateur introuvable')

    def validate_service(self, service):
        if self.role.data == 1 and int(service.data) not in [srv.id for srv in
                                                             Service.query.filter_by(is_deleted=0).all()]:
            raise ValidationError('Veuillez choisir un service')


class EditEmpForm(RegisterForm):
    submit = SubmitField('Modifier')


class ServiceForm(FlaskForm):
    # srv_id = StringField('ID: ')
    label = StringField('Libellé service: ', validators=[DataRequired()])
    submit = SubmitField('Ajouter')

    def validate_label(self, label):
        user = Service.query.filter_by(label=label.data).filter_by(is_deleted=0).first()
        if user:
            raise ValidationError('Ce Service est déjà utilisé')

    # def validate_srv_id(self, srv_id):
    #     if srv_id:
    #         srv = Service.query.get(int(srv_id.data))
    #         if not srv:
    #             raise ValidationError('Service introuvable')


class AggregateForm(FlaskForm):
    label = StringField('Libellé aggregat: ', validators=[DataRequired()])
    code = StringField('Code aggregat: ', validators=[DataRequired()])
    service = SelectField('Service: ', validate_choice=False)
    submit = SubmitField('Ajouter')

    def validate_label(self, label):
        user = Aggregate.query.filter_by(label=label.data).filter_by(is_deleted=0).first()
        if user:
            raise ValidationError('libellé déjà utilisé')

    def validate_service(self, service):
        if int(service.data) not in [srv.id for srv in Service.query.filter_by(is_deleted=0).all()]:
            raise ValidationError('Veuillez choisir un service')
    # def validate_code(self, code):
    #     user = Aggregate.query.filter_by(code=code.data).first()
    #     if user:
    #         raise ValidationError('Ce code d\'aggregat est déjà utilisé')


class ValueForm(FlaskForm):
    aggregates = SelectField('Aggrégat: ')
    value = StringField('Valeur', validators=[DataRequired()])
    submit = SubmitField('Ajouter')

    def validate_value(self, value):
        if float(value.data) <= 0:
            raise ValidationError('Impossible de passé des valeurs inférieur à 0')

    def validate_aggregates(self, aggregates ):
        if int(aggregates.data) not in [agg.id for agg in Aggregate.query.filter(and_(Aggregate.is_deleted == 0, Aggregate.service_id == current_user.service_id)).all()]:
            raise ValidationError("Choix de l'aggregate n'est pas valide")
