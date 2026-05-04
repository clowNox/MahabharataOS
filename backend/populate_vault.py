import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vault import save_secret

if len(sys.argv) < 3:
    print("Usage: python3 populate_vault.py <key_name> <secret_value>")
    sys.exit(1)

key = sys.argv[1]
val = sys.argv[2]

save_secret(key, val)
print(f"Successfully secured '{key}' in the Strategic Vault.")
