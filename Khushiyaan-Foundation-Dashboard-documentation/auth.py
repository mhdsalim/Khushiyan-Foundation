from flask_login import UserMixin, LoginManager

# Flask-Login setup
login_manager = LoginManager()

# User class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Required for Flask-Login - this decorator registers the function
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

