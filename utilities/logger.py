import logging
import os

from dotenv import load_dotenv


class Logger:
    """
    Logger is in charge to write different levels of messages
     in file and console using logging module
    """

    @staticmethod
    def get_app_logger_format() -> logging.Formatter:
        """
        Return the standard format of the logger

        Returns:
            app_file_format (logging.Formatter): Format
        """
        # Set formatter for the application
        app_file_format = logging.Formatter("%(asctime)s"
                                            " — %(name)s "
                                            "— %(levelname)s "
                                            "— %(funcName)s:%(lineno)d"
                                            " — %(message)s")
        return app_file_format

    @classmethod
    def set_handler(cls, logger: logging.Logger,
                    handler: logging.Handler) -> logging.Logger:
        """
        Return the logger with the handler configurations applied

        Args:
            logger (logging.Logger): Logger
            handler (logging.Handler): Handler

        Returns:
            logger (logging.Logger): Logger
        """
        # Set format to handler
        handler.setFormatter(cls.get_app_logger_format())
        # Add handler to logger
        logger.addHandler(handler)

        return logger

    @classmethod
    def get_logger_app_file(cls):
        """
        Return the handler associated with the file

        Returns:
            logger (logging.Logger): Logger
        """
        # Initialize environ
        # Load virtual variables
        load_dotenv()  # take environment variables from .env.

        # Create Film Rental System list logger
        logger_app_file = logging.getLogger("Film Rental System file")

        try:
            # Create handler
            handler_file = logging.FileHandler(os.getenv('LOG_FILE_PATH'))

        except FileNotFoundError:
            print("app.log file not found.")
            return None

        # Return the already set logger
        return cls.set_handler(logger_app_file, handler_file)

    @classmethod
    def get_logger_app_terminal(cls):
        """
        Return the handler associated with the terminal

        Returns:
            logger (logging.Logger): Logger
        """
        # Create Film Rental System list logger
        logger_app_terminal = logging.getLogger("Film Rental System"
                                                " list terminal")
        logger_app_terminal.setLevel(logging.DEBUG)

        # Create handler
        handler_terminal = logging.StreamHandler()

        # Return the already set logger
        return cls.set_handler(logger_app_terminal, handler_terminal)

    @classmethod
    def info(cls, message: str):
        """
        Log an info message to the terminal

        Args:
            message (str): Message to log
        """
        logger_app_terminal = cls.get_logger_app_terminal()
        logger_app_terminal.info(message)

    @classmethod
    def warning(cls, message: str):
        """
        Log a warning message to the terminal

        Args:
            message (str): Message to log
        """
        # Write message into the file
        logger_app_file = cls.get_logger_app_file()
        if logger_app_file is not None:
            logger_app_file.warning(message)

        # Write message to terminal
        logger_app_terminal = cls.get_logger_app_terminal()
        logger_app_terminal.warning(message)

    @classmethod
    def error(cls, message: str):
        """
        Log an error message to the terminal

        Args:
            message (str): Message to log
        """
        # Write message into the file
        logger_app_file = cls.get_logger_app_file()
        if logger_app_file is not None:
            logger_app_file.error(message)

        # Write message to terminal
        logger_app_terminal = cls.get_logger_app_terminal()
        logger_app_terminal.error(message)

    @classmethod
    def debug(cls, message: str):
        """
        Log a debug message to the terminal

        Args:
            message (str): Message to log
        """
        # Write message into the file
        logger_app_file = cls.get_logger_app_file()
        if logger_app_file is not None:
            logger_app_file.debug(message)

        # Write message to terminal
        logger_app_terminal = cls.get_logger_app_terminal()
        logger_app_terminal.debug(message)
