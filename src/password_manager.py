import hashlib
import socket
import random
import string
import hmac
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2.low_level import hash_secret, Type
from storage import Storage
import config


class PasswordManager:
    def __init__(self):
        self._storage = Storage()
        self._pepper = socket.gethostname()
        self.hasher: PasswordHasher = PasswordHasher()

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

    def secure_hash(self, data: str) -> str:
        return self.hasher.hash(data)

    def password_exists(self, name: str) -> bool:
        return self._storage.read(f"{name}_password") is not None

    def set_password(self, password: str, name: str) -> None:
        if self.password_exists(name):
            raise ValueError(f"{name} password already exists".capitalize())

        if len(PasswordManager.validate_password(password)):
            raise ValueError("Password is too weak")

        hashed = self.secure_hash(password + self._pepper)
        self._storage.write(f"{name}_password", hashed)

    def check_password(self, password: str, name: str) -> bool:
        try:
            self.hasher.verify(self._storage.read(f"{name}_password"), password + self._pepper)
        except VerifyMismatchError:
            return False
        
        if self.hasher.check_needs_rehash(self._storage.read(f"{name}_password")):
            self._storage.write(f"{name}_password", self.secure_hash(password + self._pepper))

        return True
    
    def service_registered(self, service_name: str) -> bool:
        services = self._storage.read("services")
        return bool(services and service_name in services)

    def register_new_service(self, ms_pass: str, service_name: str) -> (bool, str):
        """
        returns 'True/False' status and string error message (empty if successful)
        """

        if not self.check_password(ms_pass, config.MASTER_PW_NAME):
            return False, "wrong master password"
        
        if self.service_registered(service_name):
            return False, "this service is already registered"

        services = self._storage.read("services")
        if not services:
            services = []
        services.append(service_name)
        self._storage.write("services", list(set(services)))
        return True, "success"
    
    def get_available_services(self) -> list[str]:
        services = self._storage.read("services")
        return services or []
    
    def remove_service(self, service_name) -> None:
        if not self.service_registered(service_name):
            return
        
        services = self.get_available_services()
        services.remove(service_name)
        self._storage.write("services", services)
        

    def get_password_for_service(self, ms_pass: str, service_name: str) -> (str, str):
        """
        returns generated password and string error message (empty if successful)
        """

        if not self.check_password(ms_pass, config.MASTER_PW_NAME):
            return "", "wrong master password"

        if service_name not in self._storage.read("services"):
            return "", f"service '{service_name}' was not registered"

        seed = hash_secret(
            bytes(ms_pass + service_name, "utf-8"), 
            bytes(self._pepper, "utf-8"),
            time_cost=1, memory_cost=8, parallelism=1, hash_len=64, type=Type.ID
        )
        
        service_password = seed.decode("utf-8")[-16:].capitalize()

        return service_password, "success"
