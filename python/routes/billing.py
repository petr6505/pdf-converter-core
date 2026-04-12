import os
import stripe
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import User

billing_bp = Blueprint('billing', __name__)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@billing_bp.route('/api/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    data = request.get_json() or {}
    package_type = data.get('package', 'medium')
    
    packages = {
        'small': {'name': 'Starter', 'price': 5000, 'credits': 15},
        'medium': {'name': 'Standard', 'price': 10000, 'credits': 40},
        'large': {'name': 'Pro', 'price': 25000, 'credits': 150}
    }
    
    pkg = packages.get(package_type, packages['medium'])
    return_url = request.headers.get("Referer", request.host_url)
    sep = "&" if "?" in return_url else "?"
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'czk',
                    'product_data': {'name': f"EfficientPDF - {pkg['name']}"},
                    'unit_amount': pkg['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=return_url + sep + 'payment=success',
            cancel_url=return_url + sep + 'payment=cancelled',
            metadata={'credits_to_add': pkg['credits']},
            client_reference_id=str(current_user.id)
        )
        return jsonify({'checkout_url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@billing_bp.route('/api/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return 'Invalid payload', 400

    if event.type == 'checkout.session.completed':
        session = event.data.object
        user_id = session.get('client_reference_id')
        credits = int(session.get('metadata', {}).get('credits_to_add', 0))
        
        if user_id and credits:
            user = db.session.get(User, int(user_id))
            if user:
                user.credits += credits
                db.session.commit()
                
    return 'OK', 200