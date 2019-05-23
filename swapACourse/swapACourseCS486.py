from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import logging
import re
# Import smtplib for the actual sending function
import smtplib
import os
import logging
from datetime import timedelta
import os



# find the date of yesterday
today = datetime.today().date()


logLocation= '/Users/liangzhou/Documents/nbcCoop/webScraping/addACourse'
logPath = logLocation + today.strftime('/%Y/%m/%d')
logFileName="AddACourseCS486" + today.strftime("%Y%m%d") + '.txt'


global permissionNumber


def updatePermissionNumber(permissionNumber):
    permissionNumber = format(permissionNumber, "06")
    return permissionNumber


def addCourseRequest(url, username, password, subject, courseCode, chrome, permissionNumber,logger):

    try:

        # set up preference for chrome
        options = Options()
        #options.add_argument('--headless')

        # launch the chrome
        driver = webdriver.Firefox(executable_path="/Users/liangzhou/Documents/nbcCoop/webScraping/addACourse/geckodriver", firefox_options=options)
        driver.get(url)
        driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div/form/div/div/div[10]/a').click()
        driver.find_element_by_id("username").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)
        driver.find_element_by_name("_eventId_proceed").click()

        ################ Try to add the course for the first time########################
        # click enroll button
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "UWSA_ENROLL$2")))
        driver.find_element_by_id("UWSA_ENROLL$2").click()
        # wait up to 20 secs that "main_target_win0" appear and switch to it
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "main_target_win0")))
        # wait and click swap button at the top
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                    "/html/body/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[6]/td[3]/div/div/table/tbody/tr/td[26]/a/span")))
        driver.find_element_by_xpath(
            "/html/body/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[6]/td[3]/div/div/table/tbody/tr/td[26]/a/span").click()
        #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "SSR_DUMMY_RECV1$sels$1$$0")))
        #driver.find_element_by_id("SSR_DUMMY_RECV1$sels$1$$0").click()
        #click continue button
        #driver.find_element_by_id('DERIVED_SSS_SCT_SSR_PB_GO').click()

         # select cs 486
        driver.find_element_by_id("DERIVED_REGFRM1_DESCR50$225$").click()
        driver.find_element_by_xpath("/html/body/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[6]/td[2]/div/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/div/select/option[3]").click()

        # click search button
        driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SRCH$145$").click()

        # we advance one more page, then we need to wait "subject" appear on the web page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SUBJECT$0")))
        # send CS to the subject
        driver.find_element_by_id("SSR_CLSRCH_WRK_SUBJECT$0").send_keys(subject)
        # send 370 to the course code area
        driver.find_element_by_id("SSR_CLSRCH_WRK_CATALOG_NBR$1").send_keys(courseCode)

        # uncheck the tick for show open classes only
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3")))
        driver.find_element_by_id("SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3").click()
        #
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")))
        driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()

        # select section 2
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_PB_SELECT$2")))
        driver.find_element_by_id("SSR_PB_SELECT$2").click()

        # send permission number to permissin Nur box
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$")))
        driver.find_element_by_id("DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$").send_keys(permissionNumber)

        # click next for class preference
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_NEXT_PB$280$")))
        driver.find_element_by_id("DERIVED_CLS_DTL_NEXT_PB$280$").click()

        # click finish swapping
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_SSR_PB_SUBMIT")))
        driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SUBMIT").click()

        # wait for the status code appear on the web page
        # get the page source of the web page and see if an error in it.
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_DESCR50")))
        src = driver.page_source
        textFound = ('Error: Unable to swap class' in src)


        while(textFound):
            # wait for the swap button at the top apeear, then start for a second try        # wait and click swap button at the top
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                        "/html/body/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[6]/td[3]/div/div/table/tbody/tr/td[26]/a/span")))
            driver.find_element_by_xpath(
                "/html/body/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr/td/table/tbody/tr[6]/td[3]/div/div/table/tbody/tr/td[26]/a/span").click()
            permissionNumber=updatePermissionNumber(int(permissionNumber) + 1)

            #try a different permission number rather than the first time
            #wait for "Add Another Class" appear on the web and click it
            # we advance one more page wait for select dropbox appear
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_DESCR50$225$")))
            driver.find_element_by_id("DERIVED_REGFRM1_DESCR50$225$").click()

            # select cs 486
            driver.find_element_by_id("DERIVED_REGFRM1_DESCR50$225$").click()
            driver.find_element_by_xpath(
                "/html/body/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[6]/td[2]/div/table/tbody/tr/td/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/div/select/option[3]").click()

            # click search button
            driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SRCH$145$").click()

            # we advance one more page, then we need to wait "subject" appear on the web page
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SUBJECT$0")))
            # send CS to the subject
            driver.find_element_by_id("SSR_CLSRCH_WRK_SUBJECT$0").send_keys(subject)
            # send 486 to the course code area
            driver.find_element_by_id("SSR_CLSRCH_WRK_CATALOG_NBR$1").send_keys(courseCode)

            # uncheck the tick for show open classes only
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3")))
            driver.find_element_by_id("SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3").click()
            # click search
            time.sleep(1)
            searchCounter = 0
            while (searchCounter < 3):
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")))
                    driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()
                    break
                except Exception:
                    searchCounter += 1

            # select section 1
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_PB_SELECT$2")))
            driver.find_element_by_id("SSR_PB_SELECT$2").click()


            # send permission number to permissin Nur box
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$")))
            driver.find_element_by_id("DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$").send_keys(permissionNumber)

            # click next for class preference
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_NEXT_PB$280$")))
            driver.find_element_by_id("DERIVED_CLS_DTL_NEXT_PB$280$").click()

            # click finish swapping
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_SSR_PB_SUBMIT")))
            driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SUBMIT").click()

            # wait for the status code appear on the web page
            # get the page source of the web page and see if an error in it.
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_DESCR50")))
            src = driver.page_source
            textFound = ('Error: Unable to swap class' in src)

            if (textFound == False):
                tem = str(permissionNumber)
                print("Tried with permission number %s successfully" % str(permissionNumber))
                logger.info("Tried with permission number %s successfully" % str(permissionNumber))
                return
            else:
                tem = str(permissionNumber)
                print("Tried with permission number %s failed" % str(permissionNumber))
                logger.info("Tried with permission number %s failed" % str(permissionNumber))
                # click my class schedule
                driver.find_element_by_id("DERIVED_REGFRM1_LINK_STUDY_LIST$218$").click()
    except Exception as e:
            return permissionNumber







def main():
    ###################set up the log file#######################################
    pathExists = os.path.isdir(logPath)
    if (pathExists == False):
        os.makedirs(logPath)




    ##############Log File Set Up############################
    logger = logging.getLogger("AddACourseCS486")
    logger.setLevel(logging.DEBUG)
    # create a file handler which logs even debug messages
    fh = logging.FileHandler(logPath + "/" + logFileName)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handler to logger
    logger.addHandler(fh)
    ####################End#########################################

    permissionNumber=1



    parser = ConfigParser()


    parser.read("/Users/liangzhou/Documents/nbcCoop/webScraping/addACourse/AddACourse.ini")
    url = parser.get('info', 'url')
    username = parser.get('info', 'username')
    password = parser.get('info', 'password')
    subject = parser.get('info', "subject")
    courseCode=parser.get('info', 'courseCode')
    ie = parser.get('info', 'fireFox')

    while(int(permissionNumber)<10000000):
        permissionNumber=addCourseRequest(url, username, password, subject, courseCode,ie, permissionNumber,logger)
        if (str(permissionNumber) == ''):
            # we succeed
            return









if __name__ == '__main__':
    main()