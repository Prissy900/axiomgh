"""
AxiomGH — Client Onboarding Script
====================================
Run with: python onboard_client.py

This script creates a new institution and user account for a paying client.
Run it from C:\axiomgh with venv activated.
"""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'axiomgh.settings')
django.setup()

from core.models import Institution, User

print("\n" + "="*55)
print("  AxiomGH — Client Onboarding")
print("="*55)

# ── INSTITUTION DETAILS ───────────────────────────────────────────────────────
print("\n📋 INSTITUTION DETAILS\n")

name = input("Institution name (e.g. Absa Bank Ghana): ").strip()
if not name:
    print("❌ Institution name is required."); sys.exit(1)

print("\nInstitution type options:")
types = [
    ("commercial_bank",    "Commercial Bank"),
    ("fintech",            "Fintech"),
    ("payment_processor",  "Payment Processor"),
    ("savings_bank",       "Savings & Loans"),
    ("microfinance",       "Microfinance Institution"),
    ("credit_bureau",      "Credit Reference Bureau"),
    ("forex_bureau",       "Foreign Exchange Bureau"),
    ("insurance",          "Insurance Company"),
    ("development_finance","Development Finance Institution"),
]
for i, (_, label) in enumerate(types, 1):
    print(f"  {i}. {label}")

type_choice = input("\nEnter number (default 1): ").strip() or "1"
try:
    institution_type = types[int(type_choice) - 1][0]
    institution_type_label = types[int(type_choice) - 1][1]
except (ValueError, IndexError):
    institution_type = "commercial_bank"
    institution_type_label = "Commercial Bank"

license_number = input("BoG License number (e.g. BOG-2026-001): ").strip()
address = input("Institution address (optional): ").strip()
website = input("Website (optional, e.g. https://example.com): ").strip()

print("\nTier options:")
tiers = [("tier1", "Tier 1 — Large institution (full CISD requirements)"),
         ("tier2", "Tier 2 — Medium institution"),
         ("tier3", "Tier 3 — Small institution (proportional requirements)")]
for i, (_, label) in enumerate(tiers, 1):
    print(f"  {i}. {label}")
tier_choice = input("Enter number (default 1): ").strip() or "1"
try:
    tier = tiers[int(tier_choice) - 1][0]
except (ValueError, IndexError):
    tier = "tier1"

# ── USER DETAILS ──────────────────────────────────────────────────────────────
print("\n👤 PRIMARY USER (CISO / COMPLIANCE OFFICER)\n")

first_name = input("First name: ").strip()
last_name = input("Last name: ").strip()
email = input("Email address: ").strip().lower()
if not email or "@" not in email:
    print("❌ Valid email is required."); sys.exit(1)

print("\nUser role options:")
roles = [("ciso", "CISO — Chief Information Security Officer"),
         ("compliance", "Compliance Officer"),
         ("admin", "Platform Admin"),
         ("auditor", "Internal Auditor")]
for i, (_, label) in enumerate(roles, 1):
    print(f"  {i}. {label}")
role_choice = input("Enter number (default 1): ").strip() or "1"
try:
    role = roles[int(role_choice) - 1][0]
except (ValueError, IndexError):
    role = "ciso"

password = input("Temporary password (min 8 chars, default: AxiomGH2026!): ").strip() or "AxiomGH2026!"
if len(password) < 8:
    print("❌ Password must be at least 8 characters."); sys.exit(1)

# ── CONFIRM ───────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  CONFIRM CLIENT DETAILS")
print("="*55)
print(f"  Institution:   {name}")
print(f"  Type:          {institution_type_label}")
print(f"  License:       {license_number or 'Not provided'}")
print(f"  Tier:          {tier.upper()}")
print(f"  User:          {first_name} {last_name}")
print(f"  Email:         {email}")
print(f"  Role:          {role.upper()}")
print(f"  Password:      {password}")
print("="*55)

confirm = input("\nCreate this client? (y/n): ").strip().lower()
if confirm != "y":
    print("❌ Cancelled."); sys.exit(0)

# ── CREATE ────────────────────────────────────────────────────────────────────
print("\n⏳ Creating client account...")

# Check for existing institution
if Institution.objects.filter(name__iexact=name).exists():
    print(f"⚠️  Institution '{name}' already exists.")
    overwrite = input("Continue anyway and create a new entry? (y/n): ").strip().lower()
    if overwrite != "y":
        print("❌ Cancelled."); sys.exit(0)

# Check for existing email
if User.objects.filter(email=email).exists():
    print(f"❌ User with email '{email}' already exists. Use a different email."); sys.exit(1)

# Create institution
institution = Institution.objects.create(
    name=name,
    institution_type=institution_type,
    license_number=license_number,
    tier=tier,
    address=address,
    website=website,
    is_active=True,
)

# Create user
user = User.objects.create_user(
    email=email,
    password=password,
    first_name=first_name,
    last_name=last_name,
    institution=institution,
    role=role,
    is_active=True,
)

# ── SUCCESS ───────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  ✅ CLIENT ONBOARDED SUCCESSFULLY")
print("="*55)
print(f"\n  Institution ID: {institution.id}")
print(f"  Institution:    {institution.name}")
print(f"  User ID:        {user.id}")
print(f"  Email:          {user.email}")
print(f"\n  LOGIN CREDENTIALS TO SHARE WITH CLIENT:")
print(f"  ─────────────────────────────────────")
print(f"  URL:      http://your-domain.com (or localhost:3000 for demo)")
print(f"  Email:    {email}")
print(f"  Password: {password}")
print(f"\n  ⚠️  Ask the client to change their password on first login.")
print("="*55 + "\n")
