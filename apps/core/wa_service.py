import requests
import json
from django.conf import settings
from django.core.cache import cache

class FonnteService:
    """Service untuk mengirim WhatsApp menggunakan Fonnte API"""
    
    def __init__(self):
        self.api_key = settings.FONNTE_API_KEY
        self.base_url = settings.FONNTE_BASE_URL
        self.sender_name = "FamaLine"  # ← NAMA PENGIRIM
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def send_message(self, phone_number, message):
        """
        Kirim pesan teks ke nomor WhatsApp
        """
        phone_number = self._format_phone_number(phone_number)
        
        # PENTING: Gunakan parameter untuk menghilangkan watermark
        data = {
            'target': phone_number,
            'message': message,
            'countryCode': '62',
            'type': 'text',           # Gunakan 'text' bukan 'chat'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/send",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"WA sent to {phone_number}: {result}")
                return {'success': True, 'data': result}
            else:
                print(f"WA failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except requests.exceptions.RequestException as e:
            print(f"WA request error: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_otp(self, phone_number, otp_code):
        """Kirim kode OTP via WhatsApp"""
        message = f"""*{self.sender_name} - Kode Verifikasi*

Halo,

Kode verifikasi Anda adalah:

*{otp_code}*

Kode ini berlaku selama 5 menit. Jangan berikan kode ini kepada siapapun.

Terima kasih,
*Tim {self.sender_name}*
"""
        return self.send_message(phone_number, message)
    
    def send_template_taaruf(self, phone_number, name):
        """Kirim template pesan ta'aruf"""
        message = f"""*Assalamu'alaikum {name},*

Terima kasih telah mendaftar di Program Ta'aruf {self.sender_name}.

✅ Pendaftaran Anda telah kami terima.
📋 Tim mediator kami akan menghubungi Anda dalam 1x24 jam.

Jazakallah khair,
*Tim {self.sender_name} Ta'aruf* 🤝
"""
        return self.send_message(phone_number, message)
    
    def send_template_konsultasi(self, phone_number, name, psychologist, date, time, method):
        """Kirim template pesan konsultasi"""
        method_names = {
            'video': 'Video Call',
            'chat': 'Chat Konsultasi',
            'telepon': 'Telepon'
        }
        
        message = f"""*{self.sender_name} - Konsultasi*

Halo {name},

Booking konsultasi Anda telah kami terima!

📋 *Detail Konsultasi:*
👨‍⚕️ Psikolog: {psychologist}
📅 Tanggal: {date}
⏰ Waktu: {time}
💬 Metode: {method_names.get(method, method)}

Terima kasih,
*Tim {self.sender_name}* 🌿
"""
        return self.send_message(phone_number, message)
    
    def send_template_checkout(self, phone_number, name, kelas_nama, order_id, harga, payment_url):
        """Kirim template pesan checkout"""
        message = f"""*{self.sender_name} - Konfirmasi Order*

Halo {name},

Terima kasih telah melakukan pemesanan kelas!

📚 *Detail Kelas:*
🎓 Kelas: {kelas_nama}
💰 Harga: Rp{harga:,.0f}
🆔 Order ID: {order_id}

💳 *Link Pembayaran:*
{payment_url}

Terima kasih,
*{self.sender_name}* 🌿
"""
        return self.send_message(phone_number, message)
    
    def send_payment_success(self, phone_number, name, kelas_nama, order_id):
        """Kirim template pesan sukses pembayaran"""
        message = f"""*{self.sender_name} - Pembayaran Berhasil*

✅ Halo {name},

Pembayaran Anda untuk kelas *{kelas_nama}* telah kami terima!

🎉 Selamat! Anda sekarang memiliki akses penuh ke kelas.

🆔 Order ID: {order_id}

Silakan login ke akun Anda dan buka menu "Kelas Saya" untuk mulai belajar.

Terima kasih,
*{self.sender_name}* 🎓
"""
        return self.send_message(phone_number, message)
    
    def _format_phone_number(self, phone_number):
        """Format nomor telepon ke format yang benar untuk Fonnte"""
        phone = ''.join(filter(str.isdigit, phone_number))
        
        if phone.startswith('0'):
            phone = '62' + phone[1:]
        elif phone.startswith('8'):
            phone = '62' + phone
        
        return phone

# Instance global
wa_service = FonnteService()


def send_whatsapp_notification(phone_number, name, notification_type, **kwargs):
    """
    Fungsi helper untuk mengirim notifikasi WhatsApp
    """
    if notification_type == 'otp':
        return wa_service.send_otp(phone_number, kwargs.get('otp_code', ''))
    
    elif notification_type == 'taaruf':
        return wa_service.send_template_taaruf(phone_number, name)
    
    elif notification_type == 'konsultasi':
        return wa_service.send_template_konsultasi(
            phone_number, name,
            kwargs.get('psychologist', ''),
            kwargs.get('date', ''),
            kwargs.get('time', ''),
            kwargs.get('method', '')
        )
    
    elif notification_type == 'checkout':
        return wa_service.send_template_checkout(
            phone_number, name,
            kwargs.get('kelas_nama', ''),
            kwargs.get('order_id', ''),
            kwargs.get('harga', 0),
            kwargs.get('payment_url', '')
        )
    
    elif notification_type == 'payment_success':
        return wa_service.send_payment_success(
            phone_number, name,
            kwargs.get('kelas_nama', ''),
            kwargs.get('order_id', '')
        )
    
    return {'success': False, 'error': 'Unknown notification type'}


def send_otp_code(phone_number, otp_code):
    """Kirim kode OTP ke WhatsApp"""
    return send_whatsapp_notification(phone_number, '', 'otp', otp_code=otp_code)


def send_bulk_whatsapp(phone_numbers, message):
    """Kirim pesan ke banyak nomor"""
    results = []
    for phone in phone_numbers:
        result = wa_service.send_message(phone, message)
        results.append(result)
    return results
