import hashlib
import socket
import random
import string
import hmac
from storage import Storage
import config


class PasswordManager:
    def __init__(self):
        self._storage = Storage()
        self._pepper = socket.gethostname()

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        letters = string.ascii_letters + string.digits
        return "".join(random.choice(letters) for _ in range(length))

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

    @staticmethod
    def secure_hash(data: str) -> str:
        return hashlib.sha3_512(bytes(data, "utf-8")).hexdigest()

    def password_exists(self, name: str) -> bool:
        return self._storage.read(f"{name}_password") is not None

    def set_password(self, password: str, name: str) -> None:
        if self.password_exists(name):
            raise ValueError(f"{name} password already exists".capitalize())

        if len(PasswordManager.validate_password(password)):
            raise ValueError("Password is too weak")

        salt = PasswordManager.generate_salt()
        hashed = PasswordManager.secure_hash(password + salt + self._pepper)
        self._storage.write(f"{name}_password", f"{hashed}${salt}")

    def get_salt(self, name: str) -> str:
        if not self.password_exists(name):
            raise ValueError(f"{name} password is not set".capitalize())
        return self._storage.read(f"{name}_password").split("$")[1]

    def check_password(self, password: str, name: str) -> bool:
        salt = self.get_salt(name)
        hashed = PasswordManager.secure_hash(password + salt + self._pepper)
        return hmac.compare_digest(
            self._storage.read(f"{name}_password"), f"{hashed}${salt}"
        )
    
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

        service_password = PasswordManager.secure_hash(
            ms_pass + self.get_salt(config.MASTER_PW_NAME) + self._pepper + service_name
        )[:32].capitalize()

        return service_password, "success"
