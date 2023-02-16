import questionary
from termcolor import colored
import os
import config
from password_manager import PasswordManager


def get_page_header() -> str:
    return colored(
        """
██████   █████  ███████ ███████  ██████  ███████ ███    ██ 
██   ██ ██   ██ ██      ██      ██       ██      ████   ██ 
██████  ███████ ███████ ███████ ██   ███ █████   ██ ██  ██ 
██      ██   ██      ██      ██ ██    ██ ██      ██  ██ ██ 
██      ██   ██ ███████ ███████  ██████  ███████ ██   ████ 
""",
        "green",
    )


def page_header() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(get_page_header())


def print_problem(problem: str) -> None:
    print(colored(problem, "red"))


def input_app_password() -> str:
    password = ""
    while len(PasswordManager.validate_password(password)):
        password = questionary.password("Set app password: ").ask()
        for problem in PasswordManager.validate_password(password):
            print_problem(problem)

    success_message()
    return password


def input_master_password() -> str:
    return questionary.password("Master password: ").ask()


def login() -> PasswordManager:
    password_manager = None
    while password_manager is None:
        password = questionary.password("Enter the app password to log in: ").ask()
        problems = PasswordManager.validate_password(password)
        if len(problems):
            for problem in problems:
                print_problem(problem)
            continue

        try:
            password_manager = PasswordManager(password)
        except ValueError:
            password_manager = None
            print_problem("Wrong app password")
            continue

    success_message()
    return password_manager


def select_action() -> str:
    options = [
        "Get a password for registered service",
        "Register a new service",
        "Remove service",
        "Exit",
    ]
    option = questionary.select(
        "What do you want to do?", options, style=config.QUESTIONARY_STYLE
    ).ask()
    status_lookup = {
        "Exit": "exit",
        "Register a new service": "new",
        "Get a password for registered service": "get",
        "Remove service": "remove",
    }
    return status_lookup[option]


def input_new_service_name() -> str:
    return questionary.text(
        "What is the name of the service",
        style=config.QUESTIONARY_STYLE,
        instruction="(Leave blank to go back)\n>> ",
    ).ask()


def service_registration_success(service_name: str) -> None:
    print()
    print(
        colored("Service", "green"),
        colored(f"'{service_name}'", "blue"),
        colored("was registered successfully!", "green"),
    )


def service_removal_success(service_name: str) -> None:
    print()
    print(
        colored("Service", "green"),
        colored(f"'{service_name}'", "blue"),
        colored("was removed", "green"),
    )


def success_message() -> None:
    print(colored("Success!", "green"))


def show_service_password(password: str, service_name: str) -> None:
    print()
    print(
        colored("Your", "green"),
        colored(f"'{service_name}'", "blue"),
        colored("password is:", "green"),
        colored(password, "yellow", attrs=["bold"]),
    )


def go_back_input() -> None:
    print()
    input(colored("Press enter to go back", "cyan"))


def select_service(services: list[str], question: str) -> str:
    return questionary.select(
        question,
        services + ["Go back"],
        style=config.QUESTIONARY_STYLE,
    ).ask()


def no_services_message() -> None:
    print(colored("You have no registered services yet", "green"))


def mnemonic_message() -> None:
    print()
    print("This is your mnemonic picture")
    print("If it changes, it will mean that you entered the password incorrectly")
