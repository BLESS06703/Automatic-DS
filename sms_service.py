# sms_service.py - Send SMS notifications (Free using Twilio trial)
import requests

class SMSService:
    def __init__(self):
        # Twilio free trial (get these from twilio.com)
        # Sign up for free account - they give you $15 free credit
        self.account_sid = "YOUR_TWILIO_SID"  # Get from twilio.com
        self.auth_token = "YOUR_TWILIO_TOKEN"  # Get from twilio.com
        self.from_number = "+1234567890"  # Your Twilio number
        
    def send_status_update(self, to_number, customer_name, status, vehicle_info):
        """Send SMS about diagnostic status"""
        message = f"""
        Bless Digital Auto Care: {customer_name}, your {vehicle_info['make']} {vehicle_info['model']} 
        diagnostic is {status}. {self.get_status_message(status)}
        """
        
        # For testing without SMS, just print
        print(f"📱 SMS to {to_number}: {message}")
        return True
        
        # Uncomment when you have Twilio account
        # client = Client(self.account_sid, self.auth_token)
        # message = client.messages.create(
        #     body=message[:160],  # SMS limit
        #     from_=self.from_number,
        #     to=to_number
        # )
        # return message.sid
    
    def get_status_message(self, status):
        messages = {
            'pending': "We'll update you when analysis is complete.",
            'completed': "Your vehicle is ready for pickup!",
            'urgent': "Please contact us immediately regarding your vehicle."
        }
        return messages.get(status, "Thank you for choosing us.")
