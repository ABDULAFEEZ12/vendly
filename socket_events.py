from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token
from models import db, Message, ChatRoom, Offer, MessageTypeEnum, OfferStatusEnum

def register_socket_events(socketio):
    @socketio.on('join')
    def handle_join(data):
        token = data.get('token')
        room_id = data.get('room_id')
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
        except:
            return False
        join_room(str(room_id))
        emit('status', {'msg': f'User {user_id} joined room {room_id}'}, room=str(room_id))

    @socketio.on('send_message')
    def handle_message(data):
        token = data.get('token')
        room_id = data.get('room_id')
        content = data.get('content')
        try:
            decoded = decode_token(token)
            user_id = int(decoded['sub'])
        except:
            return
        msg = Message(room_id=room_id, sender_id=user_id, type=MessageTypeEnum.TEXT, content=content)
        db.session.add(msg)
        db.session.commit()
        emit('new_message', {
            'id': msg.id,
            'sender_id': user_id,
            'type': 'text',
            'content': content,
            'created_at': msg.created_at.isoformat()
        }, room=str(room_id))

    @socketio.on('make_offer')
    def handle_make_offer(data):
        token = data.get('token')
        room_id = data.get('room_id')
        amount = data.get('amount')
        try:
            decoded = decode_token(token)
            user_id = int(decoded['sub'])
        except:
            return
        offer = Offer(room_id=room_id, listing_id=data.get('listing_id'), buyer_id=user_id, amount=float(amount))
        db.session.add(offer)
        msg = Message(room_id=room_id, sender_id=user_id, type=MessageTypeEnum.OFFER, content=f"Offer: ₦{amount:,.2f}")
        db.session.add(msg)
        db.session.commit()
        emit('new_message', {
            'id': msg.id,
            'sender_id': user_id,
            'type': 'offer',
            'content': msg.content,
            'offer': {'id': offer.id, 'amount': amount, 'status': 'pending'},
            'created_at': msg.created_at.isoformat()
        }, room=str(room_id))

    @socketio.on('offer_response')
    def handle_offer_response(data):
        token = data.get('token')
        room_id = data.get('room_id')
        offer_id = data.get('offer_id')
        action = data.get('action')  # accept, reject, counter
        try:
            decoded = decode_token(token)
            user_id = int(decoded['sub'])
        except:
            return
        offer = Offer.query.get(offer_id)
        if not offer:
            return
        if action == 'accept':
            offer.status = OfferStatusEnum.ACCEPTED
            msg_content = f"Offer accepted at ₦{offer.amount:,.2f}"
            msg_type = MessageTypeEnum.ACCEPT
        elif action == 'reject':
            offer.status = OfferStatusEnum.REJECTED
            msg_content = "Offer rejected"
            msg_type = MessageTypeEnum.REJECT
        elif action == 'counter':
            new_amount = data.get('amount')
            offer.status = OfferStatusEnum.COUNTERED
            new_offer = Offer(room_id=room_id, listing_id=offer.listing_id, buyer_id=user_id, amount=float(new_amount))
            db.session.add(new_offer)
            msg = Message(room_id=room_id, sender_id=user_id, type=MessageTypeEnum.COUNTER_OFFER, content=f"Counter offer: ₦{new_amount:,.2f}")
            db.session.add(msg)
            db.session.commit()
            emit('new_message', {
                'id': msg.id,
                'sender_id': user_id,
                'type': 'counter_offer',
                'content': msg.content,
                'offer': {'id': new_offer.id, 'amount': new_amount, 'status': 'pending'},
                'created_at': msg.created_at.isoformat()
            }, room=str(room_id))
            return
        else:
            return

        msg = Message(room_id=room_id, sender_id=user_id, type=msg_type, content=msg_content)
        db.session.add(msg)
        db.session.commit()
        emit('new_message', {
            'id': msg.id,
            'sender_id': user_id,
            'type': msg_type.value,
            'content': msg_content,
            'offer': {'id': offer.id, 'amount': offer.amount, 'status': offer.status.value},
            'created_at': msg.created_at.isoformat()
        }, room=str(room_id))