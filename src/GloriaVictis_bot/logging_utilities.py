import inspect
import logging
import os.path
from discordReadWrite import get_config_parameter

logger = logging.getLogger("gv")


def prepare_logger():
    log_path = get_config_parameter("log_filename")
    print(f"Log path successfully read from config.json: {log_path}")
    log_level = get_config_parameter("log_level")
    print(f"Log level successfully read from config.json: {log_level}")

    try:
        open(log_path, 'w')
    except (FileNotFoundError, PermissionError, OSError):
        print("Log file couldn't be opened or created! The logger will NOT be started!")
        return

    if log_level == "TRACE" and os.path.exists(log_path):
        try:
            logging.basicConfig(filename=log_path, filemode='w',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S', level=5)
            print(f"{log_path} will be cleared for new log.")
        except TypeError:
            print("Logger configuration failed! Please double check cofig.json with specification to make sure"
                  "proper log level is set. The logger will NOT be started!")
            print(TypeError)
            return
        print("Logging service successfully started. Switching over from console print to logging.")
        logger.info("Logging service successfully started. Switching over from console print to logging.")
        return

    try:
        if os.path.exists(log_path):
            logging.basicConfig(filename=log_path, filemode='w',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S', level=logging.getLevelName(log_level))
            print(f"{log_path} will be cleared for new log.")
    except TypeError:
        print("Logger configuration failed! Please double check cofig.json with specification to make sure"
              "proper log level is set. The logger will NOT be started!")
        print(TypeError)
        return
    print("Logging service successfully started. Switching over from console print to logging.")
    logger.info("Logging service successfully started. Switching over from console print to logging.")


def get_current_function_name():
    frm = inspect.stack()[1]
    return inspect.getmodule(frm[0])
