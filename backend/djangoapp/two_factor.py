from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import pyotp
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def get_user_totp_device(user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    user = request.user
    device = get_user_totp_device(user)
    
    if not device:
        # Generate a random base32 key
        key = pyotp.random_base32()
        device = user.totpdevice_set.create(key=key, confirmed=False)
    
    # Create TOTP object
    totp = pyotp.TOTP(device.key)
    
    # Create provisioning URI
    provisioning_uri = totp.provisioning_uri(
        name=user.username,
        issuer_name='ft_transcendence'
    )
    
    # Generate QR code
    img = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgImage)
    stream = BytesIO()
    img.save(stream)
    qr_code = base64.b64encode(stream.getvalue()).decode()
    
    # Create otpauth URL manually to ensure correct format
    otpauth_url = f"otpauth://totp/ft_transcendence:{user.username}?secret={device.key}&issuer=ft_transcendence"
    
    return Response({
        'qr_code': qr_code,
        'secret_key': device.key,
        'config_url': otpauth_url
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    try:
        user = request.user
        token = request.data.get('token')
        
        if not token:
            return Response({'error': 'Token is required'}, status=400)
        
        logger.info(f"Verifying 2FA token for user {user.username}")
        device = get_user_totp_device(user)
        
        if not device:
            logger.warning(f"No 2FA device found for user {user.username}")
            return Response({'error': '2FA is not set up'}, status=400)
        
        # Ensure token is a string of 6 digits
        token = str(token).zfill(6)
        if not token.isdigit() or len(token) != 6:
            return Response({'error': 'Token must be 6 digits'}, status=400)
        
        # Create TOTP object with the same parameters
        totp = pyotp.TOTP(device.key)
        
        # Verify with both current and previous windows to account for time drift
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            if not device.confirmed:
                device.confirmed = True
                device.save()
                # Mettre à jour le champ has_2fa
                user.has_2fa = True
                user.save()
                logger.info(f"2FA confirmed for user {user.username}")
            return Response({'success': True, 'message': '2FA verification successful'})
        
        logger.warning(f"Invalid 2FA token attempt for user {user.username}")
        return Response({'error': 'Invalid token'}, status=400)
        
    except Exception as e:
        logger.error(f"Error in verify_2fa: {str(e)}")
        return Response({
            'error': 'An error occurred during verification',
            'detail': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    user = request.user
    devices = devices_for_user(user)
    
    for device in devices:
        device.delete()
    
    # Mettre à jour le champ has_2fa
    user.has_2fa = False
    user.save()
    
    return Response({'success': True, 'message': '2FA has been disabled'})
    
    return Response({'error': '2FA is not enabled'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    try:
        user = request.user
        device = get_user_totp_device(user)
        
        return Response({
            'enabled': user.has_2fa and device and device.confirmed,
            'is_configured': bool(device)
        })
    except Exception as e:
        logger.error(f"Error in get_2fa_status: {str(e)}")
        return Response({
            'error': 'An error occurred while checking 2FA status',
            'detail': str(e)
        }, status=500)

