import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.vault import save_secret, get_secret

test_key = "test_openai_key"
test_val = "sk-123456789"

print(f"Saving {test_key}...")
save_secret(test_key, test_val)

print(f"Retrieving {test_key}...")
retrieved = get_secret(test_key)

if retrieved == test_val:
    print("VAULT SUCCESS: Secret encrypted and decrypted correctly.")
else:
    print(f"VAULT FAILURE: Expected {test_val}, got {retrieved}")
