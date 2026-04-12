import os
import requests
import resend
from flask import Blueprint, request, jsonify, url_for, redirect, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from extensions import db, oauth
from models import User, GuestUsage

auth_bp = Blueprint('auth', __name__)

def is_strong_password(password: str) -> bool:
    """Basic security check for passwords."""
    import re
    if len(password) < 8: return False
    if not re.search(r'[A-Z]', password): return False
    if not re.search(r'[\d\W]', password): return False
    return True

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    captcha_response = data.get('captcha')

    # Verify ReCAPTCHA
    secret = os.environ.get('RECAPTCHA_SECRET_KEY')
    verify_res = requests.post(f"https://www.google.com/recaptcha/api/siteverify?secret={secret}&response={captcha_response}")
    if not verify_res.json().get('success'):
        return jsonify({"error": "CAPTCHA verification failed."}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.is_verified:
        return jsonify({"error": "Account already exists."}), 400
    
    if not existing_user:
        if not is_strong_password(password):
            return jsonify({"error": "Password is too weak. Requirements: 8+ chars, uppercase, digit/special."}), 400
        
        user = User(email=email)
        # Inherit credits from guest usage if applicable
        ip = request.remote_addr
        guest = GuestUsage.query.filter_by(ip_address=ip).first()
        used = guest.used_tries if guest else 0
        user.credits = max(0, 3 - used)
        
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        target_user = user
    else:
        target_user = existing_user

    # Email Verification via Resend
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(email, salt='email-confirm')
    confirm_url = url_for('auth.verify_email', token=token, _external=True)
    
    try:
        resend.Emails.send({
            "from": "EfficientPDF <NoReply@efficientpdf.com>", 
            "to": [email],
            "subject": "Confirm your account",
            "html": f"<p>Please confirm your account by clicking <a href='{confirm_url}'>here</a>.</p>"
        })
    except Exception:
        return jsonify({"error": "Failed to send verification email."}), 500

    return jsonify({"message": "Verification email sent."}), 201

@auth_bp.route('/api/verify/<token>')
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except Exception:
        return "Verification link expired.", 400
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_verified = True
        db.session.commit()
        return redirect('/?alert=verified')
    return "User not found.", 404

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        if not user.is_verified:
            return jsonify({"error": "Email not verified."}), 403
        login_user(user)
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials."}), 401

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

@auth_bp.route('/login/google')
def login_google():
    session['next_url'] = request.referrer
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize/google')
def authorize_google():
    next_url = session.pop('next_url', '/')
    try:
        token = oauth.google.authorize_access_token()
        email = token.get('userinfo', {}).get('email')
        if not email: return redirect(next_url)

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, is_verified=True)
            user.set_password(os.urandom(24).hex())
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(next_url)
    except Exception:
        return redirect(next_url)

@auth_bp.route('/api/user/status', methods=['GET'])
def user_status():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "email": current_user.email, "credits": current_user.credits})
    
    ip = request.remote_addr
    guest = GuestUsage.query.filter_by(ip_address=ip).first()
    return jsonify({"authenticated": False, "guest_used": guest.used_tries if guest else 0, "guest_max": 3})