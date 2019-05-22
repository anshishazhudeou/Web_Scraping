from configparser import ConfigParser
from selenium import webdriver
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
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
logFileName="AddACourseCS480" + today.strftime("%Y%m%d") + '.txt'


global permissionNumber


def updatePermissionNumber(permissionNumber):
    permissionNumber = format(permissionNumber, "06")
    return permissionNumber


def addCourseRequest(url, username, password, subject, courseCode, chrome, permissionNumber,logger):

    try:

        # set up preference for chrome
        options = Options()
        options.add_argument("--disable-infobars")
        #options.add_argument('--headless')
        #options.set_headless(headless=True)   
        #options.headless = True
        #options.add_argument('-headless')

        # launch the chrome
        #driver = webdriver.Firefox(executable_path="/Users/liangzhou/Documents/nbcCoop/webScraping/addACourse/geckodriver", firefox_options=options)
        chromePath = "/Users/liangzhou/Documents/nbcCoop/webScraping/addACourse/chromedriver"
        driver = webdriver.Chrome(executable_path=chromePath, chrome_options=options)
        driver.get(url)
        #driver.get("https://quest.pecs.uwaterloo.ca/psc/SS/ACADEMIC/SA/c/NUI_FRAMEWORK.PT_AGSTARTPAGE_NUI.GBL?CONTEXTIDPARAMS=TEMPLATE_ID%3aPTPPNAVCOL&scname=ADMN_ENROLL&PanelCollapsible=Y&PTPPB_GROUPLET_ID=UW_ENROLL&CRefName=ADMN_NAVCOLL_1&AJAXTransfer=Y")
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
        #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "SSR_DUMMY_RECV1$sels$1$$0")))
        #driver.find_element_by_id("SSR_DUMMY_RECV1$sels$1$$0").click()
        #click continue button
        #driver.find_element_by_id('DERIVED_SSS_SCT_SSR_PB_GO').click()


        # we advance one more page wait for search button appear
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_SSR_PB_SRCH")))

        # zhe ge weizhi bu ying gai you cs489 zai shopping chart li suo yi jia bu jiancha
        # try to delete every time, if it does not exist, then go forward
        try:
            driver.find_element_by_name("DERIVED_REGFRM1_SSR_PB_SRCH").click()
        except Exception as e:
            try:
                driver.find_eelement_by_id("DERIVED_REGFRM1_SSR_PB_SRCH").click()
            except Exception as e:
                pass

        # we advance one more page, then we need to wait "subject" appear on the web page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SUBJECT$0")))
        # send CS to the subject
        driver.find_element_by_id("SSR_CLSRCH_WRK_SUBJECT$0").send_keys(subject)
        # send 489 to the course code area
        driver.find_element_by_id("SSR_CLSRCH_WRK_CATALOG_NBR$1").send_keys(courseCode)

        # uncheck the tick for show open classes only
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3")))
        driver.find_element_by_id("SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3").click()

        # click search
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")))
        time.sleep(1)
        driver.find_element_by_id("win0divCLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()


        #driver.find_element_by_name("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()

        # since we advance one more page, we need to wait "select" button to be clickable
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SSR_PB_SELECT$1")))
        driver.find_element_by_id("SSR_PB_SELECT$1").click()

        # At here, we could put out produced permissionNumber each time
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$")))
        driver.find_element_by_id("DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$").send_keys(permissionNumber)

        # wait and click the next button
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_NEXT_PB$280$")))
        driver.find_element_by_id("DERIVED_CLS_DTL_NEXT_PB$280$").click()

        # process step 2 of 3
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_LINK_ADD_ENRL$82$")))
        driver.find_element_by_id("DERIVED_REGFRM1_LINK_ADD_ENRL$82$").click()

        # process the last step for the first time. wait and click "finish enrolling button"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_SSR_PB_SUBMIT")))
        driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SUBMIT").click()

        # wait for the status code appear on the web page
        # get the page source of the web page and see if an error in it.
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_DESCR50")))
        src=driver.page_source
        textFound=('Error: unable to add class' in src)

        if (textFound == False):
            # mei you error: zheng ming wo men jiashang le
            tem = str(permissionNumber)
            logger.info("Tried with permission number %s successfully" % str(permissionNumber))
            return
        else:
            tem = str(permissionNumber)
            # you error wo men yao jixuzhao
            logger.info("Tried with permission number %s failed" % str(permissionNumber))


        #click add another class
        driver.find_element_by_id("DERIVED_REGFRM1_SSR_LINK_STARTOVER")

        while(textFound):
            permissionNumber=updatePermissionNumber(int(permissionNumber) + 1)
            #try a different permission number rather than the first time
            #wait for "Add Another Class" appear on the web and click it
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_SSR_LINK_STARTOVER")))
            driver.find_element_by_id("DERIVED_REGFRM1_SSR_LINK_STARTOVER").click()

            # we delete the class in the shopping chart since we wanna enter an new permission number
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "P_DELETE$IMG$0")))
            driver.find_element_by_name("P_DELETE$IMG$0").click()

            # we advance one more page wait for search button appear
            try :
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_SSR_PB_SRCH")))
                time.sleep(1)
                driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SRCH").click()
            except Exception:
                try:
                    driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SRCH").click()
                except Exception:
                    try:
                        driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SRCH").click()
                    except Exception:
                        driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SRCH").click()
            # we advance one more page, then we need to wait "subject" appear on the web page
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SUBJECT$0")))
            # send CS to the subject
            driver.find_element_by_id("SSR_CLSRCH_WRK_SUBJECT$0").send_keys(subject)
            # send 489 to the course code area
            driver.find_element_by_id("SSR_CLSRCH_WRK_CATALOG_NBR$1").send_keys(courseCode)

            # uncheck the tick for show open classes only
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3")))
            driver.find_element_by_id("SSR_CLSRCH_WRK_SSR_OPEN_ONLY$3").click()
            # click search
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")))
            time.sleep(1)
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()
            # since we advance one more page, we need to wait "select" button to be clickable
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "SSR_PB_SELECT$1")))
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SSR_PB_SELECT$1")))
                driver.find_element_by_id("SSR_PB_SELECT$1").click()
            except Exception:
                try:
                    driver.find_element_by_id("SSR_PB_SELECT$1").click()
                except Exception:
                    try :
                        driver.find_element_by_id("SSR_PB_SELECT$1").click()
                    except Exception:
                        driver.find_element_by_id("SSR_PB_SELECT$1").click()


            # At here, we could put out produced permissionNumber each time
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$")))
            driver.find_element_by_id("DERIVED_CLS_DTL_CLASS_PRMSN_NBR$118$").send_keys(permissionNumber)

            # wait and click the next button
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_CLS_DTL_NEXT_PB$280$")))
            driver.find_element_by_id("DERIVED_CLS_DTL_NEXT_PB$280$").click()

            # process step 2 of 3
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_LINK_ADD_ENRL$82$")))
            driver.find_element_by_id("DERIVED_REGFRM1_LINK_ADD_ENRL$82$").click()

            # process the last step for the first time. wait and click "finish enrolling button"
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DERIVED_REGFRM1_SSR_PB_SUBMIT")))
            driver.find_element_by_id("DERIVED_REGFRM1_SSR_PB_SUBMIT").click()

            # wait for the status code appear on the web page
            # get the page source of the web page and see if an error in it.
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DERIVED_REGFRM1_DESCR50")))
            src = driver.page_source
            textFound = ('Error: unable to add class' in src)
            if (textFound == False):
                tem=str(permissionNumber)
                logger.info("Tried with permission number %s successfully" % str(permissionNumber))
                return
            else:
                tem = str(permissionNumber)
                logger.info("Tried with permission number %s failed" % str(permissionNumber))
            # click add another class
            driver.find_element_by_id("DERIVED_REGFRM1_SSR_LINK_STARTOVER")
    except Exception:
        return permissionNumber







def main():
    ###################set up the log file#######################################
    pathExists = os.path.isdir(logPath)
    if (pathExists == False):
        os.makedirs(logPath)




    ##############Log File Set Up############################
    logger = logging.getLogger("AddACourseCS480")
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
            print("succeed with permissionNumber %d" % permissionNumber)
            return









if __name__ == '__main__':
    main()