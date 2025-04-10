import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # إعدادات البريد الإلكتروني
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    # إعدادات الواتساب
    WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
    WHATSAPP_PHONE_NUMBER = os.getenv('WHATSAPP_PHONE_NUMBER')
    WHATSAPP_TEMPLATE_NAME = os.getenv('WHATSAPP_TEMPLATE_NAME', 'trading_alerts')

    # إعدادات أخرى
    ALERT_INTERVAL = int(os.getenv('ALERT_INTERVAL', 30))
    MAX_ALERTS = int(os.getenv('MAX_ALERTS', 50))
