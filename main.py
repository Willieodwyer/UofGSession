# Auto login a session booker for UofG Sport
import os
import sys
import json
import logging
from logging import handlers
from UofGSessionBooker import UofGSession


def main():
    # Logging
    debug_file = "debug.log"
    if os.path.exists(debug_file):
        os.remove(debug_file)
    log = logging.getLogger("UofG")
    log.setLevel(logging.INFO)
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(log_format)
    log.addHandler(ch)
    fh = handlers.RotatingFileHandler(debug_file,
                                      maxBytes=(1048576 * 5),
                                      backupCount=7)
    fh.setFormatter(log_format)
    log.addHandler(fh)

    # JSON Config
    if len(sys.argv) < 1 and not os.path.exists(sys.argv[1]):
        log.critical("Failed to load config file... exiting")
        exit(-1)

    f = open(sys.argv[1])
    config = json.loads(f.read())
    log.info("Loading config file " + sys.argv[1])

    driver = config["driver"]
    login_address = config["login_address"]
    home_address = config["home_address"]
    basket_address = config["basket_address"]

    fails = {}
    for login in config["logins"]:
        email = login["email"]
        password = login["password"]
        uofg_session = UofGSession(driver,
                                   email,
                                   password,
                                   login_address,
                                   home_address,
                                   basket_address)

        if uofg_session.login():
            log.info("Login Success!!!")
        else:
            log.critical("Login Failed!!!")
            fails[email] = [password]
            continue

        sessions = login["sessions"]
        failed_bookings = []
        for sesh in sessions:
            result = False
            for x in range(1, 6):  # Try 5 times
                if not uofg_session.go_home():
                    log.critical("Unable to go home... skipping.")
                    break
                log.info("Booking attempt {}".format(x))
                if uofg_session.book_class(sesh):
                    log.info("Booking Success!!! ({})".format(sesh))
                    result = True
                    break

            if not result:
                log.error("Booking Failed!!! ({})".format(sesh))
                failed_bookings.append(str(sesh))
            uofg_session.print_available = True

        if len(failed_bookings):
            fails[email] = failed_bookings
        del uofg_session

    if len(fails):
        log.warning("Warning, some bookings have failed {}".format(fails))


if __name__ == '__main__':
    main()
