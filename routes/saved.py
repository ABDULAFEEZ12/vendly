from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, SavedListing, Listing

saved_bp = Blueprint('saved', __name__)

@saved_bp.route('/<int:listing_id>', methods=['POST'])
@jwt_required()
def save_listing(listing_id):
    user_id = int(get_jwt_identity())
    if SavedListing.query.filter_by(user_id=user_id, listing_id=listing_id).first():
        return jsonify({'msg': 'Already saved'}), 409
    saved = SavedListing(user_id=user_id, listing_id=listing_id)
    db.session.add(saved)
    db.session.commit()
    return jsonify({'msg': 'Listing saved'}), 201

@saved_bp.route('/<int:listing_id>', methods=['DELETE'])
@jwt_required()
def unsave_listing(listing_id):
    user_id = int(get_jwt_identity())
    saved = SavedListing.query.filter_by(user_id=user_id, listing_id=listing_id).first()
    if not saved:
        return jsonify({'msg': 'Not found'}), 404
    db.session.delete(saved)
    db.session.commit()
    return jsonify({'msg': 'Unsaved'})

@saved_bp.route('', methods=['GET'])
@jwt_required()
def get_saved():
    user_id = int(get_jwt_identity())
    saved = SavedListing.query.filter_by(user_id=user_id).join(Listing).filter(Listing.is_active==True).all()
    from routes.listings import listing_to_dict
    return jsonify([listing_to_dict(s.listing, include_seller=True) for s in saved])