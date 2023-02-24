import sqlite3
from datetime import datetime

from connection_test import ConnectionTest

CREATE_CONNECTION_TEST_TABLE = "CREATE TABLE ConnectionTest(ConnectionTestID INTEGER PRIMARY KEY, Time TEXT, TimeTakenMS REAL, Success INTEGER, Error TEXT);"
CREATE_MODEM_STATUS_TABLE = "CREATE TABLE ModemStatus(ModemStatusID INTEGER PRIMARY KEY, Time TEXT, SoftwareVersion TEXT, IsAccessible INTEGER);"

TABLE_DICT = {
  'ConnectionTest': CREATE_CONNECTION_TEST_TABLE,
  'ModemStatus': CREATE_MODEM_STATUS_TABLE
}

def get_connection(config):
  if not config.has_option('Database', 'Filename'):
    print("Cannot connect to database, missing required config values")
  return sqlite3.connect(config['Database']['Filename'])

def table_missing(cursor, table_name):
  found = cursor.execute(f"""
    SELECT name
    FROM sqlite_master
    WHERE type='table' AND name=?
  """, [table_name])

  return found.fetchone() is None

def ensure_tables_exist(connection):
  cursor = connection.cursor()
  creates = ""
  for key in TABLE_DICT:
    if table_missing(cursor, key):
      creates += TABLE_DICT[key]

  if len(creates) == 0: return
  cursor.executescript("BEGIN;" + creates + "COMMIT;")
  cursor.close()

def save_connection_test(conn, ms, success, error):
  cursor = conn.cursor()
  
  data = {
    "Time": datetime.now().isoformat(),
    "TimeTakenMS": ms,
    "Success": success,
    "Error": error
  }
  query = """
    INSERT INTO ConnectionTest (Time, TimeTakenMS, Success, Error)
    VALUES(:Time, :TimeTakenMS, :Success, :Error)
  """
  
  try:
    cursor.execute(query, data)
    conn.commit()
  except Exception as e:
    print("Error when attepting to save data: " + str(data))
    raise e

  cursor.close()

def save_modem_status(conn, version, is_accessible):
  cursor = conn.cursor()

  data = {
    "Time": datetime.now().isoformat(),
    "SoftwareVersion": version,
    "IsAccessible": is_accessible
  }

  query = """
    INSERT INTO ModemStatus (Time, SoftwareVersion, IsAccessible)
    VALUES(:Time, :SoftwareVersion, :IsAccessible)
  """
  
  try:
    cursor.execute(query, data)
    conn.commit()
  except Exception as e:
    print("Error when attepting to save data: " + str(data))
    raise e

  cursor.close()

class MonitorDatabase:
  connection = None
  current_version = None
  modem_is_accessible = None

  def __init__(self, config):
    self.connection = get_connection(config)
    ensure_tables_exist(self.connection)

  def save_connection_test(self, connection_test: ConnectionTest):
    save_connection_test(
      self.connection,
      connection_test.timeTakenMS,
      connection_test.success,
      connection_test.error
    )

  def modem_up(self, version):
    self.modem_is_accessible = True
    self.current_version = version
    save_modem_status(self.connection, self.current_version, True)

  def modem_down(self):
    self.modem_is_accessible = False
    save_modem_status(self.connection, self.current_version, False)

  def close_connection(self):
    self.connection.close()
