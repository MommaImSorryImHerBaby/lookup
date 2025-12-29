# -- Autodoxxer by @daddymica -- 
# threadpool module
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests 
import json 
import typing  
import sys 
import os
import random

# json file 
config:  dict[str, str] = json.load(open('./config/config.json'))
# proxy file 
proxies: list[str]      = open('./config/proxies.txt').readlines()


class Auto:
    @staticmethod 
    def get_proxy(): # return random proxy from list 
        return random.choice(proxies).strip().replace('\n', '')
    
    def queue_email_ANTI(self: Auto, email: str) -> dict[str, str | None]:
        # queue search 4 email
        # check if email has a valid format 
        if not "@" in email or not "." in email:
            raise Exception(f"email: [{email}] is not valid.") 
        # continue if the email is valid
        # make the request 
        response = requests.get(
            url='https://search-api.dev/search.php',
            params={ # insert email & anti api_key here
                'email': email,
                'api_key': config['anti']
            },
            headers={ # insert user-agent headers here 
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }, # use a proxy 
            proxies={
                'http': self.get_proxy()
            }
        )
        # extract the json data 
        data = response.json()
        # check for errors
        if 'error' in data:
            return { # error                                                                                                                                                                                                                                                                                        
            'email': email,
                'error_code': '0_ANTIAPI', 
                'name': None, 
                'dob': None, 
                'phones': [], 
                'addresses': [], 
                'address': None
            }
        # return full dict 
        return {
            'name': data['name'],
            'dob': data['dob'],
            'phones': data['numbers'],
            'addresses': data.get('addresses'),
            'address': data['addresses'][0] if data.get('addresses', None) else None
        } 
    
    def queue_email_SNUSBASE(self: Auto, email: str) -> dict[str, str | None]:
        # queue snusbase email search
        # pass
        if not ("@" in email) or (not "." in email): 
            raise Exception(f"email: {email} is invalid.")

        response = requests.post(
            url='https://api.snusbase.com/data/search',
            json={ # payload
                'terms': [email], # email here
                'types': ['email'], # u can lookup other types of data asw
                'wildcard': False
            }, 
            headers={ # snusbase api-key
                "Auth": config['snusbase'],
                "content-type": "application/json"
            },
            proxies={
                'http': self.get_proxy()
            },
            timeout=30

        )  # check json
        data = response.json()  
        # check response status
        if 'error' in data or not response.ok:
            return {
                'error_code': '0_SNUSBASE', 
                'name': None, 
                'dob': None, 
                'phones': [], 
                'addresses': [], 
                'address': None
            }
        
        return data 
    

    def thread_handler(self: Auto, workers: int=5) -> typing.Generator[dict[str, str | None]]:
        # handle API calls via threadpool
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # declare the pool
            futures = []
            # create the threads
            for email in self.lines:
                futures.append(executor.submit(self.queue_email_ANTI, email)) 
            # iterate thru the futures 
            # this is a generator expression
            return (future.result() for future in as_completed(futures))

    # constructor
    def __init__(self: Auto):
        # load lines first 
        # check filepath
        if len(sys.argv) > 2:
            if os.path.exists(sys.argv[2]):
                with open(sys.argv[2], 'r') as file:
                    # extract targs as an array 
                    self.lines = file.readlines()
 
        # check the argvar
        if len(sys.argv) < 2:
            # print menu
            print("""Anti-Autodxxer by @ih8ngaz!
            options:
                [-s/--search] [searches anti-api by default]
                [-f/--file]   [doxxes lines]  
                [--snusbase]  [specify snusbase with search]                
        """) 
            exit()
        # 'parse'
        if (sys.argv[1].lower() == "-s") or (sys.argv[1].lower() == '--search'):
            # check if they want snusbase
            if (sys.argv[2].lower() == '--snusbase'):
                # do the snusbase search
                results = self.queue_email_SNUSBASE(sys.argv[3])
                final_string = """"""
                # iterate thru the results
                if results['size'] > 0:
                    for (key, value) in results['results'].items():
                        final_string += f"\n{key}:\n"
                        # val
                        for d in value:
                            final_string += f"email: { d['email']} | password: {d.get('password')} | domain: {d['_domain']}, \n "
                    # display results
                    print(final_string)
                else:
                    print("snusbase yielded 0 results.")

            elif ("@" in sys.argv[2]):
                # continue with the ANTI-api lookup
                search = self.queue_email_ANTI(sys.argv[2])  
                # check for errors
                if not 'error_code' in search.keys():
                    print(f"Name: {search['name']}\nDOB: {search['dob']}\nPhones: {search['phones']}\nAddress: {search['address']}\nAdresses: {search['addresses']}")
                else:
                    print(search)

        elif (sys.argv[1].lower() == '-f') or (sys.argv[1].lower() == '--file'):
            # doxx file lines
            # get file basename first
            basename = os.path.basename(sys.argv[2])[:-4]
            # more worker threads == faster processing speeds
            for result in self.thread_handler(workers=15):
                # check the dict keys for error codes for error handling
                if not 'error_code' in result.keys():
                    with open(f'{basename}-doxxed.txt', 'a+') as export:
                        export.write(f'{result}\n') # new line    
            # dbg output
            print(f"exported to: {basename}-doxxed.txt!")   
            exit()        
        
        




if __name__ == "__main__":
   Auto() 
