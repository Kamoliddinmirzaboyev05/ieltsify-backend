"""
IELTSify Seed Data — Spetsifikatsiyaga mos tariflar, coin paketlar va AI xizmat narxlari.
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from subscriptions.models import SubscriptionPlan, CoinPack, CoinServiceCost

# ============================================================
# TARIFLAR
# ============================================================
print("=== Tariflar ===")

plans_data = [
    {
        'code': 'free',
        'name': 'Free',
        'description': 'Bepul boshlang\'ich tarif',
        'price_uzs': 0,
        'duration_days': 36500,  # cheksiz
        'included_coins': 0,
        'writing_ai_limit': 1,  # haftasiga
        'speaking_ai_limit': 1,  # haftasiga
        'daily_reading_limit': 1,
        'daily_listening_limit': 1,
        'daily_writing_ai_limit': 1,
        'daily_speaking_ai_limit': 1,
        'is_unlimited_reading': False,
        'is_unlimited_listening': False,
        'is_unlimited_vocab': False,
        'has_weekly_plan': False,
        'has_advanced_analytics': False,
        'has_smart_article': False,
        'daily_vocab_limit': 10,
        'sort_order': 0,
    },
    {
        'code': 'weekly',
        'name': 'IELTSify Weekly',
        'description': 'Haftalik premium tarif — qisqa muddatli tayyorgarlik uchun',
        'price_uzs': 12900,
        'launch_price_uzs': 9900,
        'is_launch_price_active': True,
        'duration_days': 7,
        'included_coins': 20,
        'writing_ai_limit': 5,
        'speaking_ai_limit': 5,
        'daily_reading_limit': 15,
        'daily_listening_limit': 15,
        'daily_writing_ai_limit': 5,
        'daily_speaking_ai_limit': 5,
        'is_unlimited_reading': True,
        'is_unlimited_listening': True,
        'is_unlimited_vocab': True,
        'has_weekly_plan': True,
        'has_advanced_analytics': True,
        'has_smart_article': True,
        'daily_vocab_limit': None,
        'sort_order': 1,
    },
    {
        'code': 'monthly',
        'name': 'IELTSify Monthly',
        'description': 'Oylik premium tarif — jiddiy tayyorgarlik uchun eng yaxshi tanlov',
        'price_uzs': 34900,
        'launch_price_uzs': 29900,
        'is_launch_price_active': True,
        'duration_days': 30,
        'included_coins': 70,
        'writing_ai_limit': 20,
        'speaking_ai_limit': 20,
        'daily_reading_limit': 15,
        'daily_listening_limit': 15,
        'daily_writing_ai_limit': 5,
        'daily_speaking_ai_limit': 5,
        'is_unlimited_reading': True,
        'is_unlimited_listening': True,
        'is_unlimited_vocab': True,
        'has_weekly_plan': True,
        'has_advanced_analytics': True,
        'has_smart_article': True,
        'daily_vocab_limit': None,
        'badge': 'Tavsiya etiladi',
        'sort_order': 2,
    },
]

for plan_data in plans_data:
    plan, created = SubscriptionPlan.objects.update_or_create(
        code=plan_data['code'],
        defaults=plan_data,
    )
    status = "CREATED" if created else "UPDATED"
    print(f"  {status}: {plan.name} — {plan.effective_price} UZS")

# ============================================================
# COIN PAKETLAR
# ============================================================
print("\n=== Coin Paketlar ===")

packs_data = [
    {'name': '50 Coin', 'coins': 50, 'price_uzs': 7900},
    {'name': '150 Coin', 'coins': 150, 'price_uzs': 17900},
    {'name': '500 Coin', 'coins': 500, 'price_uzs': 44900},
]

# Eski paketlarni o'chirish
CoinPack.objects.all().delete()
for pack_data in packs_data:
    pack = CoinPack.objects.create(**pack_data)
    print(f"  CREATED: {pack.name} — {pack.price_uzs} UZS")

# ============================================================
# AI XIZMAT NARXLARI
# ============================================================
print("\n=== AI Xizmat Narxlari ===")

services_data = [
    {'service_code': 'writing_task1', 'name': 'Writing Task 1 AI tahlili', 'cost_coins': 8},
    {'service_code': 'writing_task2', 'name': 'Writing Task 2 AI tahlili', 'cost_coins': 10},
    {'service_code': 'speaking_part1', 'name': 'Speaking Part 1 AI tahlili', 'cost_coins': 4},
    {'service_code': 'speaking_part2', 'name': 'Speaking Part 2 AI tahlili', 'cost_coins': 6},
    {'service_code': 'speaking_part3', 'name': 'Speaking Part 3 AI tahlili', 'cost_coins': 6},
    {'service_code': 'speaking_full_mock', 'name': 'Full Speaking Mock tahlili', 'cost_coins': 12},
    {'service_code': 'full_mock_report', 'name': 'Full IELTS Mock Report', 'cost_coins': 15},
    {'service_code': 'ai_tutor', 'name': 'Kengaytirilgan AI Tutor javobi', 'cost_coins': 2},
]

for svc_data in services_data:
    svc, created = CoinServiceCost.objects.update_or_create(
        service_code=svc_data['service_code'],
        defaults=svc_data,
    )
    status = "CREATED" if created else "UPDATED"
    print(f"  {status}: {svc.name} → {svc.cost_coins} coin")

print("\n✅ Seed data muvaffaqiyatli yuklandi!")
