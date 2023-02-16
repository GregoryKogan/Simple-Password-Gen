import config
from password_manager import PasswordManager
from storage import Storage
import ui.interface as interface


def start_page() -> PasswordManager:
    interface.page_header()
    return (
        interface.login()
        if Storage.exists(config.STORAGE_FILENAME)
        else PasswordManager(interface.input_app_password())
    )


def main_menu_page() -> str:
    interface.page_header()
    return interface.select_action()


def new_service_page(password_manager: PasswordManager) -> None:
    interface.page_header()
    service_name = None
    while not service_name or service_name in password_manager.services:
        if service_name in password_manager.services:
            interface.print_problem(
                f"Service '{service_name}' has already been registered"
            )
        service_name = interface.input_new_service_name()
        if service_name == "":
            return
    password_manager.add_service(service_name)
    interface.service_registration_success(service_name)
    interface.go_back_input()


def get_password_page(password_manager: PasswordManager) -> None:
    interface.page_header()
    if not len(password_manager.services):
        interface.no_services_message()
        interface.go_back_input()
        return

    master_password = None
    while not master_password or len(
        password_manager.validate_master(str(master_password))
    ):
        if master_password:
            for problem in password_manager.validate_master(str(master_password)):
                interface.print_problem(problem)
        master_password = interface.input_master_password()
    interface.success_message()
    service_name = interface.select_service(
        password_manager.services, "What service do you want to get the password for?"
    )
    if service_name == "Go back":
        return

    password = password_manager.generate_password(master_password, service_name)
    interface.show_service_password(password, service_name)

    interface.go_back_input()


def remove_service_page(password_manager: PasswordManager) -> None:
    interface.page_header()

    if not len(password_manager.services):
        interface.no_services_message()
        interface.go_back_input()
        return

    service_name = interface.select_service(
        password_manager.services, "Which service do you want to remove?"
    )
    if service_name == "Go back":
        return
    password_manager.remove_service(service_name)
    interface.service_removal_success(service_name)
    interface.go_back_input()
