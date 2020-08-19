# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 14:05:01 2020

@author: Owner PC
"""
def getSchoolLink(link):
    slashesCount = 0
    for i, character in enumerate(link, 0):
        if str(character) is "/":
            slashesCount = slashesCount + 1
        if slashesCount is 3:
            break
    return link[0 : i]


def downloadDir(string):
    string = string.replace("/", "\\")
    return string
        

def strDir(string):
    invalidChars = ["\"", "*","<", ">", "?", "\\", "|", "/", ":"]
    for character in invalidChars:
        string = string.replace(character, "_")
    return string


def scroll_shim(passed_in_driver, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way)
        
        
def breakingTheTree(elements, parentFolder, downloadDirectory, userCourseLink):
    

    #subtreeElements = driver.find_elements(By.CLASS_NAME, "folder-expander")
    subtreeElementsNames = driver.find_elements(By.CLASS_NAME, "folder-title")
    subtreeElements = [None]*(len(subtreeElementsNames))
    for i, element in enumerate(subtreeElementsNames, 0):
        try:
            subtreeElements[i] = element.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_class_name("folder-expander")
        except NoSuchElementException:
            pass
    subfileElements = driver.find_elements(By.CLASS_NAME, "sExtlink-processed")
    
    for file in subfileElements:
        if file not in elements[1]:

            fileLink = str(file.get_attribute("href"))
            

            if ((userCourseLink + "/gp") in fileLink):
                #fileName = file.text
                #print("Downloading " + fileName)
                downloadFile(fileLink, downloadDirectory, parentFolder)
   
    print("Tree Elements: " + str(len(elements[0])) + "\tSub-tree Elements: " + str(len(subtreeElements)))
    for i, element in enumerate(subtreeElementsNames, 0):        
        if element not in elements[0]:
            #subtreeElements = driver.find_elements(By.CLASS_NAME, "folder-expander")
            scroll_shim(driver, element)
            time.sleep(1)
            #driver.execute_script("arguments[0].scrollIntoView();", element)
            #actions = ActionChains(driver)
            #actions.move_to_element(element).click().perform()
            if subtreeElements[i] is not None:
                subtreeElements[i].click()
            try: 
                os.mkdir(parentFolder + (element.text).replace("/", "-"))
                print("Making folder " + str(parentFolder + strDir(element.text)))
            except FileExistsError: 
                print("Folder already created " + str(parentFolder + strDir(element.text)))
                pass
            #print(str(i) + " " + subtreeElementsNames[i].text)
                   
            [subtreeElementsNames, subfileElements] = breakingTheTree([subtreeElementsNames, subfileElements], parentFolder + (element.text).replace("/", "-") + "\\", downloadDirectory, userCourseLink)
            
    return [subtreeElementsNames, subfileElements]

            


def downloadFile(fileLink, downloadDirectory, parentFolder):
    driver.execute_script("window.open()")
    driver.switch_to_window(driver.window_handles[1])
    driver.get(fileLink)
    try:
        downloadLink = driver.find_element_by_class_name("attachments-file-name").find_element_by_class_name("sExtlink-processed")
        downloadLink.click()
        try: 
            fileName = downloadLink.find_element_by_class_name("infotip").get_attribute("aria-label")
        except NoSuchElementException:
            fileName = driver.find_element_by_class_name("page-title").text
            pass
        try:
            os.rename((downloadDirectory + fileName), \
                      (parentFolder + fileName))
            print("Downloading " + fileName)
            print("Moving to " + parentFolder)
        except FileExistsError:
            os.remove(downloadDirectory + fileName)
            print(fileName + " already exists")
            pass
        except FileNotFoundError:
            print("Could not download: " + fileName + " due to invalid file type")
            pass
    
    except NoSuchElementException:
        print("Error finding download link here: " + fileLink)
        

    driver.close()
    driver.switch_to_window(driver.window_handles[0])

    
    
  
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from builtins import FileExistsError
from selenium.common.exceptions import NoSuchElementException
from tkinter import filedialog
from tkinter import *
root = Tk()

userEmail = str(input("Enter your email for login: "))
userPassword = str(input("Enter your password for login: "))
userCourseLink = str(input("Enter the URL for the homepage of the course you wish to \
                           download course materials for: "))

#downloadDirectory = str(input("Enter the directory in which you would like course contents \
#                              to be downloaded: "))
print("Select the directory in which you would like course contents to be downloaded")
root.filename =  filedialog.askdirectory()
downloadDirectory = downloadDir(root.filename + "/")
print ("Your selected download directory: " + downloadDirectory)
#downloadDirectory = r"C:\Users\Owner PC\Downloads\\"

# =============================================================================
# Preconfiguration
# =============================================================================
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", downloadDirectory)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                       "application/vnd.ms-excel, application/msword, application/octet-stream, \
                       application/vnd.ms-powerpoint, video/mp4, video/x-flv, video/x-ms-wmv, \
                       application/vnd.ms-powerpoint.presentation.macroEnabled.12, video/x-ms-asf, \
                       application/vnd.openxmlformats-officedocument.wordprocessingml.document, \
                       application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, \
                       application/vnd.openxmlformats-officedocument.presentationml.presentation, \
                       application/pdf, application/x-pdf, application/vnd.pdf")

profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
profile.set_preference("pdfjs.disabled", True)
# =============================================================================
# Deplying the Firefox browser and going to the Schoology website
# =============================================================================
driver = webdriver.Firefox(executable_path=r'Downloads/geckodriver/geckodriver.exe', firefox_profile=profile)

driver.get(getSchoolLink(userCourseLink))

# =============================================================================
# Logging In
# =============================================================================
mail = driver.find_element_by_id("username")
mail.send_keys(userEmail)
password = driver.find_element_by_id("password")
password.send_keys(userPassword)
driver.find_element_by_id("signin").click()
time.sleep(3)

driver.get(userCourseLink)
parentFolder = driver.find_element_by_class_name("page-title").find_element_by_class_name("sExtlink-processed").text
parentFolder = downloadDirectory + strDir(parentFolder) + "\\"
try:
    os.mkdir(parentFolder)
except FileExistsError:
    pass


treeElements = []
fileElements = []
elements = [treeElements, fileElements]
breakingTheTree(elements, parentFolder, downloadDirectory, userCourseLink)