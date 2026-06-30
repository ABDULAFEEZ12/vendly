from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, decode_token
from models import db, User, Listing, Report, Admin
from werkzeug.security import check_password_hash

admin_bp = Blueprint('admin', __name__)

def get_admin_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return token

def verify_admin():
    token = get_admin_token()
    if not token:
        return None
    try:
        decoded = decode_token(token)
        admin = Admin.query.get(int(decoded['sub']))
        return admin
    except:
        return None

def admin_required():
    return verify_admin() is not None

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    admin = Admin.query.filter_by(email=email).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'msg': 'Invalid admin credentials'}), 401

    token = create_access_token(identity=str(admin.id))
    return jsonify({
        'token': token,
        'admin': {'id': admin.id, 'email': admin.email, 'full_name': admin.full_name}
    })

@admin_bp.route('/check', methods=['GET'])
def admin_check():
    admin = verify_admin()
    if admin:
        return jsonify({'valid': True, 'admin': {'id': admin.id, 'email': admin.email, 'full_name': admin.full_name}})
    return jsonify({'valid': False}), 401

@admin_bp.route('/approve-student/<int:user_id>', methods=['POST'])
def approve_student(user_id):
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    user.verified_badge = True
    user.is_verified = True
    db.session.commit()
    return jsonify({'msg': 'User verified and badge granted'})

@admin_bp.route('/pending-verifications', methods=['GET'])
def pending_verifications():
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    users = User.query.filter_by(verification_method='student_id', verified_badge=False).all()
    return jsonify([{
        'id': u.id, 'email': u.email, 'full_name': u.full_name,
        'school': u.school, 'student_id_url': u.student_id_url
    } for u in users])

@admin_bp.route('/stats', methods=['GET'])
def admin_stats():
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    return jsonify({
        'total_users': User.query.count(),
        'total_listings': Listing.query.count(),
        'active_listings': Listing.query.filter_by(is_active=True, is_sold=False).count(),
        'pending_verifications': User.query.filter_by(verification_method='student_id', verified_badge=False).count(),
        'total_reports': Report.query.count(),
    })

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    users = User.query.order_by(User.created_at.desc()).limit(100).all()
    return jsonify([{
        'id': u.id, 'email': u.email, 'full_name': u.full_name,
        'school': u.school, 'verified_badge': u.verified_badge,
        'created_at': u.created_at.isoformat()
    } for u in users])

@admin_bp.route('/reports', methods=['GET'])
def get_reports():
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    reports = Report.query.order_by(Report.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': r.id,
        'reporter_email': r.reporter.email if r.reporter else 'Unknown',
        'listing_title': Listing.query.get(r.listing_id).title if Listing.query.get(r.listing_id) else 'Deleted',
        'listing_id': r.listing_id,
        'reason': r.reason,
        'created_at': r.created_at.isoformat()
    } for r in reports])

@admin_bp.route('/reports/<int:report_id>/dismiss', methods=['POST'])
def dismiss_report(report_id):
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    report = Report.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
    return jsonify({'msg': 'Report dismissed'})

@admin_bp.route('/listings/<int:listing_id>/remove', methods=['POST'])
def admin_remove_listing(listing_id):
    if not admin_required():
        return jsonify({'msg': 'Admin login required'}), 401
    listing = Listing.query.get(listing_id)
    if listing:
        listing.is_active = False
        db.session.commit()
    return jsonify({'msg': 'Listing removed'})
