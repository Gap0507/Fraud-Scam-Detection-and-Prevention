"""
Email Data Simulator for Phishing Detection
Generates realistic phishing and legitimate emails for testing and training
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EmailDataSimulator:
    def __init__(self):
        self.phishing_templates = {
            "phishing_bank": [
                {
                    "subject": "URGENT: Your account has been compromised!",
                    "body": "Dear Customer,\n\nWe have detected suspicious activity on your account. To protect your account, please verify your identity immediately by clicking the link below:\n\n{link}\n\nIf you do not verify within 24 hours, your account will be suspended.\n\nBest regards,\nSecurity Team\n{bank_name}"
                },
                {
                    "subject": "Account Suspension Notice - Action Required",
                    "body": "Hello,\n\nYour account has been temporarily suspended due to security concerns. To reactivate your account, please:\n\n1. Click here: {link}\n2. Enter your login credentials\n3. Verify your identity\n\nThis is urgent - please act now to avoid permanent closure.\n\n{bank_name} Security Department"
                }
            ],
            "phishing_payment": [
                {
                    "subject": "Payment Verification Required",
                    "body": "Dear Valued Customer,\n\nWe need to verify your payment information to prevent fraud. Please click the link below to update your payment details:\n\n{link}\n\nFailure to verify within 48 hours will result in service interruption.\n\nThank you for your cooperation.\n\nPayment Security Team"
                },
                {
                    "subject": "Invoice Payment Overdue - Immediate Action Required",
                    "body": "Your invoice payment is overdue. To avoid late fees and service interruption, please pay immediately:\n\nAmount: ${amount}\nDue Date: {date}\n\nPay Now: {link}\n\nIf you have already paid, please ignore this email.\n\nAccounts Receivable"
                }
            ],
            "phishing_tech": [
                {
                    "subject": "Microsoft Security Alert - Account Compromised",
                    "body": "Microsoft Security Center\n\nWe detected unusual sign-in activity on your Microsoft account. Someone may have accessed your account from an unrecognized device.\n\nLocation: {location}\nTime: {time}\n\nIf this wasn't you, secure your account immediately:\n{link}\n\nMicrosoft Security Team"
                },
                {
                    "subject": "Apple ID Security - Verification Required",
                    "body": "Apple ID Security Alert\n\nYour Apple ID has been locked for security reasons. To unlock your account, please verify your identity:\n\n{link}\n\nThis verification must be completed within 24 hours or your account will be permanently disabled.\n\nApple Support"
                }
            ],
            "phishing_government": [
                {
                    "subject": "IRS Tax Refund - Action Required",
                    "body": "Internal Revenue Service\n\nYou have a pending tax refund of ${amount}. To process your refund, please verify your information:\n\n{link}\n\nThis is time-sensitive. Please complete verification within 7 days.\n\nIRS Tax Department"
                },
                {
                    "subject": "Social Security Administration - Account Update",
                    "body": "Social Security Administration\n\nYour Social Security account requires immediate attention. Please update your information to maintain benefits:\n\n{link}\n\nFailure to update may result in benefit suspension.\n\nSSA Administration"
                }
            ],
            "phishing_shopping": [
                {
                    "subject": "Order Confirmation - Payment Issue",
                    "body": "Thank you for your order! However, we encountered an issue processing your payment.\n\nOrder #: {order_number}\nAmount: ${amount}\n\nPlease update your payment information:\n{link}\n\nYour order will be processed once payment is confirmed.\n\nCustomer Service"
                },
                {
                    "subject": "Amazon Account - Security Verification",
                    "body": "Amazon Security Team\n\nWe noticed unusual activity on your Amazon account. To protect your account, please verify your identity:\n\n{link}\n\nThis verification is required to continue using your account.\n\nAmazon Security"
                }
            ],
            "phishing_lottery": [
                {
                    "subject": "Congratulations! You've Won $50,000!",
                    "body": "Congratulations!\n\nYou have been selected as the winner of our annual lottery! You have won $50,000!\n\nTo claim your prize, please provide your personal information:\n{link}\n\nThis offer expires in 48 hours. Don't miss out!\n\nLottery Department"
                },
                {
                    "subject": "You're a Winner! Claim Your Prize Now",
                    "body": "Congratulations! You've won our grand prize!\n\nPrize: ${amount}\n\nTo claim your prize, please click the link below and provide your details:\n{link}\n\nWinners must claim within 24 hours.\n\nPrize Department"
                }
            ]
        }
        
        self.legitimate_templates = {
            "bank_notification": [
                {
                    "subject": "Account Statement Available",
                    "body": "Dear Customer,\n\nYour monthly account statement is now available online. You can view it by logging into your account at {bank_url} or by calling us at {phone}.\n\nThank you for banking with us.\n\n{bank_name} Customer Service"
                },
                {
                    "subject": "Transaction Alert",
                    "body": "Transaction Alert\n\nA transaction of ${amount} was made on your account on {date} at {time}.\n\nIf you did not make this transaction, please contact us immediately at {phone}.\n\n{bank_name} Security Team"
                }
            ],
            "appointment_reminder": [
                {
                    "subject": "Appointment Reminder - Tomorrow at {time}",
                    "body": "Hello,\n\nThis is a reminder that you have an appointment scheduled for tomorrow at {time} with Dr. {doctor_name}.\n\nPlease arrive 15 minutes early. If you need to reschedule, please call {phone}.\n\nThank you,\n{clinic_name}"
                },
                {
                    "subject": "Your Appointment is Confirmed",
                    "body": "Your appointment has been confirmed:\n\nDate: {date}\nTime: {time}\nLocation: {location}\n\nPlease bring a valid ID and insurance card.\n\n{clinic_name} Scheduling"
                }
            ],
            "delivery_notification": [
                {
                    "subject": "Your Package Has Been Delivered",
                    "body": "Good news! Your package has been delivered.\n\nTracking Number: {tracking}\nDelivered to: {address}\nTime: {time}\n\nThank you for choosing {company}!\n\nDelivery Team"
                },
                {
                    "subject": "Package Out for Delivery",
                    "body": "Your package is out for delivery and should arrive today between {time1} and {time2}.\n\nTracking: {tracking}\n\nYou can track your package at {tracking_url}\n\n{company} Delivery"
                }
            ],
            "newsletter": [
                {
                    "subject": "Weekly Newsletter - {date}",
                    "body": "Hello,\n\nHere's your weekly newsletter with the latest updates:\n\n- New features released\n- Upcoming events\n- Tips and tricks\n\nRead more: {newsletter_url}\n\nBest regards,\n{company_name} Team"
                },
                {
                    "subject": "Monthly Update from {company_name}",
                    "body": "Thank you for being a valued customer!\n\nThis month's highlights:\n- New product launches\n- Customer success stories\n- Industry insights\n\nView full update: {newsletter_url}\n\n{company_name} Marketing Team"
                }
            ],
            "verification_legitimate": [
                {
                    "subject": "Email Verification Required",
                    "body": "Please verify your email address to complete your registration.\n\nClick here to verify: {verification_link}\n\nThis link will expire in 24 hours.\n\nIf you didn't create an account, please ignore this email.\n\n{company_name} Support"
                },
                {
                    "subject": "Two-Factor Authentication Code",
                    "body": "Your two-factor authentication code is: {code}\n\nThis code will expire in 10 minutes.\n\nIf you didn't request this code, please secure your account immediately.\n\n{company_name} Security"
                }
            ]
        }
        
        self.sender_emails = [
            "noreply@bank.com", "security@microsoft.com", "support@apple.com",
            "noreply@amazon.com", "notifications@paypal.com", "alerts@chase.com",
            "security@wellsfargo.com", "support@citibank.com", "noreply@irs.gov",
            "info@ssa.gov", "support@google.com", "noreply@facebook.com"
        ]
        
        self.phishing_emails = [
            "security@bank-verify.com", "support@microsoft-security.net",
            "noreply@apple-verification.org", "alerts@amazon-payment.tk",
            "security@paypal-verify.ml", "support@chase-security.ga",
            "noreply@wells-fargo-verify.cf", "alerts@citi-bank-security.cc",
            "security@irs-verification.info", "support@ssa-update.gq"
        ]
        
        self.links = [
            "https://secure-bank.com/verify", "https://microsoft-security.net/login",
            "https://apple-verification.org/account", "https://amazon-payment.tk/update",
            "https://paypal-verify.ml/confirm", "https://chase-security.ga/verify",
            "https://wells-fargo-verify.cf/login", "https://citi-bank-security.cc/update",
            "https://irs-verification.info/refund", "https://ssa-update.gq/benefits"
        ]
        
        self.legitimate_links = [
            "https://www.bankofamerica.com", "https://account.microsoft.com",
            "https://appleid.apple.com", "https://www.amazon.com",
            "https://www.paypal.com", "https://secure.chase.com",
            "https://connect.wellsfargo.com", "https://online.citi.com",
            "https://www.irs.gov", "https://www.ssa.gov"
        ]
        
        self.amounts = ["100", "250", "500", "1000", "2500", "5000", "10000", "25000", "50000"]
        self.order_numbers = ["ORD-123456", "INV-789012", "REF-345678", "TXN-901234", "PAY-567890"]
        self.tracking_numbers = ["1Z999AA1234567890", "9400111206213857246182", "1Z999BB9876543210"]
        self.phone_numbers = ["1-800-555-0123", "1-800-555-0456", "1-800-555-0789", "1-800-555-0321"]
        self.dates = ["2024-12-01", "2024-12-02", "2024-12-03", "2024-12-04", "2024-12-05"]
        self.times = ["9:00 AM", "10:30 AM", "2:00 PM", "3:30 PM", "4:45 PM"]
        self.locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ"]
        self.addresses = ["123 Main St, Anytown, ST 12345", "456 Oak Ave, Somewhere, ST 67890"]
        self.companies = ["Bank of America", "Wells Fargo", "Chase", "Citibank", "Microsoft", "Apple", "Google", "Amazon"]
        self.doctors = ["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", "Dr. Davis"]
        self.clinics = ["City Medical Center", "Downtown Clinic", "Health Plus", "Family Care", "Wellness Center"]
    
    async def generate_email_data(self, count: int = 100, phishing_ratio: float = 0.5) -> List[Dict[str, Any]]:
        """
        Generate email data for testing
        Args:
            count: Number of emails to generate
            phishing_ratio: Ratio of phishing emails (0.0 to 1.0)
        """
        emails = []
        phishing_count = int(count * phishing_ratio)
        legitimate_count = count - phishing_count
        
        # Generate phishing emails
        for i in range(phishing_count):
            email_data = await self._generate_phishing_email()
            emails.append(email_data)
        
        # Generate legitimate emails
        for i in range(legitimate_count):
            email_data = await self._generate_legitimate_email()
            emails.append(email_data)
        
        # Shuffle the emails
        random.shuffle(emails)
        
        return emails
    
    async def _generate_phishing_email(self) -> Dict[str, Any]:
        """Generate a single phishing email"""
        phishing_type = random.choice(list(self.phishing_templates.keys()))
        template = random.choice(self.phishing_templates[phishing_type])
        
        # Replace placeholders
        subject = template["subject"]
        body = template["body"]
        
        # Replace common placeholders
        replacements = {
            "{link}": random.choice(self.links),
            "{amount}": random.choice(self.amounts),
            "{date}": random.choice(self.dates),
            "{time}": random.choice(self.times),
            "{location}": random.choice(self.locations),
            "{order_number}": random.choice(self.order_numbers),
            "{bank_name}": random.choice(self.companies),
            "{phone}": random.choice(self.phone_numbers)
        }
        
        for placeholder, value in replacements.items():
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)
        
        # Add some variation
        subject = self._add_variation(subject)
        body = self._add_variation(body)
        
        return {
            "subject": subject,
            "body": body,
            "sender": random.choice(self.phishing_emails),
            "timestamp": self._random_timestamp(),
            "is_phishing": True,
            "phishing_type": phishing_type,
            "channel": "email"
        }
    
    async def _generate_legitimate_email(self) -> Dict[str, Any]:
        """Generate a single legitimate email"""
        legitimate_type = random.choice(list(self.legitimate_templates.keys()))
        template = random.choice(self.legitimate_templates[legitimate_type])
        
        # Replace placeholders
        subject = template["subject"]
        body = template["body"]
        
        # Replace common placeholders
        replacements = {
            "{link}": random.choice(self.legitimate_links),
            "{verification_link}": random.choice(self.legitimate_links),
            "{newsletter_url}": random.choice(self.legitimate_links),
            "{tracking_url}": random.choice(self.legitimate_links),
            "{bank_url}": random.choice(self.legitimate_links),
            "{amount}": random.choice(self.amounts),
            "{date}": random.choice(self.dates),
            "{time}": random.choice(self.times),
            "{time1}": random.choice(self.times),
            "{time2}": random.choice(self.times),
            "{tracking}": random.choice(self.tracking_numbers),
            "{address}": random.choice(self.addresses),
            "{phone}": random.choice(self.phone_numbers),
            "{bank_name}": random.choice(self.companies),
            "{company_name}": random.choice(self.companies),
            "{company}": random.choice(self.companies),
            "{doctor_name}": random.choice(self.doctors),
            "{clinic_name}": random.choice(self.clinics),
            "{code}": str(random.randint(100000, 999999))
        }
        
        for placeholder, value in replacements.items():
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)
        
        # Add some variation
        subject = self._add_variation(subject)
        body = self._add_variation(body)
        
        return {
            "subject": subject,
            "body": body,
            "sender": random.choice(self.sender_emails),
            "timestamp": self._random_timestamp(),
            "is_phishing": False,
            "legitimate_type": legitimate_type,
            "channel": "email"
        }
    
    def _add_variation(self, text: str) -> str:
        """Add natural variation to the text"""
        # Randomly add or remove punctuation
        if random.random() < 0.2:
            if text.endswith('.'):
                text = text[:-1]
            elif not text.endswith(('!', '?', '.')):
                text += random.choice(['.', '!', '?'])
        
        # Randomly add extra spaces or remove them
        if random.random() < 0.1:
            text = text.replace('  ', ' ')
        
        # Randomly change case (rare)
        if random.random() < 0.05:
            text = text.upper()
        elif random.random() < 0.05:
            text = text.lower()
        
        return text
    
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
        logger.info(f"Generating email test dataset: {train_count} train, {test_count} test")
        
        # Generate training data
        train_data = await self.generate_email_data(train_count, phishing_ratio=0.5)
        
        # Generate test data
        test_data = await self.generate_email_data(test_count, phishing_ratio=0.5)
        
        # Calculate statistics
        train_phishing_count = sum(1 for item in train_data if item["is_phishing"])
        test_phishing_count = sum(1 for item in test_data if item["is_phishing"])
        
        return {
            "train": train_data,
            "test": test_data,
            "statistics": {
                "train_total": len(train_data),
                "train_phishing": train_phishing_count,
                "train_legitimate": len(train_data) - train_phishing_count,
                "test_total": len(test_data),
                "test_phishing": test_phishing_count,
                "test_legitimate": len(test_data) - test_phishing_count
            }
        }
    
    async def generate_specific_phishing_type(self, phishing_type: str, count: int = 50) -> List[Dict[str, Any]]:
        """Generate specific type of phishing emails"""
        if phishing_type not in self.phishing_templates:
            raise ValueError(f"Unknown phishing type: {phishing_type}")
        
        emails = []
        for _ in range(count):
            template = random.choice(self.phishing_templates[phishing_type])
            
            subject = template["subject"]
            body = template["body"]
            
            # Replace placeholders
            replacements = {
                "{link}": random.choice(self.links),
                "{amount}": random.choice(self.amounts),
                "{date}": random.choice(self.dates),
                "{time}": random.choice(self.times),
                "{location}": random.choice(self.locations),
                "{order_number}": random.choice(self.order_numbers),
                "{bank_name}": random.choice(self.companies),
                "{phone}": random.choice(self.phone_numbers)
            }
            
            for placeholder, value in replacements.items():
                subject = subject.replace(placeholder, value)
                body = body.replace(placeholder, value)
            
            subject = self._add_variation(subject)
            body = self._add_variation(body)
            
            emails.append({
                "subject": subject,
                "body": body,
                "sender": random.choice(self.phishing_emails),
                "timestamp": self._random_timestamp(),
                "is_phishing": True,
                "phishing_type": phishing_type,
                "channel": "email"
            })
        
        return emails
    
    async def save_dataset(self, data: List[Dict[str, Any]], filename: str):
        """Save dataset to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Email dataset saved to {filename}")
    
    async def load_dataset(self, filename: str) -> List[Dict[str, Any]]:
        """Load dataset from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Email dataset loaded from {filename}")
        return data
