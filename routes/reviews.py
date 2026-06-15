from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Review

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    reviewer_id = int(get_jwt_identity())
    data = request.get_json()
    if not all(k in data for k in ['reviewed_user_id', 'listing_id', 'rating']):
        return jsonify({'msg': 'Missing fields'}), 400
    review = Review(
        reviewer_id=reviewer_id,
        reviewed_user_id=data['reviewed_user_id'],
        listing_id=data['listing_id'],
        rating=int(data['rating']),
        comment=data.get('comment', '')
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'msg': 'Review submitted'}), 201

@reviews_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    reviews = Review.query.filter_by(reviewed_user_id=user_id).all()
    return jsonify([{
        'id': r.id,
        'reviewer_name': r.reviewer.full_name,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.isoformat()
    } for r in reviews])