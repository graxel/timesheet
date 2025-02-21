import os
import time
import datetime as dt
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def start_browser(headless=0):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=2048x1000")
    if headless:
        chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration (optional but recommended in headless mode)
    chrome_options.add_argument("--no-sandbox")  # Disable the sandbox (useful for running on some systems like Docker)
    service = webdriver.ChromeService("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    time.sleep(2)
    driver.set_window_size(2048, 1000)
    return driver


def log_in(driver):

    driver.get('https://portal.insightglobal.com/Candidate/')
    time.sleep(3)

    username_box = driver.find_element(By.CSS_SELECTOR, "input[id='ctl00_cphMain_logIn_UserName']")
    password_box = driver.find_element(By.CSS_SELECTOR, "input[id='ctl00_cphMain_logIn_Password']")
    login_button = driver.find_element(By.CSS_SELECTOR, "input[id='ctl00_cphMain_logIn_Login']")

    load_dotenv()
    username_box.send_keys(os.getenv('TIMESHEET_USERNAME'))
    password_box.send_keys(os.getenv('TIMESHEET_PASSWORD'))

    login_button.click()


def click_correct_week_link(driver):
    # switch to dashboard iframe
    driver.switch_to.default_content()
    driver.switch_to.frame('dashboard')

    table = driver.find_element(By.CSS_SELECTOR, "table[class='rgMasterTable']")
    tbody = table.find_element(By.CSS_SELECTOR, "tbody")

    for tr in tbody.find_elements(By.CSS_SELECTOR, "tr"):
        link = tr.find_element(By.CSS_SELECTOR, "a")
        if "CVS - Machine Learning Engineer" in link.get_attribute("title"):
            tds = tr.find_elements(By.CSS_SELECTOR, "td")
            from_date = dt.datetime.strptime(tds[1].text, "%m/%d/%Y")
            to_date = dt.datetime.strptime(tds[2].text, "%m/%d/%Y")
            if dt.timedelta(days=-2) < dt.datetime.now() - to_date < dt.timedelta(days=4):
                link.click()


def switch_to_timesheet_iframe(driver):
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    non_dashboard_frames = [frame for frame in iframes if frame.get_attribute('id') != 'dashboard']
    driver.switch_to.frame(non_dashboard_frames[0])
    return driver


def fill_out_hours(driver):
    time.sleep(3)

    # get list of widget_container elements for days
    main = driver.find_element(By.CSS_SELECTOR, "table[id='ctl00_ctl00_cphMain_cphMain_tblTimeDays']")
    time.sleep(0.5)
    widget_containers = main.find_elements(By.CSS_SELECTOR, "div[class='widgetContainer']")


    for widget_container in widget_containers[1:6]:
        print("opening day")
        # click add time button
        entries = widget_container.find_element(By.CSS_SELECTOR, "div[id$=entries]")
        click_element(driver, entries, "button")
        time.sleep(0.5)

    for widget_container in widget_containers[1:6]:
        add_hours_to_day(driver, widget_container)

    for widget_container in widget_containers[1:6]:
        print("closing day")
        # save hours for day
        click_element(driver, widget_container, "button[id$='btnsaveadd']")
        time.sleep(0.5)


def click_element(driver, parent, css_selector):
    time.sleep(0.5)
    element = parent.find_element(By.CSS_SELECTOR, css_selector)

    wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds
    wait.until(EC.element_to_be_clickable(element))

    # driver.execute_script("arguments[0].click();", element)
    # driver.execute_script("arguments[0].scrollIntoView(true);", element)

    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()
    time.sleep(0.5)


def add_hours_to_day(driver, widget_container):
    
    # enter day start and end times
    print("adding work hours", end='  ', flush=True)
    start_end = widget_container.find_element(By.CSS_SELECTOR, "tr[id='trStartEnd']")
    click_element(driver, start_end, "input[id$='starttime']")
    click_element(driver, driver, "td[data-hour='8']")
    click_element(driver, driver, "td[data-minute='30']")
    click_element(driver, start_end, "input[id$='endtime']")
    click_element(driver, driver, "td[data-hour='17']")
    click_element(driver, driver, "td[data-minute='0']")

    # add break
    print("adding break", end='  ', flush=True)
    click_element(driver, widget_container, "button[id$='btnBreakAdd']")
    time.sleep(2)

    # enter break start and end times
    print("adding break hours", end='  ', flush=True)
    click_element(driver, driver, "span[data-bind='control: StartTime']")
    click_element(driver, driver, "td[data-hour='12']")
    click_element(driver, driver, "span[data-bind='control: EndTime']")
    click_element(driver, driver, "td[data-hour='12']")
    click_element(driver, driver, "td[data-minute='30']")

    # save break
    print("saving break")
    click_element(driver, driver, "button[class='btn btn-success']")
    time.sleep(0.5)

def confirm_and_submit(driver):
    time.sleep(2)
    # get list of widget_container elements for days
    main = driver.find_element(By.CSS_SELECTOR, "table[id='ctl00_ctl00_cphMain_cphMain_tblTimeDays']")
    time.sleep(0.5)
    widget_containers = main.find_elements(By.CSS_SELECTOR, "div[class='widgetContainer']")
    for widget_container in widget_containers:
        print(widget_container.text.replace('\n', ' '))

    while (x := input("Everything look alright? y/n").lower()) not in ['y', 'n']:
        print(f"Invalid input, please enter 'y' or 'n'.")
    if x == 'y':
        submit_timesheet(driver)
    if x == 'n':
        open_window_for_review()


def submit_timesheet(driver):
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[class='rbDecorated']")
    print(submit_button.get_attribute('value'))
    click_element(driver, driver, "input[class='rbDecorated']")
    time.sleep(1)
    
    final_submit_button = driver.find_element(By.CSS_SELECTOR, "button[id^='widget_submittimesheet_'][id$='_btnsubmit']")
    print(final_submit_button.text)
    click_element(driver, driver, "button[id^='widget_submittimesheet_'][id$='_btnsubmit']")
    driver.quit()


def open_window_for_review():
    print("Check your hours here: https://portal.insightglobal.com/Candidate/")
