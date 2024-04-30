import inspect
import json
import os
import sys
import time
import logging

logger = logging.getLogger("gv")
# The KEYS tuple serves as a hardcoded verification of config.json integrity. Whenever a change to json is being done,
# it is required that the corresponding key is put into KEYS
KEYS = ("channel_id", "page", "log_level", "log_filename")
commands_json = "config/commands.json"
config_json = "config/config.json"
discord_token = "config/token.json"
tournaments_json = "storage/tournaments.json"


def get_current_function_name():
    frm = inspect.stack()[1]
    return inspect.getmodule(frm[0])


def _check_commands_json_integrity() -> bool:
    print(f"Performing {commands_json} integrity check...")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{commands_json}"):
        print(f"File {commands_json} does not exists! The application will now exit.")
        return False
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{commands_json}", "r"):
            if os.path.getsize(f"{os.path.realpath(os.path.dirname(__file__))}/{commands_json}") <= 2:
                print(f"{commands_json} file is empty! The application will now exit.")
                return False
            else:
                print(f"{commands_json} integrity check passed.")
                return True


def _check_config_json_integrity() -> bool:
    print(f"Performing {config_json} integrity check...")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}"):
        print(f"File {config_json} does not exists! The application will now exit.")
        return False
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}", "r") as file:
            if os.path.getsize(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}") <= 2:
                print(f"{config_json} file is empty! The application will now exit.")
                return False
            config = json.load(file)
            if all(key in config for key in KEYS):
                print(f"{config_json} integrity check passed.")
                return True
            else:
                print(f"{config_json} doesn't contain required dictionary keys! The application will now exit.")
                return False


def _write_to_config(key, value) -> None:
    logger.info(f"Attempting to update key: {key} with value: {value} in {config_json}.")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}"):
        sys.exit(f"{config_json} not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}", "r+") as file:
            config = json.load(file)
            if key in config:
                config[key] = value
                file.seek(0)
                json.dump(config, file)
                file.truncate()
                file.close()
            else:
                logger.warning(f"The key: {key} doesn't exist in {config_json}. No update will be done.")
                file.close()
                return
        logger.info(f"Key: {key} updated to value: {value}")


def check_json_integrity() -> (str, bool):
    print("Starting json files integrity checks...")
    commands_check = _check_commands_json_integrity()
    config_check = _check_config_json_integrity()
    return (f"{commands_json} file integrity check: {str(commands_check)}, {config_json} file integrity check: "
            f"{str(config_check)}", commands_check and config_check)


def get_config_from_json() -> dict:
    print(f"Getting configuration from {config_json} started.")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}"):
        logger.warning(f"get_config_from_json stopped with an error: {config_json} not found!"
                       f"Please add it and try again. Application will now exit.")
        sys.exit("{config_json} not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{config_json}", "r") as file:
            logger.info("{config_json} exists. Loading the configuration into the application.")
            config = json.load(file)
            file.close()
            logger.info("Configuration loaded successfully.")
            return config


def get_config_parameter(key):
    config = get_config_from_json()
    if key in config:
        return config[key]
    else:
        raise ValueError("Requested key is not present in the configuration file!")


def get_discord_token():
    print(f"Getting discord token from {discord_token} started.")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{discord_token}"):
        logger.warning(f"get_config_from_json stopped with an error: {discord_token} not found!"
                       f"Please add it and try again. Application will now exit.")
        sys.exit("{discord_token} not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{discord_token}", "r") as file:
            print(f"{discord_token} exists. Loading the discord token.")
            config = json.load(file)
            if "token" in config:
                file.close()
                print("Discord token retrieved successfully.")
                return config["token"]
            else:
                file.close()
                raise ValueError(f"Discord token is not present in {discord_token}!")


def get_supported_commands() -> str:
    logger.debug(f"Getting the list of supported commands from {commands_json} file.")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{commands_json}"):
        logger.error(f"{commands_json} not found! Please add it and try again.")
        sys.exit(f"{commands_json} not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{commands_json}", "r") as file:
            commands = json.load(file)
            return_string = "Hello! I'm a GloriaVictis bot. Currently I recognize the following commands:\r"
            for desc, command in commands.items():
                return_string = return_string + "**" + desc + "** - " + "*" + command + "*" + "\r"
            file.close()
            logger.debug(f"Returning the supported command list:\r{return_string}")
            return return_string


def get_tournaments() -> dict:
    logger.log(5, f"Getting the tournament list from {tournaments_json} file.")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{tournaments_json}"):
        logger.error(f"{tournaments_json} not found! Please add it and try again.")
        sys.exit(f"{tournaments_json} not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{tournaments_json}", "r") as file:
            if os.path.getsize(f"{os.path.realpath(os.path.dirname(__file__))}/{tournaments_json}") <= 2:
                return {}
            tournaments = json.load(file)
            file.close()
            if type(tournaments) is dict:
                return tournaments
            else:
                logger.debug(f"{tournaments_json} appears to be empty, returning empty dictionary.")
                return {}


def set_channels(channel_id) -> None:
    logger.info(f"Setting the receiving channel to id: {channel_id}")
    try:
        id_int = int(channel_id)
    except ValueError:
        logger.warning(f"The channel id {channel_id} is not a proper channel id value (int). Operation aborted.")
        raise ValueError(f"The channel id {channel_id} is not a proper channel id value (int). Operation aborted.")
    _write_to_config("channel_id", id_int)


def write_tournaments(tournaments) -> None:
    logger.debug(f"Writing the tournament list to {tournaments_json}")
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/tournaments.json"):
        sys.exit(f"{tournaments_json} not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{tournaments_json}", "w") as file:
            json.dump(tournaments, file)
            time.sleep(1)
            file.close()
