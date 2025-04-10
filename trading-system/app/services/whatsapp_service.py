import requests
from config import Config
from typing import Dict, Optional
import logging

class WhatsAppService:
    def __init__(self):
        self.base_url = "https://api.whatsapp.com/v1/messages"
        self.headers = {
            "Authorization": f"Bearer {Config.WHATSAPP_API_KEY}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    def send_alert(self, alert: Dict, recipient: str) -> bool:
        """إرسال تنبيه تداول عبر الواتساب"""
        try:
            message = self._format_alert_message(alert)
            payload = self._create_payload(message, recipient)
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"تم إرسال إشعار الواتساب إلى {recipient}")
                return True
            else:
                self.logger.error(f"فشل إرسال الإشعار: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في إرسال إشعار الواتساب: {str(e)}")
            return False

    def _format_alert_message(self, alert: Dict) -> str:
        """تنسيق رسالة التنبيه باللغة العربية"""
        alert_type = {
            'price': 'تغير السعر',
            'volume': 'تغير الحجم',
            'rsi': 'إشارة RSI'
        }.get(alert['type'], 'تنبيه تداول')
        
        return (
            f"🚨 *{alert_type}*\n\n"
            f"📊 *الرمز*: {alert.get('symbol', 'N/A')}\n"
            f"📈 *القيمة الحالية*: {alert.get('value', 'N/A')}\n"
            f"📅 *الوقت*: {alert.get('time', 'N/A')}\n\n"
            f"📌 *التفاصيل*: {alert.get('message', '')}"
        )

    def _create_payload(self, message: str, recipient: str) -> Dict:
        """إنشاء هيكل رسالة الواتساب"""
        return {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": Config.WHATSAPP_TEMPLATE_NAME,
                "language": {"code": "ar"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": message}
                        ]
                    }
                ]
            }
        }
