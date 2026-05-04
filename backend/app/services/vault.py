import os
import json
from cryptography.fernet import Fernet
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
VAULT_PATH = BASE_DIR / "app" / "db" / "vault.enc"
KEY_PATH = BASE_DIR / "app" / "core" / "master.key"

def ensure_master_key():
    """Generates a master key if it doesn't exist."""
    if not KEY_PATH.exists():
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    with open(KEY_PATH, "rb") as f:
        return f.read()

def get_fernet():
    key = ensure_master_key()
    return Fernet(key)

def save_secret(key_name: str, secret_value: str):
    """Encrypts and saves a secret to the vault."""
    fernet = get_fernet()
    
    vault_data = {}
    if VAULT_PATH.exists():
        with open(VAULT_PATH, "rb") as f:
            encrypted_data = f.read()
            if encrypted_data:
                try:
                    decrypted_data = fernet.decrypt(encrypted_data)
                    vault_data = json.loads(decrypted_data)
                except:
                    vault_data = {}

    vault_data[key_name] = secret_value
    
    encrypted_vault = fernet.encrypt(json.dumps(vault_data).encode())
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VAULT_PATH, "wb") as f:
        f.write(encrypted_vault)

def get_secret(key_name: str) -> str:
    """Retrieves and decrypts a secret from the vault."""
    if not VAULT_PATH.exists():
        return None
        
    fernet = get_fernet()
    with open(VAULT_PATH, "rb") as f:
        encrypted_data = f.read()
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
            vault_data = json.loads(decrypted_data)
            return vault_data.get(key_name)
        except:
            return None

def get_all_secrets() -> dict:
    """Retrieves all secrets as a dict (e.g. for user_context)."""
    if not VAULT_PATH.exists():
        return {}
        
    fernet = get_fernet()
    with open(VAULT_PATH, "rb") as f:
        encrypted_data = f.read()
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except:
            return {}
