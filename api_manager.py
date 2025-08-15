#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير API لإرسال الطلبات الجديدة إلى النظام الخارجي
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import config

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.username = config.API_USERNAME
        self.password = config.API_PASSWORD
        self.timeout = config.API_TIMEOUT
        self.enabled = config.API_ENABLED
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Username": self.username,
            "X-API-Password": self.password
        }
    
    def send_order_to_api(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        إرسال الطلب الجديد إلى API
        
        Args:
            invoice_data: بيانات الفاتورة من قاعدة البيانات المحلية
            
        Returns:
            Dict: نتيجة الإرسال
        """
        # التحقق من تفعيل API
        if not self.enabled:
            logger.info("API معطل - تم تخطي إرسال الطلب")
            return {
                "success": False,
                "message": "API معطل حالياً"
            }
        
        try:
            # تحويل بيانات الفاتورة إلى تنسيق API
            api_data = self._convert_invoice_to_api_format(invoice_data)
            
            logger.info(f"إرسال طلب جديد إلى API: {invoice_data.get('receipt_number', 'غير محدد')}")
            
            # إرسال الطلب إلى API
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=api_data,
                timeout=self.timeout
            )
            
            # معالجة الاستجابة
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ تم إرسال الطلب بنجاح: {result.get('data', {}).get('order_id', 'غير محدد')}")
                return {
                    "success": True,
                    "message": "تم إرسال الطلب بنجاح",
                    "api_order_id": result.get('data', {}).get('order_id'),
                    "api_order_group_id": result.get('data', {}).get('order_group_id')
                }
            elif response.status_code == 409:
                # استخراج رسالة مختصرة من الرد
                short_message = self._extract_short_message(response.text)
                logger.error(f"❌ تكرار في الطلب: {response.text}")
                return {
                    "success": False,
                    "message": f"تكرار في الطلب: {short_message}",
                    "is_duplicate": True
                }
            elif response.status_code == 422:
                result = response.json()
                logger.error(f"❌ خطأ في التحقق من البيانات: {result.get('errors', {})}")
                return {
                    "success": False,
                    "message": "خطأ في التحقق من البيانات",
                    "errors": result.get('errors', {})
                }
            elif response.status_code == 401:
                # استخراج رسالة مختصرة من الرد
                short_message = self._extract_short_message(response.text)
                logger.error(f"❌ خطأ في المصادقة: {response.text}")
                return {
                    "success": False,
                    "message": f"خطأ في المصادقة: {short_message}"
                }
            elif response.status_code == 500:
                # استخراج رسالة مختصرة من الرد
                short_message = self._extract_short_message(response.text)
                logger.error(f"❌ خطأ في الخادم: {response.text}")
                return {
                    "success": False,
                    "message": f"خطأ في الخادم: {short_message}"
                }
            else:
                # استخراج رسالة مختصرة من الرد
                short_message = self._extract_short_message(response.text)
                logger.error(f"❌ خطأ غير متوقع: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"خطأ غير متوقع: {response.status_code} - {short_message}"
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ انتهت مهلة الاتصال بالخادم")
            return {
                "success": False,
                "message": "انتهت مهلة الاتصال بالخادم"
            }
        except requests.exceptions.ConnectionError:
            logger.error("❌ خطأ في الاتصال بالخادم")
            return {
                "success": False,
                "message": "خطأ في الاتصال بالخادم"
            }
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع: {str(e)}")
            return {
                "success": False,
                "message": f"خطأ غير متوقع: {str(e)}"
            }
    
    def _extract_short_message(self, response_text: str) -> str:
        """
        استخراج رسالة مختصرة من رد API
        
        Args:
            response_text: النص الكامل للرد من API
            
        Returns:
            str: رسالة مختصرة
        """
        try:
            # محاولة تحليل JSON
            import json
            data = json.loads(response_text)
            
            # البحث عن رسالة في الحقول الشائعة
            message_fields = ['message', 'error', 'msg', 'description', 'detail']
            for field in message_fields:
                if field in data and data[field]:
                    message = str(data[field])
                    # تقصير الرسالة إذا كانت طويلة
                    if len(message) > 100:
                        message = message[:100] + "..."
                    return message
            
            # إذا لم نجد رسالة، نعيد أول 100 حرف من النص
            if len(response_text) > 100:
                return response_text[:100] + "..."
            return response_text
            
        except (json.JSONDecodeError, TypeError):
            # إذا فشل تحليل JSON، نعيد أول 100 حرف
            if len(response_text) > 100:
                return response_text[:100] + "..."
            return response_text

    def _convert_invoice_to_api_format(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تحويل بيانات الفاتورة المحلية إلى تنسيق API
        
        Args:
            invoice_data: بيانات الفاتورة من قاعدة البيانات المحلية
            
        Returns:
            Dict: بيانات الطلب بتنسيق API
        """
        # تحويل المحافظة إلى مدينة (يمكن تعديلها حسب الحاجة)
        city_mapping = {
            "الانبار": "الأنبار",
            "بغداد": "بغداد",
            "البصرة": "البصرة",
            "الموصل": "الموصل",
            "النجف": "النجف",
            "كربلاء": "كربلاء",
            "الديوانية": "الديوانية",
            "الزبير": "الزبير",
            "الرمادي": "الرمادي",
            "الفلوجة": "الفلوجة"
        }
        
        governorate = invoice_data.get('governorate', '')
        city = city_mapping.get(governorate, governorate)
        
        # تحويل بيانات العنوان
        shipping_address = {
            "contact_person_name": invoice_data.get('client_name', ''),
            "phone": invoice_data.get('client_phone', ''),
            "country": "العراق",
            "city": city,
            "zip": "00000",  # رمز بريدي افتراضي
            "address": f"{governorate} - {invoice_data.get('nearest_point', '')}",
            "latitude": 33.3152,  # إحداثيات افتراضية للعراق
            "longitude": 44.3661,
            "floor": "",
            "flat": "",
            "house": "",
            "street": invoice_data.get('nearest_point', ''),
            "avenue": "",
            "piece": ""
        }
        
        # تحويل تفاصيل المنتج (افتراضي - يمكن تعديله)
        order_details = [
            {
                "product_id": 1,  # معرف افتراضي للمنتج
                "qty": invoice_data.get('quantity', 1),
                "price": invoice_data.get('price', 0),
                "tax": 0,
                "discount": 0,
                "tax_model": "exclude",
                "variant": "",
                "variation": ""
            }
        ]
        
        # تجميع بيانات API
        api_data = {
            "customer_id": 1,  # معرف افتراضي للعميل
            "order_amount": invoice_data.get('total_sales', 0),
            "payment_method": "cash_on_delivery",
            "order_status": "pending",
            "payment_status": "unpaid",
            "order_note": invoice_data.get('notes', ''),
            "shipping_address_data": shipping_address,
            "order_details": order_details,
            "seller_id": 1,  # معرف افتراضي للبائع
            "shipping_cost": 0,
            "discount_amount": 0,
            "coupon_code": "",
            "delivery_man_id": None,
            "deliveryman_charge": 0,
            "expected_delivery_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return api_data
    
    def test_api_connection(self) -> Dict[str, Any]:
        """
        اختبار الاتصال بـ API
        
        Returns:
            Dict: نتيجة الاختبار
        """
        try:
            # بيانات اختبار بسيطة
            test_data = {
                "customer_id": 1,
                "order_amount": 100.00,
                "payment_method": "cash_on_delivery",
                "shipping_address_data": {
                    "contact_person_name": "اختبار",
                    "phone": "+964700000000",
                    "country": "العراق",
                    "city": "بغداد",
                    "zip": "00000",
                    "address": "عنوان اختبار"
                },
                "order_details": [
                    {
                        "product_id": 1,
                        "qty": 1,
                        "price": 100.00
                    }
                ]
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code in [201, 422]:  # 422 يعني خطأ في البيانات ولكن الاتصال يعمل
                return {
                    "success": True,
                    "message": "الاتصال بـ API يعمل بشكل صحيح",
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "message": f"خطأ في الاتصال: {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في الاتصال: {str(e)}"
            }

# إنشاء نسخة عامة من مدير API
api_manager = APIManager()
