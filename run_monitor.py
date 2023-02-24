from requests import get as getRequest, RequestException
from time import sleep
from configparser import ConfigParser 
from monitor_database import MonitorDatabase
from connection_test import ConnectionTest
from mb8611 import get_software_version, is_modem_accessible

CONFIG_FILE = '.env'
TEST_WEBSITE = 'http://www.google.com/'
INTERNET_TIMEOUT = 1
MODEM_TIMEOUT = 1
POLL_DELAY_SECONDS = 5


def get_config():
  config = ConfigParser()
  config.read(CONFIG_FILE)
  return config


def test_internet_connection():
  try:
    response = getRequest(TEST_WEBSITE, timeout=1)
  except RequestException as e:
    print("Request exception: " + str(e))
    return ConnectionTest(None, False, str(e))
  
  timeTakenMS = response.elapsed.microseconds / 1000.0
  return ConnectionTest(timeTakenMS, True, None)


def init_database(database: MonitorDatabase, config: ConfigParser):
  modem_accessible = is_modem_accessible(config, MODEM_TIMEOUT)

  if not modem_accessible:
    database.modem_down()
    return

  software_version = get_software_version(config)
  database.modem_up(software_version)


def handle_status_change(database: MonitorDatabase, config: ConfigParser):
  modem_accessible = is_modem_accessible(config, MODEM_TIMEOUT)

  if modem_accessible == database.modem_is_accessible: return

  if modem_accessible:
    current_software = get_software_version(config)

    if (current_software != database.current_version):
      print(f"Modem firmware version changed: {database.current_version} -> {current_software}")

    database.modem_up(current_software)
  else: database.modem_down()


def poll_loop(database: MonitorDatabase, config: ConfigParser):
  run = True
  last_success = None

  while run:
    try:
      connection_result = test_internet_connection()
      database.save_connection_test(connection_result)

      if connection_result.success != last_success:
        handle_status_change(database, config)
      
      last_success = connection_result.success
      
      print("Current status: " + "connected" if last_success else "disconnected")
      sleep(POLL_DELAY_SECONDS)

    except KeyboardInterrupt:
      print("\nExiting cleanly...")
      run = False
  
  database.close_connection()

if __name__ == "__main__":
  config = get_config()
  database = MonitorDatabase(config)

  poll_loop(database, config)
