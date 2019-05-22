from configparser import ConfigParser
import requests
import pandas as pd
import numpy as np
import tempfile
import boto3
import os
from datetime import datetime
from bs4 import BeautifulSoup


def traderNotesToDf(parser,venue):

    # send request to the server
    venueLowerCase = venue.lower()
    r = requests.get(parser.get(venueLowerCase, 'url'))

    # get the content from web server
    c = r.content

    # get soup object which contains everything that we need from web
    soup = BeautifulSoup(c, "html.parser")

    # all is a list of tags that contains all information that we need
    all = soup.find_all('table', {'width': "100%"})[0].find_all('tr')

    # update all, all is a list of tags that contains all information that we need
    all = all[1:]

    # get the venue
    # venue=soup.find_all('font', {'face': 'Arial'})[3].text.split(' ')[:2]
    # venue = venue[0] + (venue[1]).upper()
    # create a list of dictionary which will be used to create a data frame later on
    outerList=[]
    for item in all:
        innerList=[]
        if (item.find('font') != None):
            poNumber = int(item.find('font').text.replace(' ', ''))
            poName = item.find_all('font')[1].text

            # Encode poName with 'latin-1' first, then decode it with 'utf-8'. Then we will get the coresponding version
            # of English version of PoName
            encodedPoName = poName.encode('latin-1')
            decodedPoName = str(encodedPoName, 'utf-8', 'ignore')

            # split the decodedPoName by space. If the length of list is greater or equal to 3, then check if the second
            # element is alpha. Otherwise split simply use the first and second element as the shortname
            if (len(decodedPoName.split()) >= 3):
                if decodedPoName.split()[1].isalpha():
                    poShortName = decodedPoName.split()[0] + ' ' + decodedPoName.split()[1]
                else:
                    poShortName = decodedPoName.split()[0] + ' ' + decodedPoName.split()[2]
            else:
                poShortName = decodedPoName.split()[0] + ' ' + decodedPoName.split()[1]

            # split the short name by space
            listOfPoShortName = poShortName.split()
            poShortName = []
            for partOfShortName in listOfPoShortName:
                partOfShortName = ''.join(list(filter(lambda x: x.isalpha(), partOfShortName)))
                poShortName.append(partOfShortName)
            poShortName = poShortName[0] + ' ' + poShortName[1]

            innerList.append(poNumber)
            innerList.append(poName)
            innerList.append(venue)
            innerList.append(poShortName)
            outerList.append(innerList)
    df = pd.DataFrame(np.array(outerList), columns=parser.get('columnName', 'columnName').split())
    return df


def dfToS3(parser, date, venue, df):

    # create a temporary file and fetch the data frame into this temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        df.to_csv(temp, sep='|', index=False)

    # uplodad result from csv to the corresponding keys on s3
    bucketName = parser.get('s3', 'bucketName') # repalce with your bucket name
    key = parser.get('s3', 'key')

    # connect to s3
    s3 = boto3.resource('s3')

    # name of a csv file that we want to upload on s3
    nameOfCsv = "PoList_%s_%s.%s" %(venue,date,'txt')
    keyDir = key + '/' + ('yyyymmdd=%s'%date) + '/'

    #update keyDir(directory) with correspoding file name
    updatedKey = keyDir + nameOfCsv
    data= open(temp.name, 'rb')
    s3.Bucket(bucketName).put_object(Key=updatedKey, Body=data)

    # close the and remove the tem file
    temp.close()
    data.close()
    os.remove(temp.name)


def main():
    parser = ConfigParser()
    # read the configuration file
    parser.read('ref_polist_web_to_s3.ini')
    parser.read('ref_polist_web_to_s3.ini')
    # get the current date
    date = datetime.now().strftime('%Y%m%d')

    # transfer the data from TMX Trader Notes to S3
    venue = parser.get('tsx', 'venue')
    df = traderNotesToDf(parser,venue)
    dfToS3(parser, date, venue, df)

    venue = parser.get('tsxventure', 'venue')
    df = traderNotesToDf(parser,venue)
    dfToS3(parser, date, venue, df)

    venue = parser.get('alpha', 'venue')
    df = traderNotesToDf(parser,venue)
    dfToS3(parser, date, venue, df)


if __name__ == '__main__':
    main()
