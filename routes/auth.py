from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
import cloudinary.uploader

auth_bp = Blueprint('auth', __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def user_to_dict(user):
    return {
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'school': user.school,
        'department': user.department,
        'level': user.level,
        'profile_picture': user.profile_picture,
        'is_verified': user.is_verified,
        'verified_badge': user.verified_badge,
        'verification_method': user.verification_method,
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['email', 'password', 'full_name']
    if not all(k in data for k in required):
        return jsonify({'msg': 'Missing fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg': 'Email already registered'}), 409

    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        full_name=data['full_name'],
        school=data.get('school'),
        department=data.get('department'),
        level=data.get('level')
    )
    # Determine verification method
    if data['email'].endswith('.edu.ng') or data.get('school'):
        user.verification_method = 'email'
    else:
        user.verification_method = 'student_id'

    db.session.add(user)
    db.session.commit()

    # Send verification email if method is email (only if mail is configured)
    if user.verification_method == 'email':
        try:
            serializer = get_serializer()
            token = serializer.dumps(user.email, salt='email-verify')
            verify_url = url_for('auth.verify_email', token=token, _external=True)
            msg = Message('Vendly - Verify your email',
                          recipients=[user.email])
            msg.body = f'Please click this link to verify your email: {verify_url}'
            mail = current_app.extensions.get('mail')
            if mail:
                mail.send(msg)
        except Exception as e:
            print(f"Mail error (non-fatal): {e}")

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'msg': 'Registration successful',
        'access_token': access_token,
        'user': user_to_dict(user)
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'msg': 'Invalid email or password'}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': user_to_dict(user)
    })

@auth_bp.route('/verify-email')
def verify_email():
    token = request.args.get('token')
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)
    except:
        return jsonify({'msg': 'Invalid or expired token'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    user.is_verified = True
    user.verified_badge = True
    db.session.commit()
    return jsonify({'msg': 'Email verified successfully'})

@auth_bp.route('/upload-student-id', methods=['POST'])
@jwt_required()
def upload_student_id():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if 'image' not in request.files:
        return jsonify({'msg': 'No image file'}), 400
    file = request.files['image']
    try:
        result = cloudinary.uploader.upload(
            file,
            folder='vendly/student_ids',
            resource_type='image',
            upload_preset=current_app.config.get('CLOUDINARY_UPLOAD_PRESET', 'vendly-unsigned')
        )
        user.student_id_url = result['secure_url']
        user.verification_method = 'student_id'
        db.session.commit()
        return jsonify({'msg': 'Student ID uploaded, pending admin approval'})
    except Exception as e:
        return jsonify({'msg': 'Upload failed', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify({'user': user_to_dict(user)})

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json()
    if 'full_name' in data: user.full_name = data['full_name']
    if 'school' in data: user.school = data['school']
    if 'department' in data: user.department = data['department']
    if 'level' in data: user.level = data['level']
    if 'profile_picture' in data: user.profile_picture = data['profile_picture']
    db.session.commit()
    return jsonify({'user': user_to_dict(user)})

@auth_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify(user_to_dict(user))