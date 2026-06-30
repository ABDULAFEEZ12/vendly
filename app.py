import warnings
warnings.filterwarnings('ignore')

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail, Message
from config import Config
from models import db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    with app.app_context():
        import models
        db.create_all()

    @app.context_processor
    def inject_config():
        return {
            'cloud_name': app.config.get('CLOUDINARY_CLOUD_NAME', ''),
            'upload_preset': app.config.get('CLOUDINARY_UPLOAD_PRESET', 'vendly-unsigned')
        }

    # Register API blueprints
    from routes.auth import auth_bp
    from routes.listings import listings_bp
    from routes.saved import saved_bp
    from routes.chat import chat_bp
    from routes.reviews import reviews_bp
    from routes.reports import reports_bp
    from routes.admin import admin_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(listings_bp, url_prefix='/api/listings')
    app.register_blueprint(saved_bp, url_prefix='/api/saved')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    from socket_events import register_socket_events
    register_socket_events(socketio)

    # ---------- FRONTEND PAGE ROUTES ----------
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/forgot-password')
    def forgot_password_page():
        return render_template('forgot_password.html')

    @app.route('/reset-password')
    def reset_password_page():
        token = request.args.get('token', '')
        return render_template('reset_password.html', token=token)

    @app.route('/test-email')
    def test_email():
        try:
            mail = Mail(app)
            msg = Message('Test from Vendly', recipients=['tellaafeezadewale@gmail.com'])
            msg.body = 'This is a test email from Vendly!'
            mail.send(msg)
            return '✅ Email sent! Check your inbox.'
        except Exception as e:
            return f'❌ Email failed: {str(e)}'

    @app.route('/marketplace')
    def marketplace_page():
        return render_template('marketplace.html')

    @app.route('/listing/<int:id>')
    def listing_detail_page(id):
        return render_template('listing_detail.html')

    @app.route('/listings/new')
    def new_listing_page():
        return render_template('create_listing.html')

    @app.route('/listings/<int:id>/edit')
    def edit_listing_page(id):
        return render_template('edit_listing.html')

    @app.route('/chat')
    def chat_list_page():
        return render_template('chat_list.html')

    @app.route('/chat/<int:room_id>')
    def chat_room_page(room_id):
        return render_template('chat_room.html')

    @app.route('/profile/<int:user_id>')
    def profile_page(user_id):
        return render_template('profile.html')

    @app.route('/saved')
    def saved_page():
        return render_template('saved.html')

    @app.route('/notifications')
    def notifications_page():
        return render_template('notifications.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    return app, socketio

app, socketio = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 55)
    print("  🚀  VENDLY - Student Marketplace")
    print(f"  🌐  http://0.0.0.0:{port}")
    print("  📍  Press Ctrl+C to stop")
    print("=" * 55)
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
