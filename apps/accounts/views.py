from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, BACKEND_SESSION_KEY
from django.contrib.auth.backends import ModelBackend
import json
import logging
import requests
from django.conf import settings


logger = logging.getLogger(__name__)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Set backend
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, f'Selamat datang kembali, {username}!')
                next_url = request.GET.get('next', 'core:index')
                return redirect(next_url)
        messages.error(request, 'Username atau password salah.')
    
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save phone number if provided
            phone = request.POST.get('phone', '')
            if phone:
                user.profile.phone = phone  # You need to create a Profile model
            login(request, user)
            messages.success(request, 'Akun berhasil dibuat! Selamat bergabung.')
            return redirect('core:index')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    form = UserCreationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Anda telah logout.')
    return redirect('core:index')

@csrf_exempt
def send_wa_otp(request):
    """API endpoint to send OTP via Fonnte"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            message = data.get('message')
            
            # Format phone number
            if phone_number.startswith('0'):
                phone_number = '62' + phone_number[1:]
            elif not phone_number.startswith('62'):
                phone_number = '62' + phone_number
            
            # Send via Fonnte API
            headers = {
                'Authorization': settings.FONNTE_API_KEY,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'target': phone_number,
                'message': message,
                'countryCode': '62',
                'type': 'text',           # TAMBAHKAN INI
                'gateway': 'individual'   # TAMBAHKAN INI
            }
            
            response = requests.post(
                f"{settings.FONNTE_BASE_URL}/send",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': response.text})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})



@csrf_exempt
def whatsapp_login(request):
    """Handle WhatsApp login"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            
            # Bersihkan nomor telepon
            raw_number = phone_number.strip()
            
            # Format nomor ke format internasional (62xxx)
            phone_clean = ''.join(filter(str.isdigit, raw_number))
            if phone_clean.startswith('0'):
                phone_clean = '62' + phone_clean[1:]
            elif phone_clean.startswith('8'):
                phone_clean = '62' + phone_clean
            elif not phone_clean.startswith('62'):
                phone_clean = '62' + phone_clean
            
            # Konversi ke format lokal 08XXXXXXXXXX untuk tampilan
            local_number = '0' + phone_clean[2:]   # 628xxx → 08xxx
            
            # Username dari 10 digit terakhir (unik & aman untuk DB)
            short_number = phone_clean[-10:]
            username = f"wa_{short_number}"
            
            # Cek apakah user sudah ada
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{short_number}@wa.user",
                    'first_name': local_number,     # tampil "081234567890"
                    'last_name': ''
                }
            )
            
            if created:
                user.set_unusable_password()
                user.save()
            else:
                # Update first_name ke format lokal jika belum
                if not user.first_name.startswith('0'):
                    user.first_name = local_number
                    user.save(update_fields=['first_name'])
            
            # Simpan nomor lengkap ke profile (gunakan get_or_create untuk aman)
            from apps.core.models import Profile
            profile, profile_created = Profile.objects.get_or_create(user=user)
            profile.phone_number = raw_number
            profile.full_phone = phone_clean
            profile.save()
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return JsonResponse({'success': True, 'username': local_number})
            
        except Exception as e:
            print(f"Error in whatsapp_login: {e}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})