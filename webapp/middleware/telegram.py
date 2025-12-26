import hmac
import hashlib
import json
import logging
from urllib.parse import parse_qsl, unquote
from typing import Optional

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


class TelegramWebAppAuth: 
    """Telegram Web App authentication handler."""
    
    def __init__(self, bot_token: str):
        """Initialize with bot token."""
        self.bot_token = bot_token
    
    def validate_init_data(self, init_data: str) -> Optional[dict]:
        """
        Validate Telegram Web App initData and extract user information.
        
        Args:
            init_data: Raw initData string from Telegram Web App SDK
            
        Returns:
            Dictionary with user data if valid, None if invalid
        """
        try:
            # Parse the init data
            parsed_data = dict(parse_qsl(init_data))
            
            # Extract hash and other data
            received_hash = parsed_data.pop('hash', None)
            if not received_hash:
                logger.warning("No hash found in init data")
                return None
            
            # Create data check string
            data_check_arr = []
            for key, value in sorted(parsed_data.items()):
                data_check_arr.append(f"{key}={value}")
            data_check_string = '\n'.join(data_check_arr)
            
            # Create secret key from bot token
            secret_key = hmac.new(
                b"WebAppData",
                self.bot_token.encode(),
                hashlib.sha256
            ).digest()
            
            # Calculate expected hash
            expected_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Verify hash
            if not hmac.compare_digest(received_hash, expected_hash):
                security_logger.warning("Invalid hash in init data")
                return None
            
            # Extract user data
            user_data_str = parsed_data.get('user')
            if not user_data_str:
                logger.warning("No user data found in init data")
                return None
            
            # Parse user JSON
            user_data = json.loads(unquote(user_data_str))
            
            # Validate required fields
            if 'id' not in user_data:
                logger.warning("No user ID found in user data")
                return None
            
            return {
                'telegram_id': user_data['id'],
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'language_code': user_data.get('language_code'),
                'is_premium': user_data.get('is_premium', False),
            }
            
        except Exception as e:
            logger.error(f"Error validating init data: {e}")
            return None
