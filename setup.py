from main_app import database
from main_app.models import User
from werkzeug.security import generate_password_hash
user = User()
user.username="admin"
user.role = "Master"
user.password_hash = generate_password_hash('123456789','sha256')
user.service_id = None
database.session.add(user)
database.session.commit()

print(f'user_id  = {user.id} created!')