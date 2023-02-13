import string
from argon2 import PasswordHasher
from argon2.low_level import hash_secret, Type
from hashlib import sha3_512, sha3_224
from storage import Storage
import os
from base64 import b64encode
from aes_cipher import AESCipher
import config


class PasswordManager:
    def __init__(self, app_password):
        if len(PasswordManager.validate_password(app_password)):
            raise ValueError("Invalid app password")

        self._storage: Storage = Storage(app_password)
        self._salt: str = self.init_salt()

    @staticmethod
    def combine_strings(strings: list[str]) -> str:
        return "".join(f"{len(s)}:{s}" for s in strings)

    @staticmethod
    def convert_to_password(seed: str) -> str:
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

    def hash(self, data: str, stable: bool = False) -> str:
        hasher = PasswordHasher()
        return (
            hash_secret(
                bytes(data, "utf-8"),
                bytes(self._salt, "utf-8"),
                time_cost=1,
                memory_cost=8,
                parallelism=1,
                hash_len=64,
                type=Type.ID,
            ).decode("utf-8")
            if stable
            else hasher.hash(PasswordManager.combine_strings([data, self._salt]))
        )

    def init_salt(self) -> str:
        if self._storage.stores_key(config.SALT_KEY):
            return str(self._storage.read(config.SALT_KEY))
        salt = b64encode(os.urandom(config.SALT_LENGTH)).decode("utf-8")
        self._storage.write(config.SALT_KEY, salt)
        return salt

    def init_pepper(self, master_password: str) -> None:
        if self._storage.stores_key(config.PEPPER_KEY):
            raise ValueError("Pepper already exists")

        pepper = b64encode(os.urandom(config.PEPPER_LENGTH)).decode("utf-8")
        key = self.hash(master_password, stable=True)
        self._storage.write(config.PEPPER_KEY, AESCipher.encrypt(key, pepper))

    def get_pepper(self, master_password: str) -> str:
        if not self._storage.stores_key(config.PEPPER_KEY):
            raise ValueError("Pepper does not exist")

        encrypted = str(self._storage.read(config.PEPPER_KEY))
        key = self.hash(master_password, stable=True)
        return AESCipher.decrypt(key, encrypted)

    def set_master(self, master_password: str) -> None:
        if len(PasswordManager.validate_password(master_password)):
            raise ValueError("Invalid password")

        self.init_pepper(master_password)

    def generate_password(self, master_password: str, service_name: str) -> str:
        pepper = self.get_pepper(master_password)
        return PasswordManager.convert_to_password(
            self.hash(
                PasswordManager.combine_strings(
                    [master_password, pepper, service_name]
                ),
                stable=True,
            )
        )

    def add_service(self, master_password: str, service_name: str) -> None:
        if service_name in self.get_services(master_password):
            return

        services = []
        if self._storage.stores_key(config.SERVICES_KEY):
            services = self._storage.read(config.SERVICES_KEY)

        pepper = self.get_pepper(master_password)
        key = self.hash(
            PasswordManager.combine_strings([master_password, pepper]), stable=True
        )
        services.append(AESCipher.encrypt(key, service_name))

        self._storage.write(config.SERVICES_KEY, services)

    def remove_service(self, master_password: str, service_name: str) -> None:
        services = []
        if self._storage.stores_key(config.SERVICES_KEY):
            services = self._storage.read(config.SERVICES_KEY)

        pepper = self.get_pepper(master_password)
        key = self.hash(
            PasswordManager.combine_strings([master_password, pepper]), stable=True
        )
        services.remove(AESCipher.encrypt(key, service_name))

        self._storage.write(config.SERVICES_KEY, services)

    def get_services(self, master_password: str) -> list[str]:
        services = []
        if self._storage.stores_key(config.SERVICES_KEY):
            services = self._storage.read(config.SERVICES_KEY)

        if not len(services):
            return []

        pepper = self.get_pepper(master_password)
        key = self.hash(
            PasswordManager.combine_strings([master_password, pepper]), stable=True
        )

        return [AESCipher.decrypt(key, service) for service in services]
