from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Listing, User, CategoryEnum, ConditionEnum, CampusEnum
from sqlalchemy import or_
import cloudinary.uploader
from flask import current_app
import json

listings_bp = Blueprint('listings', __name__)

@listings_bp.route('', methods=['POST'])
@jwt_required()
def create_listing():
    user_id = get_jwt_identity()
    data = request.form
    files = request.files.getlist('images')

    # Validate required fields
    required = ['title', 'price', 'category', 'condition', 'campus']
    if not all(k in data for k in required):
        return jsonify({'msg': 'Missing fields'}), 400

    # Validate enums
    try:
        category = CategoryEnum(data['category'])
        condition = ConditionEnum(data['condition'])
        campus = CampusEnum(data['campus'])
    except ValueError:
        return jsonify({'msg': 'Invalid enum value'}), 400

    # Upload images
    image_urls = []
    if files:
        for file in files[:5]:
            try:
                result = cloudinary.uploader.upload(
                    file,
                    folder='vendly/listings',
                    resource_type='image',
                    upload_preset=current_app.config['CLOUDINARY_UPLOAD_PRESET']
                )
                image_urls.append(result['secure_url'])
            except Exception as e:
                return jsonify({'msg': 'Image upload failed', 'error': str(e)}), 500
    elif 'image_urls' in data:
        try:
            image_urls = json.loads(data['image_urls'])
        except:
            pass

    listing = Listing(
        seller_id=int(user_id),
        title=data['title'],
        description=data.get('description', ''),
        price=float(data['price']),
        category=category,
        condition=condition,
        images=image_urls,
        campus=campus
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({'msg': 'Listing created', 'listing': listing_to_dict(listing)}), 201

@listings_bp.route('', methods=['GET'])
def get_listings():
    # Query params: search, category, campus, condition, sort, min_price, max_price
    query = Listing.query.filter(Listing.is_active == True, Listing.is_sold == False)

    search = request.args.get('search')
    if search:
        query = query.filter(or_(
            Listing.title.ilike(f'%{search}%'),
            Listing.description.ilike(f'%{search}%')
        ))

    category = request.args.get('category')
    if category:
        try:
            cat_enum = CategoryEnum(category)
            query = query.filter(Listing.category == cat_enum)
        except: pass

    campus = request.args.get('campus')
    if campus:
        try:
            camp_enum = CampusEnum(campus)
            query = query.filter(Listing.campus == camp_enum)
        except: pass

    condition = request.args.get('condition')
    if condition:
        try:
            cond_enum = ConditionEnum(condition)
            query = query.filter(Listing.condition == cond_enum)
        except: pass

    min_price = request.args.get('min_price')
    if min_price:
        try: query = query.filter(Listing.price >= float(min_price))
        except: pass

    max_price = request.args.get('max_price')
    if max_price:
        try: query = query.filter(Listing.price <= float(max_price))
        except: pass

    sort = request.args.get('sort', 'newest')
    if sort == 'price_low':
        query = query.order_by(Listing.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Listing.price.desc())
    else: # newest
        query = query.order_by(Listing.created_at.desc())

    listings = query.limit(100).all()
    return jsonify([listing_to_dict(l) for l in listings])

@listings_bp.route('/<int:id>', methods=['GET'])
def get_listing(id):
    listing = Listing.query.get(id)
    if not listing:
        return jsonify({'msg': 'Listing not found'}), 404
    return jsonify(listing_to_dict(listing, include_seller=True))

@listings_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_listing(id):
    user_id = int(get_jwt_identity())
    listing = Listing.query.get(id)
    if not listing or listing.seller_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403

    data = request.form
    if 'title' in data: listing.title = data['title']
    if 'description' in data: listing.description = data['description']
    if 'price' in data: listing.price = float(data['price'])
    if 'category' in data:
        try: listing.category = CategoryEnum(data['category'])
        except: pass
    if 'condition' in data:
        try: listing.condition = ConditionEnum(data['condition'])
        except: pass
    if 'campus' in data:
        try: listing.campus = CampusEnum(data['campus'])
        except: pass

    files = request.files.getlist('images')
    if files:
        image_urls = []
        for file in files[:5]:
            try:
                result = cloudinary.uploader.upload(
                    file,
                    folder='vendly/listings',
                    resource_type='image',
                    upload_preset=current_app.config['CLOUDINARY_UPLOAD_PRESET']
                )
                image_urls.append(result['secure_url'])
            except: pass
        if image_urls:
            listing.images = image_urls
    elif 'image_urls' in data:
        try:
            listing.images = json.loads(data['image_urls'])
        except:
            pass

    db.session.commit()
    return jsonify(listing_to_dict(listing))

@listings_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_listing(id):
    user_id = int(get_jwt_identity())
    listing = Listing.query.get(id)
    if not listing or listing.seller_id != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    listing.is_active = False
    db.session.commit()
    return jsonify({'msg': 'Listing deactivated'})

@listings_bp.route('/user/<int:user_id>', methods=['GET'])
def user_listings(user_id):
    listings = Listing.query.filter_by(seller_id=user_id, is_active=True).order_by(Listing.created_at.desc()).all()
    return jsonify([listing_to_dict(l) for l in listings])

def listing_to_dict(listing, include_seller=False):
    data = {
        'id': listing.id,
        'title': listing.title,
        'description': listing.description,
        'price': listing.price,
        'category': listing.category.value,
        'condition': listing.condition.value,
        'images': listing.images,
        'campus': listing.campus.value,
        'is_active': listing.is_active,
        'is_sold': listing.is_sold,
        'created_at': listing.created_at.isoformat()
    }
    if include_seller:
        from routes.auth import user_to_dict
        data['seller'] = user_to_dict(listing.seller)
    return data