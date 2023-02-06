from password_manager import PasswordManager
import ui.interface as interface
import config


def start_page(pw_manager: PasswordManager) -> None:
    interface.page_header()

    if not pw_manager.password_exists(config.APP_PW_NAME):
        pw_manager.set_password(interface.input_app_password(), config.APP_PW_NAME)
    else:
        interface.login(pw_manager)

    if not pw_manager.password_exists(config.MASTER_PW_NAME):
        pw_manager.set_password(
            interface.input_master_password(pw_manager),
            config.MASTER_PW_NAME,
        )


def main_menu_page() -> str:
    interface.page_header()
    return interface.select_action()


def new_service_page(pw_manager: PasswordManager) -> None:
    interface.page_header()
    ms_password = interface.verify_master_password(pw_manager)
    service_name = interface.input_new_service_name(pw_manager)
    status, problem = pw_manager.register_new_service(ms_password, service_name)
    if status:
        interface.service_registration_success(service_name)
        interface.show_service_password(pw_manager, ms_password, service_name)
    else:
        interface.print_problem(problem)

    interface.go_back_input()


def get_password_page(pw_manager: PasswordManager) -> None:
    interface.page_header()
    ms_password = interface.verify_master_password(pw_manager)
    service_name = interface.select_service(pw_manager)
    interface.show_service_password(pw_manager, ms_password, service_name)
    interface.go_back_input()


def remove_service_page(pw_manager: PasswordManager) -> None:
    interface.page_header()
    service_name = interface.select_service(pw_manager)
    pw_manager.remove_service(service_name)
    interface.service_removal_success(service_name)
    interface.go_back_input()
