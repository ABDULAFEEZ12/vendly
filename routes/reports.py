from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Report

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['POST'])
@jwt_required()
def report_listing():
    reporter_id = int(get_jwt_identity())
    data = request.get_json()
    if not all(k in data for k in ['listing_id', 'reason']):
        return jsonify({'msg': 'Missing fields'}), 400
    report = Report(
        reporter_id=reporter_id,
        listing_id=data['listing_id'],
        reason=data['reason']
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'msg': 'Report submitted'}), 201