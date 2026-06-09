import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from subscriptions.models import SubscriptionPlan, CoinPack, CoinWallet

User = get_user_model()

# Create UserProfile for admin (if not exists via signal)
admin = User.objects.get(email='admin@ieltsify.com')
UserProfile.objects.get_or_create(user=admin)
CoinWallet.objects.get_or_create(user=admin, defaults={'balance': 1000})
print(f'Admin profile ready: {admin.email}')

# Create test user
if not User.objects.filter(email='test@ieltsify.com').exists():
    user = User.objects.create_user(
        username='testuser', email='test@ieltsify.com',
        password='test123', first_name='Test', last_name='User'
    )
    UserProfile.objects.get_or_create(user=user)
    CoinWallet.objects.get_or_create(user=user, defaults={'balance': 100})
    print('Test user created: test@ieltsify.com / test123')
else:
    user = User.objects.get(email='test@ieltsify.com')
    UserProfile.objects.get_or_create(user=user)
    CoinWallet.objects.get_or_create(user=user, defaults={'balance': 100})
    print('Test user already exists')

# Create subscription plans
if not SubscriptionPlan.objects.exists():
    SubscriptionPlan.objects.create(
        code='free', name='Free', price_uzs=0,
        duration_days=365, included_coins=0, daily_vocab_limit=10
    )
    SubscriptionPlan.objects.create(
        code='basic_weekly', name='Basic Weekly', price_uzs=19900,
        duration_days=7, included_coins=50
    )
    SubscriptionPlan.objects.create(
        code='basic_monthly', name='Basic Monthly', price_uzs=49900,
        duration_days=30, included_coins=200
    )
    print('Subscription plans created')
else:
    print('Subscription plans already exist')

# Create coin packs
if not CoinPack.objects.exists():
    CoinPack.objects.create(name='50 Coin', coins=50, price_uzs=9900)
    CoinPack.objects.create(name='150 Coin', coins=150, price_uzs=19900)
    CoinPack.objects.create(name='500 Coin', coins=500, price_uzs=49900)
    print('Coin packs created')
else:
    print('Coin packs already exist')

print('\n=== LOCAL SETUP COMPLETE ===')
print('Admin: admin@ieltsify.com / admin123')
print('User:  test@ieltsify.com / test123')
print('Backend: http://localhost:8000')
