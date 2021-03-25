import hashlib

from flask import Flask, request, jsonify
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import exc

SALT = 'qwerty'
POSTGRE_DSN = 'postgresql://web_py:12345@127.0.0.1:5432/web_py'


app = Flask(__name__)
app.config.from_mapping(SQLALCHEMY_DATABASE_URI=POSTGRE_DSN)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class BasicException(Exception):
    status_code = 0
    default_message = 'Unknown Error'

    def __init__(self, message: str = None, status_code: int = None):
        super().__init__(message)
        self.message = message
        request.status = self.status_code
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):

        return {
            'message': self.message or self.default_message
        }


class NotFound(BasicException):
    status_code = 404
    default_message = 'Not found'


class AuthError(BasicException):
    status_code = 401
    default_message = 'Auth error'


class BadLuck(BasicException):
    status_code = 400
    default_message = 'Bad luck'


@app.errorhandler(BadLuck)
@app.errorhandler(NotFound)
@app.errorhandler(AuthError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class BaseModelMixin:

    @classmethod
    def by_id(cls, obj_id):
        obj = cls.query.get(obj_id)
        if obj:
            return obj
        else:
            raise NotFound

    def add(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.IntegrityError:
            raise BadLuck


class User(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __str__(self):
        return f'User {self.username}'

    def __repr__(self):
        return str(self)

    def set_password(self, raw_password):
        raw_password = f'{raw_password}{SALT}'
        self.password = hashlib.md5(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        raw_password = f'{raw_password}{SALT}'
        return self.password == hashlib.md5(raw_password.encode()).hexdigest()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            "email": self.email
        }


class UserView(MethodView):

    def get(self, user_id):
        user = User.by_id(user_id)
        return jsonify(user.to_dict())

    def post(self):
        user = User(**request.json)
        user.set_password(request.json['password'])
        user.add()
        return jsonify(user.to_dict())


@app.route('/health/', methods=['GET', ])
def health():
    if request.method == 'GET':
        return jsonify({'status': 'OK'})

    return {'status': 'OK'}


app.add_url_rule('/users/<int:user_id>', view_func=UserView.as_view('users_get'), methods=['GET', ])
app.add_url_rule('/users/', view_func=UserView.as_view('users_create'), methods=['POST', ])

app.run()
