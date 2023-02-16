import string
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2.low_level import hash_secret
from hashlib import sha3_512, sha3_224
from storage import Storage
import os
from base64 import b64encode
import config


class PasswordManager:
    def __init__(self, app_password: str):
        if len(PasswordManager.validate_password(app_password)):
            raise ValueError("Invalid app password")

        try:
            self._storage: Storage = Storage(app_password, config.STORAGE_FILENAME)
        except ValueError as e:
            raise ValueError("Wrong app password") from e

        self._salt: str = self._init_salt()
        self._storage.write(config.APP_KEY, self._hash(app_password, stable=False))

    @property
    def services(self) -> list[str]:
        return self._storage.read(config.SERVICES_KEY) or []

    @staticmethod
    def _combine_strings(strings: list[str]) -> str:
        return "".join(f"{len(s)}:{s}" for s in strings)

    @staticmethod
    def _convert_to_password(seed: str) -> str:
        # Hash the input hex string to produce a seed value
        seed_num = int(sha3_224(seed.encode()).hexdigest(), 16)

        hex_list = list(sha3_512(seed.encode()).hexdigest()[: config.PASSWORD_LENGTH])

        # Deterministically replace some bytes with characters from various character sets
        special_chars = "!$%&*+-?_"
        for i in range(len(hex_list)):
            if i % 5 == 0:
                hex_list[i] = string.ascii_lowercase[(seed_num // (i + 1)) % 26]
            elif i % 5 == 1:
                hex_list[i] = string.ascii_uppercase[(seed_num // (i + 1)) % 26]
            elif i % 5 == 2:
                hex_list[i] = string.digits[(seed_num // (i + 1)) % 10]
            elif i % 5 == 3:
                hex_list[i] = special_chars[(seed_num // (i + 1)) % len(special_chars)]

        return "".join(hex_list)

    def _init_salt(self) -> str:
        if self._storage.stores_key(config.SALT_KEY):
            return str(self._storage.read(config.SALT_KEY))
        salt = b64encode(os.urandom(config.SALT_LENGTH)).decode("utf-8")
        self._storage.write(config.SALT_KEY, salt)
        return salt

    def _hash(self, data: str, stable: bool = True) -> str:
        return (
            hash_secret(
                data.encode(),
                self._salt.encode(),
                time_cost=config.HASHER_PARAMS.time_cost,
                memory_cost=config.HASHER_PARAMS.memory_cost,
                parallelism=config.HASHER_PARAMS.parallelism,
                hash_len=config.HASHER_PARAMS.hash_len,
                type=config.HASHER_PARAMS.type,
            ).decode("utf-8")
            if stable
            else PasswordHasher.from_parameters(config.HASHER_PARAMS).hash(
                PasswordManager._combine_strings([data, self._salt])
            )
        )

    def _check_app_password(self, password: str) -> bool:
        hasher = PasswordHasher.from_parameters(config.HASHER_PARAMS)
        stored = str(self._storage.read(config.APP_KEY))
        try:
            hasher.verify(
                stored, PasswordManager._combine_strings([password, self._salt])
            )
        except VerifyMismatchError:
            return False

        if hasher.check_needs_rehash(stored):
            self._storage.write(config.APP_KEY, self._hash(password, stable=False))

        return True

    @staticmethod
    def validate_password(password: str) -> list[str]:
        problems = []
        if len(password) < 8:
            problems.append("Password must be at least 8 characters")
        if all(c not in string.ascii_lowercase for c in password) or all(
            c not in string.ascii_uppercase for c in password
        ):
            problems.append("Password must contain capital and lowercase letters")
        if all(c not in string.digits for c in password):
            problems.append("Password must contain digits")
        if all(c not in "$#@!*" for c in password):
            problems.append("Password must contain special characters: '$#@!*'")
        return problems

    def validate_master(self, master_password: str) -> list[str]:
        problems = []
        problems.extend(PasswordManager.validate_password(master_password))
        if self._check_app_password(master_password):
            problems.append("Master password must not match app password")
        return problems

    def generate_password(self, master_password: str, service_name: str) -> str:
        if len(self.validate_master(master_password)):
            raise ValueError("Invalid master password")

        if service_name not in self.services:
            raise ValueError(f"Service '{service_name}' does not exist")

        if not len(service_name):
            raise ValueError("Empty string can't represent a service")

        return PasswordManager._convert_to_password(
            self._hash(
                PasswordManager._combine_strings([master_password, service_name])
            )
        )

    def add_service(self, service_name: str) -> None:
        if not len(service_name):
            raise ValueError("Empty string can't represent a service")

        services = self.services
        if service_name not in services:
            services.append(service_name)
            self._storage.write(config.SERVICES_KEY, services)

    def remove_service(self, service_name: str) -> None:
        services = self.services
        if service_name in services:
            services.remove(service_name)
            self._storage.write(config.SERVICES_KEY, services)
