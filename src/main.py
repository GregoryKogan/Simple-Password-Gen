from password_manager import PasswordManager
import config
from ui.pages import *


if __name__ == "__main__":
    pw_manager = PasswordManager()

    start_page(pw_manager)
    while True:
        action = main_menu_page()
        if action == "exit":
            exit()
        elif action == "new":
            new_service_page(pw_manager)
        elif action == "get":
            get_password_page(pw_manager)
        else:
            remove_service_page(pw_manager)
