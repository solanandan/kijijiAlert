from bs4 import BeautifulSoup
import requests
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_email = 'your_email@your_domain.com' 
password = 'your_password'


def sendEmail (from_, to_, subject, body):
    msg = MIMEMultipart()
    msg['From'] = from_
    msg['To']  = to_ 
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))
    
    try:
        s = smtplib.SMTP(host='smtp.gmail.com', port=587) #change if domain not gmail.com
        s.ehlo()
        s.starttls()
    
        s.login(from_email, password)
        print('Login Successful.', end=' ')
    except:  
        print('Login Failed.', end=' ')
        
    try:
        s.send_message(msg)
        del(msg)
        s.close()
        print('Email Sent.')
    except:
        print("Sending Failed")          
        
### Run once every 10 minutes ###    
while(not(time.sleep(600))): 
    #### Get postings from URL ####
    #Enter Kijiji search page URL to parse
    URL = 'https://www.kijiji.ca/b-cats-kittens/kitchener-waterloo/c125l1700212?sort=dateDesc'
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'lxml')

    #### Find new postings ####
    #All postings are under <div class = "info-container"> tags
    match = soup.find_all('div', class_='info-container') 
    new_postings = ''
    
    #Open postings.txt
    try:
        f = open("postings.txt","r")
        contents = f.read() 
    #Create file if file does not exist
    except:
        f = open("postings.txt","w+")
        f.close()
        f = open("postings.txt","r")
        contents=[]
    
    #Loop through all postings
    for i in match:
        #get posting title and price and remove \n and excess blank spaces for better readability
        title = i.find('div',class_='title').text.replace('\n','').replace('  ','')
        price = i.find('div',class_='price').text.replace('\n','').replace('  ','')
        #check if the posting is a "Wanted" posting or if price is "Please Contact" (usually implies very expensive)
        #also check if posting exists in the postings.txt file
        if ('wanted' not in title.lower()) and (
                ('$' in price) or ('free' in title.lower())
                ) and (title not in contents):
            #store all relevant postings
            new_postings=new_postings+('{}: {}\n'.format(title,price)) 
    f.close()
    
    #Execute if there are any new postings
    if(len(new_postings) > 0):
        print("New posting found.", end=' ')
        #append new postings to postings.txt
        f = open("postings.txt","a")
        f.write(new_postings)
        f.close()
        print("File updated with new posting.")
        ### Send email with new postings ###
        sendEmail(from_ = from_email, to_ = from_email, 
                  subject = "New Kijiji Posting", body = new_postings)
    else:
        pass
