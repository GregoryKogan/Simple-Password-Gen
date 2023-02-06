from termcolor import colored
from simple_term_menu import TerminalMenu
import os
from password_manager import PasswordManager
import config


def page_header() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    pass_gen_line = """
██████   █████  ███████ ███████  ██████  ███████ ███    ██ 
██   ██ ██   ██ ██      ██      ██       ██      ████   ██ 
██████  ███████ ███████ ███████ ██   ███ █████   ██ ██  ██ 
██      ██   ██      ██      ██ ██    ██ ██      ██  ██ ██ 
██      ██   ██ ███████ ███████  ██████  ███████ ██   ████ 
"""
    print(colored(pass_gen_line, "green"))


def print_problem(problem: str) -> None:
    print(colored(problem.capitalize(), "red"))


def input_app_password() -> str:
    password = ""
    while len(PasswordManager.validate_password(password)) > 0:
        password = input(colored("Set app password: ", "blue"))
        for problem in PasswordManager.validate_password(password):
            print_problem(problem)

    return password


def input_master_password(pw_manager: PasswordManager) -> str:
    password = ""
    while len(
        PasswordManager.validate_password(password)
    ) > 0 or pw_manager.check_password(password, config.APP_PW_NAME):
        password = input(colored("Set master password: ", "blue"))
        for problem in PasswordManager.validate_password(password):
            print_problem(problem)
        if pw_manager.check_password(password, config.APP_PW_NAME):
            print_problem(
                "The master password must not be the same as the app password"
            )

    return password


def login(pw_manager: PasswordManager) -> None:
    password = ""
    while not pw_manager.check_password(password, config.APP_PW_NAME):
        password = input(colored("Enter the app password to log in: ", "blue"))
        if not pw_manager.check_password(password, config.APP_PW_NAME):
            print_problem("Invalid password")
    print(colored("Success!", "green"))


def select_action() -> str:
    options = [
        "Register a new service",
        "Get a password for registered service",
        "Remove service",
        "Exit",
    ]
    terminal_menu = TerminalMenu(options, menu_cursor_style=("fg_green", "bold"))
    menu_entry_index = terminal_menu.show()

    status_lookup = {
        "Exit": "exit",
        "Register a new service": "new",
        "Get a password for registered service": "get",
        "Remove service": "remove",
    }
    return status_lookup[options[menu_entry_index]]


def verify_master_password(pw_manager: PasswordManager) -> str:
    password = ""
    while not pw_manager.check_password(password, config.MASTER_PW_NAME):
        password = input(colored("Enter the master password: ", "blue"))
        if not pw_manager.check_password(password, config.MASTER_PW_NAME):
            print_problem("Invalid password")
    print(colored("Success!\n", "green"))
    return password


def input_new_service_name(pw_manager: PasswordManager) -> str:
    service_name = ""
    while not service_name or pw_manager.service_registered(service_name):
        service_name = input(colored("Enter service name: ", "blue"))
        if pw_manager.service_registered(service_name):
            print_problem("This service is already registered")
    return service_name


def service_registration_success(service_name: str) -> None:
    print(
        colored("Service", "green"),
        colored(f"'{service_name}'", 'blue'),
        colored("was registered successfully!", "green"),
    )


def service_removal_success(service_name: str) -> None:
    print(
        colored("Service", "green"),
        colored(f"'{service_name}'", 'blue'),
        colored("was removed", "green"),
    )


def show_service_password(
    pw_manager: PasswordManager, ms_pass: str, service_name: str
) -> None:
    password, status = pw_manager.get_password_for_service(ms_pass, service_name)
    if len(password):
        print()
        print(
            colored("Your", "green"),
            colored(f"'{service_name}'", 'blue'),
            colored("password is:", "green"),
            colored(password, "yellow"),
        )
    else:
        print_problem(status)


def go_back_input():
    print()
    input(colored("Press enter to go back", "cyan"))


def select_service(pw_manager: PasswordManager) -> str:
    services = pw_manager.get_available_services()
    terminal_menu = TerminalMenu(services, menu_cursor_style=("fg_green", "bold"))
    print(colored("Select a service", "blue"))
    menu_entry_index = terminal_menu.show()
    return services[menu_entry_index]
