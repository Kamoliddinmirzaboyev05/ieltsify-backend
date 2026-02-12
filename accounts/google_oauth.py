"""
Google OAuth2 Service for Django DRF
Production-ready implementation with proper security and error handling
"""

import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
logger = logging.getLogger(__name__)


class GoogleOAuth2Service:
    """Production-ready Google OAuth2 service"""
    
    @staticmethod
    def verify_id_token(id_token_string):
        """
        Verify Google ID token with proper security checks
        
        Args:
            id_token_string (str): Google ID token from frontend
            
        Returns:
            dict: Token payload if valid, None if invalid
            
        Raises:
            ValueError: For invalid tokens
            Exception: For verification errors
        """
        try:
            # Verify token with Google's servers
            idinfo = id_token.verify_oauth2_token(
                id_token_string,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Additional security checks
            if not GoogleOAuth2Service._validate_token_payload(idinfo):
                logger.warning(f"Invalid token payload: {idinfo}")
                return None
                
            return idinfo
            
        except ValueError as e:
            logger.error(f"Invalid Google token: {str(e)}")
            raise ValueError("Invalid or expired Google token")
            
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise Exception("Token verification failed")
    
    @staticmethod
    def _validate_token_payload(payload):
        """
        Validate token payload for security
        
        Args:
            payload (dict): Decoded token payload
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required fields
        required_fields = ['sub', 'email', 'aud', 'iss', 'exp', 'iat']
        if not all(field in payload for field in required_fields):
            return False
        
        # Check audience (must match our CLIENT_ID)
        if payload.get('aud') != settings.GOOGLE_CLIENT_ID:
            return False
        
        # Check issuer (must be Google)
        valid_issuers = ['accounts.google.com', 'https://accounts.google.com']
        if payload.get('iss') not in valid_issuers:
            return False
        
        # Check email format
        email = payload.get('email')
        if not email or '@' not in email:
            return False
        
        return True
    
    @staticmethod
    def get_or_create_user(email, first_name='', last_name='', google_sub=''):
        """
        Get or create user from Google data
        
        Args:
            email (str): User email from Google
            first_name (str): User first name
            last_name (str): User last name
            google_sub (str): Google subject ID
            
        Returns:
            tuple: (user, created)
        """
        try:
            with transaction.atomic():
                # Try to get existing user
                user = User.objects.filter(email=email).first()
                
                if user:
                    # Update existing user with Google data if needed
                    if not user.first_name and first_name:
                        user.first_name = first_name
                    if not user.last_name and last_name:
                        user.last_name = last_name
                    user.save()
                    return user, False
                
                # Create new user
                username = email.split('@')[0]
                counter = 1
                
                # Ensure unique username
                while User.objects.filter(username=username).exists():
                    username = f"{email.split('@')[0]}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='user'
                )
                
                # Mark email as verified (from Google)
                if hasattr(user, 'userprofile'):
                    user.userprofile.email_verified = True
                    user.userprofile.save()
                
                logger.info(f"Created new user from Google OAuth: {email}")
                return user, True
                
        except Exception as e:
            logger.error(f"Error creating/getting user: {str(e)}")
            raise Exception("User creation failed")
    
    @staticmethod
    def generate_jwt_tokens(user):
        """
        Generate JWT tokens for user
        
        Args:
            user (User): Django user object
            
        Returns:
            dict: Access and refresh tokens with user info
        """
        try:
            refresh = RefreshToken.for_user(user)
            
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'email_verified': getattr(user.userprofile, 'email_verified', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise Exception("Token generation failed")
    
    @staticmethod
    def authenticate_google_user(id_token_string):
        """
        Complete Google OAuth authentication flow
        
        Args:
            id_token_string (str): Google ID token
            
        Returns:
            dict: Authentication result with tokens and user info
            
        Raises:
            ValueError: For invalid tokens
            Exception: For processing errors
        """
        try:
            # Step 1: Verify token
            token_payload = GoogleOAuth2Service.verify_id_token(id_token_string)
            if not token_payload:
                raise ValueError("Invalid token payload")
            
            # Step 2: Extract user data
            email = token_payload['email']
            first_name = token_payload.get('given_name', '')
            last_name = token_payload.get('family_name', '')
            google_sub = token_payload.get('sub', '')
            
            # Step 3: Get or create user
            user, created = GoogleOAuth2Service.get_or_create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                google_sub=google_sub
            )
            
            # Step 4: Generate tokens
            tokens = GoogleOAuth2Service.generate_jwt_tokens(user)
            
            # Step 5: Return result
            return {
                'success': True,
                'tokens': tokens,
                'user_created': created,
                'message': 'Login successful' if not created else 'Account created and logged in'
            }
            
        except ValueError as e:
            logger.warning(f"Google auth validation error: {str(e)}")
            return {
                'success': False,
                'error': 'invalid_token',
                'message': str(e)
            }
            
        except Exception as e:
            logger.error(f"Google auth error: {str(e)}")
            return {
                'success': False,
                'error': 'authentication_failed',
                'message': 'Authentication failed. Please try again.'
            }
