import argon2.profiles as profiles
from questionary import Style

STORAGE_FILENAME = "storage.json"
APP_KEY = "app"
SALT_KEY = "salt"
SERVICES_KEY = "services"
STORAGE_SALT_KEY = "storage_salt"
STORAGE_DATA_KEY = "storage_data"
SALT_LENGTH = 32
PASSWORD_LENGTH = 24
HASHER_PARAMS = profiles.RFC_9106_HIGH_MEMORY
QUESTIONARY_STYLE = Style(
    [
        ("qmark", "fg:#7aa2f7 bold"),  # token in front of the question
        ("question", "bold"),  # question text
        ("pointer", "fg:#90d05a bold"),  # pointer used in select and checkbox prompts
        (
            "highlighted",
            "fg:#7aa2f7 bold",
        ),  # pointed-at choice in select and checkbox prompts
    ]
)
