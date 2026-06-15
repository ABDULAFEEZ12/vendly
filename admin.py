from flask import Blueprint, request, jsonify
from models import db, User

admin_bp = Blueprint('admin', __name__)

# Very basic admin – in production, protect with admin role
ADMIN_EMAILS = ['admin@vendly.com']  # set via env or config

@admin_bp.route('/approve-student/<int:user_id>', methods=['POST'])
def approve_student(user_id):
    # In real app, check admin JWT
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    user.verified_badge = True
    user.is_verified = True
    db.session.commit()
    return jsonify({'msg': 'User verified and badge granted'})

@admin_bp.route('/pending-verifications', methods=['GET'])
def pending_verifications():
    users = User.query.filter_by(verification_method='student_id', verified_badge=False).all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'full_name': u.full_name,
        'student_id_url': u.student_id_url
    } for u in users])