import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Disable self signed certificate warning since MB8611 uses a self signed cert
requests.packages.urllib3.disable_warnings()

CURRENT_VERSION_POLL_TIMEOUT_SECONDS = 10

def get_driver(headless=False):
  options = ChromeOptions()
  if headless: options.add_argument('--headless=new')
  return webdriver.Chrome(options=options)

def navigate_to_modem(driver, config):
  if not config.has_option('Navigation', 'ModemAddress'):
    print("Cannot navigate, missing required config values")
  driver.get(config['Navigation']['ModemAddress'])

def handle_self_signed_cert(driver):
  if driver.title != "Privacy error": return
  if "ERR_CERT_AUTHORITY_INVALID" not in driver.find_element(By.ID, 'error-code').text:
    print("Unrecognized error")
    return
  
  driver.find_element(By.ID, 'details-button').click()
  driver.find_element(By.ID, 'proceed-link').click()

def login(driver, config):
  if not config.has_option('Auth', 'Username'):
    print("Cannot auth, missing username")
  if not config.has_option('Auth', 'Password'):
    print("Cannot auth, missing password")

  driver.find_element(By.ID, 'loginUsername').send_keys(config['Auth']['Username'])
  
  # Clicking into loginText is required to make loginPassword interactable
  driver.find_element(By.ID, 'loginText').click()
  driver.find_element(By.ID, 'loginPassword').send_keys(config['Auth']['Password'])

  driver.find_element(By.ID, 'LoginApply').click()

def get_software_version_from_element(driver):
  element = WebDriverWait(driver, CURRENT_VERSION_POLL_TIMEOUT_SECONDS).until(
      EC.visibility_of_element_located((By.ID, "MotoHomeSfVer"))
  )
  return element.text

def get_software_version(config, headless=True):
  driver = get_driver(headless)

  try:
    navigate_to_modem(driver, config)
    handle_self_signed_cert(driver)
    login(driver, config)
    current_version = get_software_version_from_element(driver)
  except Exception as e:
    print(e)
    driver.get_screenshot_as_file("screenshot.png")

  driver.close()
  return current_version

def is_modem_accessible(config, timeout):
  if not config.has_option('Navigation', 'ModemAddress'):
    print("Cannot check modem accessibility, missing required config values")

  try:
    requests.get(config['Navigation']['ModemAddress'], timeout=timeout, verify=False)
  except requests.RequestException:
    return False
  
  return True