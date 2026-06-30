from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class CategoryEnum(str, enum.Enum):
    ELECTRONICS = 'Electronics'
    FASHION = 'Fashion'
    BOOKS = 'Books'
    FOOD = 'Food'
    SERVICES = 'Services'
    OTHER = 'Other'

class ConditionEnum(str, enum.Enum):
    NEW = 'New'
    USED = 'Used'

class CampusEnum(str, enum.Enum):
    LASU = 'LASU'
    UNILAG = 'UNILAG'
    UI = 'UI'
    OAU = 'OAU'
    OTHER = 'Other'

class MessageTypeEnum(str, enum.Enum):
    TEXT = 'text'
    OFFER = 'offer'
    COUNTER_OFFER = 'counter_offer'
    ACCEPT = 'accept'
    REJECT = 'reject'

class OfferStatusEnum(str, enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    COUNTERED = 'countered'

class NotificationTypeEnum(str, enum.Enum):
    NEW_MESSAGE = 'new_message'
    NEW_OFFER = 'new_offer'
    OFFER_ACCEPTED = 'offer_accepted'
    OFFER_REJECTED = 'offer_rejected'
    COUNTER_OFFER = 'counter_offer'
    NEW_REVIEW = 'new_review'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100))
    department = db.Column(db.String(100))
    level = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    verification_method = db.Column(db.String(20))
    student_id_url = db.Column(db.String(255))
    verified_badge = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    listings = db.relationship('Listing', backref='seller', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewed_user_id', backref='reviewed_user', lazy=True)
    reviews_written = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.Enum(CategoryEnum), nullable=False)
    condition = db.Column(db.Enum(ConditionEnum), nullable=False)
    images = db.Column(db.JSON, default=list)
    campus = db.Column(db.Enum(CampusEnum), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_sold = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedListing(db.Model):
    __tablename__ = 'saved_listings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    user = db.relationship('User', backref='saved')
    listing = db.relationship('Listing', backref='saved_by')

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    listing = db.relationship('Listing', backref='chat_rooms')
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum(MessageTypeEnum), default=MessageTypeEnum.TEXT)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.relationship('ChatRoom', backref='messages')
    sender = db.relationship('User')

class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(OfferStatusEnum), default=OfferStatusEnum.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.relationship('ChatRoom', backref='offers')
    buyer = db.relationship('User')

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reporter = db.relationship('User', backref='reports')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum(NotificationTypeEnum), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
