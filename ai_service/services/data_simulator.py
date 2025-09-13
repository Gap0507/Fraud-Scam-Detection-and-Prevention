"""
Data Simulator for SMS Scam Detection
Generates realistic SMS messages for testing and training
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataSimulator:
    def __init__(self):
        self.scam_templates = {
            "arrest_scam": [
                "URGENT: You have an outstanding warrant. Call {phone} immediately or face arrest.",
                "POLICE NOTICE: Your account is under investigation. Verify identity at {url} or face legal action.",
                "WARRANT ISSUED: Immediate payment of ${amount} required. Call {phone} now to avoid arrest.",
                "FBI ALERT: Your social security number is compromised. Call {phone} immediately.",
                "COURT NOTICE: You must appear in court. Call {phone} to confirm or face arrest."
            ],
            "bank_scam": [
                "BANK ALERT: Unusual activity detected. Verify account at {url} or account will be closed.",
                "URGENT: Your account is suspended. Call {phone} immediately to reactivate.",
                "SECURITY ALERT: Login required. Click {url} to verify or account will be frozen.",
                "FRAUD DETECTED: Transfer ${amount} to secure account. Call {phone} now.",
                "ACCOUNT SUSPENDED: Verify identity at {url} within 24 hours or lose access."
            ],
            "otp_scam": [
                "Your OTP is {otp}. Do not share with anyone. Valid for 5 minutes.",
                "Verification code: {otp}. Enter this code to confirm your identity.",
                "SECURITY CODE: {otp}. Use this code to verify your account.",
                "OTP: {otp}. This code expires in 10 minutes. Do not share.",
                "Your verification code is {otp}. Enter it to complete the process."
            ],
            "payment_scam": [
                "URGENT: Transfer ${amount} to {account} immediately or face consequences.",
                "PAYMENT REQUIRED: Send ${amount} via {method} to avoid account closure.",
                "IMMEDIATE PAYMENT: ${amount} due now. Pay via {method} or face legal action.",
                "WIRE TRANSFER: Send ${amount} to {account} to resolve this matter.",
                "CRYPTO PAYMENT: Send {amount} Bitcoin to {address} immediately."
            ],
            "prize_scam": [
                "CONGRATULATIONS! You've won ${amount}! Call {phone} to claim your prize.",
                "YOU'RE A WINNER! Claim your ${amount} prize at {url} now!",
                "PRIZE ALERT: You've won a free vacation! Call {phone} to claim.",
                "LUCKY WINNER: You've won ${amount} in our lottery! Visit {url} to claim.",
                "CONGRATS! You've won a free iPhone! Call {phone} immediately to claim."
            ],
            "tax_scam": [
                "IRS ALERT: Tax refund of ${amount} pending. Verify at {url} to receive.",
                "TAX NOTICE: You owe ${amount} in back taxes. Pay now or face penalties.",
                "IRS INVESTIGATION: Your tax return is under review. Call {phone} immediately.",
                "TAX REFUND: ${amount} available. Click {url} to claim your refund.",
                "IRS NOTICE: Immediate payment of ${amount} required. Call {phone} now."
            ]
        }
        
        self.legitimate_templates = {
            "bank_notification": [
                "Your account balance is ${amount}. Thank you for banking with us.",
                "Transaction alert: ${amount} withdrawn from your account on {date}.",
                "Your monthly statement is ready. View at {url} or call {phone}.",
                "Account update: Your new debit card has been mailed to your address.",
                "Security notice: Your password was changed successfully."
            ],
            "appointment_reminder": [
                "Reminder: You have an appointment with Dr. Smith on {date} at {time}.",
                "Appointment confirmed: {date} at {time}. Please arrive 15 minutes early.",
                "Your appointment has been rescheduled to {date} at {time}.",
                "Appointment reminder: {date} at {time}. Call {phone} if you need to reschedule.",
                "Your appointment is tomorrow at {time}. Please confirm by replying YES."
            ],
            "delivery_notification": [
                "Your package has been delivered to {address} on {date}.",
                "Delivery update: Your order will arrive between {time1} and {time2}.",
                "Package delivered: {item} was left at your front door.",
                "Delivery confirmation: Your order has been delivered successfully.",
                "Your package is out for delivery. Expected arrival: {time}."
            ],
            "verification_legitimate": [
                "Your verification code is {otp}. This code expires in 10 minutes.",
                "Security code: {otp}. Use this code to complete your login.",
                "Verification required: Enter code {otp} to verify your identity.",
                "Your login code is {otp}. Do not share this code with anyone.",
                "Two-factor authentication code: {otp}. Valid for 5 minutes."
            ]
        }
        
        self.phone_numbers = [
            "555-0123", "555-0456", "555-0789", "555-0321", "555-0654",
            "555-0987", "555-0111", "555-0222", "555-0333", "555-0444"
        ]
        
        self.urls = [
            "https://secure-bank.com", "https://verify-account.net", "https://official-gov.org",
            "https://my-bank.com", "https://account-verify.com", "https://secure-login.net"
        ]
        
        self.amounts = ["100", "250", "500", "1000", "2500", "5000", "10000"]
        self.otp_codes = ["123456", "654321", "789012", "345678", "901234"]
        self.dates = ["2024-12-01", "2024-12-02", "2024-12-03", "2024-12-04", "2024-12-05"]
        self.times = ["9:00 AM", "10:30 AM", "2:00 PM", "3:30 PM", "4:45 PM"]
        self.addresses = ["123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm St", "654 Maple Dr"]
        self.items = ["iPhone", "laptop", "package", "documents", "medication"]
        self.methods = ["PayPal", "Venmo", "Zelle", "Bitcoin", "wire transfer"]
        self.accounts = ["1234567890", "9876543210", "5555666677", "1111222233", "4444555566"]
        self.addresses_crypto = ["1A2B3C4D5E6F7G8H9I0J", "9Z8Y7X6W5V4U3T2S1R0Q", "5M4N3B2V1C0X9Z8Y7W6E"]
    
    async def generate_sms_data(self, count: int = 100, scam_ratio: float = 0.5) -> List[Dict[str, Any]]:
        """
        Generate SMS data for testing
        Args:
            count: Number of SMS messages to generate
            scam_ratio: Ratio of scam messages (0.0 to 1.0)
        """
        messages = []
        scam_count = int(count * scam_ratio)
        legitimate_count = count - scam_count
        
        # Generate scam messages
        for i in range(scam_count):
            message_data = await self._generate_scam_sms()
            messages.append(message_data)
        
        # Generate legitimate messages
        for i in range(legitimate_count):
            message_data = await self._generate_legitimate_sms()
            messages.append(message_data)
        
        # Shuffle the messages
        random.shuffle(messages)
        
        return messages
    
    async def _generate_scam_sms(self) -> Dict[str, Any]:
        """Generate a single scam SMS message"""
        scam_type = random.choice(list(self.scam_templates.keys()))
        template = random.choice(self.scam_templates[scam_type])
        
        # Replace placeholders
        message = template.format(
            phone=random.choice(self.phone_numbers),
            url=random.choice(self.urls),
            amount=random.choice(self.amounts),
            otp=random.choice(self.otp_codes),
            account=random.choice(self.accounts),
            method=random.choice(self.methods),
            address=random.choice(self.addresses_crypto)
        )
        
        # Add some variation
        message = self._add_variation(message)
        
        return {
            "message": message,
            "sender": random.choice(self.phone_numbers),
            "timestamp": self._random_timestamp(),
            "is_scam": True,
            "scam_type": scam_type,
            "channel": "sms"
        }
    
    async def _generate_legitimate_sms(self) -> Dict[str, Any]:
        """Generate a single legitimate SMS message"""
        legitimate_type = random.choice(list(self.legitimate_templates.keys()))
        template = random.choice(self.legitimate_templates[legitimate_type])
        
        # Replace placeholders
        message = template.format(
            phone=random.choice(self.phone_numbers),
            url=random.choice(self.urls),
            amount=random.choice(self.amounts),
            otp=random.choice(self.otp_codes),
            date=random.choice(self.dates),
            time=random.choice(self.times),
            time1=random.choice(self.times),
            time2=random.choice(self.times),
            address=random.choice(self.addresses),
            item=random.choice(self.items)
        )
        
        # Add some variation
        message = self._add_variation(message)
        
        return {
            "message": message,
            "sender": random.choice(self.phone_numbers),
            "timestamp": self._random_timestamp(),
            "is_scam": False,
            "legitimate_type": legitimate_type,
            "channel": "sms"
        }
    
    def _add_variation(self, message: str) -> str:
        """Add natural variation to the message"""
        # Randomly add or remove punctuation
        if random.random() < 0.3:
            if message.endswith('.'):
                message = message[:-1]
            elif not message.endswith(('!', '?', '.')):
                message += random.choice(['.', '!', '?'])
        
        # Randomly add extra spaces or remove them
        if random.random() < 0.2:
            message = message.replace('  ', ' ')
        
        # Randomly change case
        if random.random() < 0.1:
            message = message.upper()
        elif random.random() < 0.1:
            message = message.lower()
        
        return message
    
    def _random_timestamp(self) -> str:
        """Generate a random timestamp within the last 7 days"""
        now = datetime.now()
        random_days = random.randint(0, 7)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        
        timestamp = now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        return timestamp.isoformat()
    
    async def generate_test_dataset(self, train_count: int = 800, test_count: int = 200) -> Dict[str, Any]:
        """Generate a complete test dataset"""
        logger.info(f"Generating test dataset: {train_count} train, {test_count} test")
        
        # Generate training data
        train_data = await self.generate_sms_data(train_count, scam_ratio=0.5)
        
        # Generate test data
        test_data = await self.generate_sms_data(test_count, scam_ratio=0.5)
        
        # Calculate statistics
        train_scam_count = sum(1 for item in train_data if item["is_scam"])
        test_scam_count = sum(1 for item in test_data if item["is_scam"])
        
        return {
            "train": train_data,
            "test": test_data,
            "statistics": {
                "train_total": len(train_data),
                "train_scam": train_scam_count,
                "train_legitimate": len(train_data) - train_scam_count,
                "test_total": len(test_data),
                "test_scam": test_scam_count,
                "test_legitimate": len(test_data) - test_scam_count
            }
        }
    
    async def generate_specific_scam_type(self, scam_type: str, count: int = 50) -> List[Dict[str, Any]]:
        """Generate specific type of scam messages"""
        if scam_type not in self.scam_templates:
            raise ValueError(f"Unknown scam type: {scam_type}")
        
        messages = []
        for _ in range(count):
            template = random.choice(self.scam_templates[scam_type])
            message = template.format(
                phone=random.choice(self.phone_numbers),
                url=random.choice(self.urls),
                amount=random.choice(self.amounts),
                otp=random.choice(self.otp_codes),
                account=random.choice(self.accounts),
                method=random.choice(self.methods),
                address=random.choice(self.addresses_crypto)
            )
            
            message = self._add_variation(message)
            
            messages.append({
                "message": message,
                "sender": random.choice(self.phone_numbers),
                "timestamp": self._random_timestamp(),
                "is_scam": True,
                "scam_type": scam_type,
                "channel": "sms"
            })
        
        return messages
    
    async def save_dataset(self, data: List[Dict[str, Any]], filename: str):
        """Save dataset to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Dataset saved to {filename}")
    
    async def load_dataset(self, filename: str) -> List[Dict[str, Any]]:
        """Load dataset from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Dataset loaded from {filename}")
        return data
