class CommissionTracker:
    """Track all commissions for Singh Ji Gateway"""
    
    def __init__(self):
        self.rates = {
            'upi': 0.0,      # 0% - Govt rule
            'card': 0.02,    # 2%
            'wallet': 0.015, # 1.5%
            'international': 0.03  # 3%
        }
    
    def calculate(self, amount, method):
        rate = self.rates.get(method, 0.02)
        commission = amount * rate
        gst = commission * 0.18  # 18% GST
        
        return {
            'amount': amount,
            'method': method,
            'commission_rate': rate * 100,
            'commission': commission,
            'gst': gst,
            'net_to_merchant': amount - commission - gst,
            'singh_ji_earns': commission * 0.5  # 50% of commission
        }
    
    def monthly_report(self, merchant_id):
        return {
            'merchant_id': merchant_id,
            'month': 'June 2026',
            'total_transactions': 500,
            'total_volume': 250000,
            'total_commission': 5000,
            'singh_ji_share': 2500,
            'status': 'paid'
        }

# Example
tracker = CommissionTracker()
print(tracker.calculate(1000, 'card'))
# {'amount': 1000, 'commission': 20, 'singh_ji_earns': 10, ...}
