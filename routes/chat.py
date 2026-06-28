from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ChatRoom, Message, Offer, Listing, MessageTypeEnum, OfferStatusEnum
from routes.auth import user_to_dict

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/start', methods=['POST'])
@jwt_required()
def start_chat():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    listing_id = data.get('listing_id')
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'msg': 'Listing not found'}), 404
    room = ChatRoom.query.filter_by(listing_id=listing_id, buyer_id=user_id).first()
    if room:
        return jsonify({'room_id': room.id})
    room = ChatRoom(listing_id=listing_id, buyer_id=user_id, seller_id=listing.seller_id)
    db.session.add(room)
    db.session.commit()
    return jsonify({'room_id': room.id}), 201

@chat_bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_rooms():
    user_id = int(get_jwt_identity())
    rooms = ChatRoom.query.filter(
        (ChatRoom.buyer_id == user_id) | (ChatRoom.seller_id == user_id)
    ).order_by(ChatRoom.created_at.desc()).all()
    result = []
    for room in rooms:
        other_user = room.seller if room.buyer_id == user_id else room.buyer
        last_msg = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.desc()).first()
        result.append({
            'room_id': room.id,
            'listing': {
                'id': room.listing.id,
                'title': room.listing.title,
                'price': room.listing.price,
                'image': room.listing.images[0] if room.listing.images else None
            },
            'other_user': user_to_dict(other_user),
            'last_message': {
                'content': last_msg.content,
                'type': last_msg.type.value,
                'created_at': last_msg.created_at.isoformat()
            } if last_msg else None
        })
    return jsonify(result)

@chat_bp.route('/rooms/<int:room_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(room_id):
    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({'msg': 'Room not found'}), 404
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.created_at.asc()).all()
    
    result = []
    for m in messages:
        msg_dict = {
            'id': m.id,
            'sender_id': m.sender_id,
            'type': m.type.value,
            'content': m.content,
            'created_at': m.created_at.isoformat()
        }
        # If this message is offer-related, attach the latest matching offer
        if m.type in [MessageTypeEnum.OFFER, MessageTypeEnum.COUNTER_OFFER]:
            offer = Offer.query.filter_by(room_id=room_id).order_by(Offer.created_at.desc()).first()
            if offer:
                msg_dict['offer'] = offer_to_dict(offer)
        result.append(msg_dict)
    
    return jsonify(result)

@chat_bp.route('/rooms/<int:room_id>/send', methods=['POST'])
@jwt_required()
def send_message(room_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'msg': 'Message cannot be empty'}), 400
    
    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({'msg': 'Room not found'}), 404
    
    if user_id not in [room.buyer_id, room.seller_id]:
        return jsonify({'msg': 'Unauthorized'}), 403
    
    msg = Message(
        room_id=room_id,
        sender_id=user_id,
        type=MessageTypeEnum.TEXT,
        content=content
    )
    db.session.add(msg)
    db.session.commit()
    
    return jsonify(message_to_dict(msg)), 201

@chat_bp.route('/rooms/<int:room_id>/offer', methods=['POST'])
@jwt_required()
def make_offer(room_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    amount = data.get('amount')
    if not amount:
        return jsonify({'msg': 'Amount required'}), 400
    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({'msg': 'Room not found'}), 404
    if user_id not in [room.buyer_id, room.seller_id]:
        return jsonify({'msg': 'Unauthorized'}), 403
    
    offer = Offer(
        room_id=room_id,
        listing_id=room.listing_id,
        buyer_id=user_id,
        amount=float(amount)
    )
    db.session.add(offer)
    db.session.flush()  # Get the offer ID before creating message
    
    msg = Message(
        room_id=room_id,
        sender_id=user_id,
        type=MessageTypeEnum.OFFER,
        content=f"💰 Offer: ₦{float(amount):,.2f}"
    )
    db.session.add(msg)
    db.session.commit()
    
    return jsonify({'offer': offer_to_dict(offer), 'message': message_to_dict(msg)}), 201

@chat_bp.route('/rooms/<int:room_id>/offer/<int:offer_id>', methods=['PUT'])
@jwt_required()
def respond_offer(room_id, offer_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    action = data.get('action')
    
    print(f"DEBUG respond_offer: room={room_id}, offer={offer_id}, user={user_id}, action={action}")
    
    offer = Offer.query.get(offer_id)
    if not offer:
        print(f"DEBUG: Offer {offer_id} not found in DB")
        return jsonify({'msg': 'Offer not found'}), 404
    
    if offer.room_id != room_id:
        print(f"DEBUG: Room mismatch - offer.room={offer.room_id}, requested={room_id}")
        return jsonify({'msg': 'Offer does not belong to this room'}), 404
    
    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({'msg': 'Room not found'}), 404
    
    if user_id not in [room.buyer_id, room.seller_id]:
        print(f"DEBUG: Auth fail - user={user_id}, buyer={room.buyer_id}, seller={room.seller_id}")
        return jsonify({'msg': 'Unauthorized'}), 403

    if action == 'accept':
        offer.status = OfferStatusEnum.ACCEPTED
        msg_type = MessageTypeEnum.ACCEPT
        content = f"✅ Offer accepted at ₦{offer.amount:,.2f}"
    elif action == 'reject':
        offer.status = OfferStatusEnum.REJECTED
        msg_type = MessageTypeEnum.REJECT
        content = "❌ Offer rejected"
    elif action == 'counter':
        new_amount = data.get('amount')
        if not new_amount:
            return jsonify({'msg': 'Counter amount required'}), 400
        offer.status = OfferStatusEnum.COUNTERED
        new_offer = Offer(
            room_id=room_id,
            listing_id=room.listing_id,
            buyer_id=user_id,
            amount=float(new_amount)
        )
        db.session.add(new_offer)
        db.session.flush()
        msg = Message(
            room_id=room_id,
            sender_id=user_id,
            type=MessageTypeEnum.COUNTER_OFFER,
            content=f"🔄 Counter offer: ₦{float(new_amount):,.2f}"
        )
        db.session.add(msg)
        db.session.commit()
        print(f"DEBUG: Counter offer {new_offer.id} created")
        return jsonify({'offer': offer_to_dict(new_offer), 'message': message_to_dict(msg)}), 200
    else:
        return jsonify({'msg': 'Invalid action. Use: accept, reject, or counter'}), 400

    msg = Message(
        room_id=room_id,
        sender_id=user_id,
        type=msg_type,
        content=content
    )
    db.session.add(msg)
    db.session.commit()
    
    print(f"DEBUG: Offer {offer.id} now {offer.status.value}")
    return jsonify({'offer': offer_to_dict(offer), 'message': message_to_dict(msg)}), 200

def offer_to_dict(o):
    return {
        'id': o.id,
        'room_id': o.room_id,
        'amount': o.amount,
        'status': o.status.value,
        'buyer_id': o.buyer_id,
        'created_at': o.created_at.isoformat()
    }

def message_to_dict(m):
    return {
        'id': m.id,
        'sender_id': m.sender_id,
        'type': m.type.value,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    }
