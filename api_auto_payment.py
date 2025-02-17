from functools import wraps
from flask_jwt_extended import get_jwt_identity 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Configure database and JWT secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


def is_user_logged_in(f):
    @wraps(f)
    def decorated_functions(*args, **kwargs):
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized access"}), 401
        return f(*args, **kwargs)
    return decorated_functions

def check_params(*expected_params):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.json
            missing_params = [param for param in expected_params if param not in data]
            if missing_params:
                return jsonify({"error": f"Missing parameters: {', '.join(missing_params)}"}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator


def check_method(expected_method):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.method != expected_method:
                return jsonify({"error": f"Method not allowed, expected {expected_method}"}), 405
            return f(*args, **kwargs)
        return wrapper
    return decorator



# Routes for user authentication
@app.route('/register', methods=['POST'])
@check_method('POST')
@check_params('username', 'password')
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
@check_method('POST')
@check_params('username', 'password')
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200





@app.route('/logout', methods=['POST'])
@jwt_required()
@check_method('POST')
def logout():
    # For JWTs, logout can be handled by token blacklisting 
    return jsonify({"message": "Successfully logged out"}), 200

# Payment route (unchanged)
@app.route('/payment', methods=['POST'])
@jwt_required()
@is_user_logged_in
@check_method('POST')
@check_params('pay_amount')
def handle_payment():
    data = request.json
    pay_amount = data.get('pay_amount')

    if not pay_amount:
        return jsonify({"error": "Missing 'pay_amount' field in request body"}), 400

    print(f"Received payment amount: {pay_amount}")
    return jsonify({"message": f"Payment amount received: {pay_amount}"}), 200

if __name__ == "__main__":
   # db.create_all()  # Creates tables if they don't exist
    app.run(host='0.0.0.0', port=5000)