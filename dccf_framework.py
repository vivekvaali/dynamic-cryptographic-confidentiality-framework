
import os
import json
import base64
import secrets
import time
from pathlib import Path
from datetime import datetime, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DCCF:
    KEY_SIZE = 128
    NONCE_SIZE = 12

    def __init__(self, key_dir="/content/dccf_keys"):
        self.key_dir = Path(key_dir)
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.logs = []
        self.tenants = {}
        self._load_tenants()

    def _log(self, action, tenant, status):
        self.logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "tenant": tenant,
            "status": status
        })

    def _validate_tenant(self, tenant):
        if not tenant or not tenant.replace("_", "").isalnum():
            raise ValueError("Invalid tenant name.")

    def _tenant_file(self, tenant):
        self._validate_tenant(tenant)
        return self.key_dir / f"{tenant}.json"

    def _save_tenant(self, tenant):
        path = self._tenant_file(tenant)
        temp_path = path.with_suffix(".tmp")

        with open(temp_path, "w") as file:
            json.dump(self.tenants[tenant], file)

        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)

    def _load_tenants(self):
        for path in self.key_dir.glob("*.json"):
            try:
                with open(path, "r") as file:
                    record = json.load(file)

                tenant = path.stem
                self._validate_tenant(tenant)

                for key_record in record["keys"].values():
                    key = base64.b64decode(key_record["key"])
                    if len(key) != 16:
                        raise ValueError("Invalid AES-128 key length.")

                if record["current_key_id"] not in record["keys"]:
                    raise ValueError("Current key ID is missing.")

                self.tenants[tenant] = record

            except Exception:
                print(f"Warning: Could not load tenant key file: {path.name}")

    def add_tenant(self, tenant):
        self._validate_tenant(tenant)

        if tenant in self.tenants:
            return False

        key_id = secrets.token_hex(8)
        key = AESGCM.generate_key(bit_length=self.KEY_SIZE)

        self.tenants[tenant] = {
            "current_key_id": key_id,
            "keys": {
                key_id: {
                    "key": base64.b64encode(key).decode("utf-8"),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }

        self._save_tenant(tenant)
        self._log("Tenant Registration", tenant, "SUCCESS")
        return True

    def encrypt(self, tenant, data):
        if tenant not in self.tenants:
            raise ValueError("Tenant is not registered.")

        key_id = self.tenants[tenant]["current_key_id"]
        key = base64.b64decode(
            self.tenants[tenant]["keys"][key_id]["key"]
        )

        nonce = secrets.token_bytes(self.NONCE_SIZE)
        aad = f"{tenant}:{key_id}".encode("utf-8")

        ciphertext = AESGCM(key).encrypt(nonce, data, aad)
        token = base64.b64encode(nonce + ciphertext).decode("utf-8")

        self._log("File Encryption", tenant, "SUCCESS")

        return {
            "tenant": tenant,
            "kid": key_id,
            "token": token
        }

    def decrypt(self, tenant, encrypted_record):
        if tenant not in self.tenants:
            raise ValueError("Tenant is not registered.")

        if encrypted_record["tenant"] != tenant:
            raise ValueError("Tenant mismatch.")

        key_id = encrypted_record["kid"]

        if key_id not in self.tenants[tenant]["keys"]:
            raise ValueError("Encryption key not found.")

        key = base64.b64decode(
            self.tenants[tenant]["keys"][key_id]["key"]
        )

        raw = base64.b64decode(encrypted_record["token"])

        if len(raw) <= self.NONCE_SIZE:
            raise ValueError("Invalid encrypted file.")

        nonce = raw[:self.NONCE_SIZE]
        ciphertext = raw[self.NONCE_SIZE:]
        aad = f"{tenant}:{key_id}".encode("utf-8")

        plaintext = AESGCM(key).decrypt(nonce, ciphertext, aad)

        self._log("File Decryption", tenant, "SUCCESS")
        return plaintext

    def rotate_key(self, tenant):
        if tenant not in self.tenants:
            raise ValueError("Tenant is not registered.")

        key_id = secrets.token_hex(8)
        key = AESGCM.generate_key(bit_length=self.KEY_SIZE)

        self.tenants[tenant]["keys"][key_id] = {
            "key": base64.b64encode(key).decode("utf-8"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.tenants[tenant]["current_key_id"] = key_id
        self._save_tenant(tenant)
        self._log("Key Rotation", tenant, "SUCCESS")

        return key_id

    def share_data(self, source_tenant, target_tenant, encrypted_record):
        plaintext = self.decrypt(source_tenant, encrypted_record)
        shared_record = self.encrypt(target_tenant, plaintext)

        self._log(
            f"Secure Sharing from {source_tenant}",
            target_tenant,
            "SUCCESS"
        )

        return shared_record
