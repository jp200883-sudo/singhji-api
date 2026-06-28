from flask import Flask, request, jsonify
import razorpay
import stripe
import requests
import os

app = Flask(__name__)

# Config
RAZORPAY_KEY = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
STRIPE_KEY = os.getenv('STRIPE_SECRET_KEY')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))

class SinghJiGateway:
    """World Wide Payment Gateway"""
    
    def __init__(self):
        self.commission_rate = 0.02  # 2%
        self.merchants = {}
    
    def process_payment(self, data):
        """Route payment to correct gateway"""
        country = data.get('country', 'IN')
        method = data.get('method', 'upi')
        
        if country == 'IN':
            return self._process_india(data)
        else:
            return self._process_international(data)
    
    def _process_india(self, data):
        """UPI, Cards, Wallets via Razorpay"""
        try:
            order = razorpay_client.order.create({
                'amount': int(data['amount'] * 100),  # paise
                'currency': 'INR',
                'payment_capture': 1
            })
            
            # Calculate commission
            commission = data['amount'] * self.commission_rate
            
            return {
                'success': True,
                'order_id': order['id'],
                'commission': commission,
                'gateway': 'razorpay',
                'qr_url': f"https://singhji.ai/qr/{order['id']}"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _process_international(self, data):
        """Stripe/PayPal for global"""
        # Stripe integration
        pass
    
    def generate_merchant_qr(self, merchant_id, amount=None):
        """Generate branded QR for merchant"""
        upi_id = f"singhji.{merchant_id}@sbi"
        
        qr_data = {
            'pa': upi_id,
            'pn': 'Singh Ji Gateway',
            'cu': 'INR'
        }
        if amount:
            qr_data['am'] = amount
        
        # Generate QR code
        import qrcode
        qr = qrcode.make(str(qr_data))
        
        return {
            'qr_code': qr,
            'upi_url': f"upi://pay?{ '&'.join([f'{k}={v}' for k,v in qr_data.items()]) }",
            'merchant_id': merchant_id
        }

gateway = SinghJiGateway()

@app.route('/api/gateway/pay', methods=['POST'])
def process_payment():
    data = request.json
    result = gateway.process_payment(data)
    return jsonify(result)

@app.route('/api/gateway/qr/<merchant_id>', methods=['GET'])
def get_merchant_qr(merchant_id):
    amount = request.args.get('amount')
    result = gateway.generate_merchant_qr(merchant_id, amount)
    return jsonify(result)

@app.route('/api/gateway/commission', methods=['GET'])
def get_commission():
    """Track all commissions"""
    return jsonify({
        'total_transactions': 1000,
        'total_volume': 500000,
        'total_commission': 10000,
        'pending_settlement': 2500
    })

if __name__ == '__main__':
    app.run(debug=True)
