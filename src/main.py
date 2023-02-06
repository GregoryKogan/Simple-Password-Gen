import hashlib
import socket
import random
import string
from termcolor import colored
import hmac


def greet_user() -> None:
    pass_gen_line = """
██████   █████  ███████ ███████  ██████  ███████ ███    ██ 
██   ██ ██   ██ ██      ██      ██       ██      ████   ██ 
██████  ███████ ███████ ███████ ██   ███ █████   ██ ██  ██ 
██      ██   ██      ██      ██ ██    ██ ██      ██  ██ ██ 
██      ██   ██ ███████ ███████  ██████  ███████ ██   ████ 
"""
    print(colored(pass_gen_line, "green"))


def gen_salt(length: int = 16) -> str:
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


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


def set_master_password() -> None:
    ms_pass = ""
    while len(validate_password(ms_pass)) > 0:
        ms_pass = input(colored("Set master password: ", "blue"))
        for problem in validate_password(ms_pass):
            print(colored(problem, "red"))

    pepper = socket.gethostname()
    salt = gen_salt()
    hashed = hashlib.sha3_512(bytes(ms_pass + salt + pepper, "utf-8")).hexdigest()

    record = f"{hashed}${salt}"
    with open("ms-pass.txt", "w") as f:
        print(record, file=f, end="")

    print(colored("Master password set!", "green"))


def get_password_record() -> str:
    if not master_password_exists():
        raise "Master password is not set"

    with open("ms-pass.txt", "r") as f:
        return f.readline()


def check_password(password):
    record = get_password_record()
    salt = record.split("$")[1]
    pepper = socket.gethostname()
    hashed = hashlib.sha3_512(bytes(password + salt + pepper, "utf-8")).hexdigest()
    my_record = f"{hashed}${salt}"

    return hmac.compare_digest(record, my_record)


def register_new_service(password: str, service_name: str) -> None:
    if not check_password(password):
        print(colored("Wrong master password!", "red"))
        return

    salt = get_password_record().split("$")[1]
    pepper = socket.gethostname()
    service_pass = (
        hashlib.sha3_512(bytes(password + salt + pepper + service_name, "utf-8"))
        .hexdigest()[:32]
        .capitalize()
    )

    with open("services.txt", "a") as f:
        print(service_name, file=f)

    print(f"Service '{service_name}' registered")
    print(f"Your password for {service_name}: {service_pass}")


def master_password_exists() -> bool:
    try:
        with open("ms-pass.txt", "r") as f:
            record = f.readline()
            return len(record) != 0
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    greet_user()
    if not master_password_exists():
        set_master_password()

    while True:
        p = input("Password: ")
        n = input("Service name: ")
        register_new_service(p, n)
