from password_manager import PasswordManager
from ui.pages import (
    start_page,
    main_menu_page,
    new_service_page,
    remove_service_page,
    get_password_page,
)


if __name__ == "__main__":
    password_manager: PasswordManager = start_page()
    while True:
        action = main_menu_page()
        if action == "exit":
            exit()
        elif action == "new":
            new_service_page(password_manager)
        elif action == "get":
            get_password_page(password_manager)
        else:
            remove_service_page(password_manager)
