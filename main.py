# load libraries
import requests
from requests.exceptions import HTTPError
from IPython.display import clear_output
import re
from flask import Flask,jsonify,request,send_file
from dotenv import load_dotenv
import os
# Define functions

# get details of covid 19 cases
'''
Fetch covid cases indian data through pincode
'''
def get_details(pincode_dist):
    all_del = []
    if len(pincode_dist) == 0 or pincode_dist.lower() == 'india':
        response = requests.get('https://api.covid19india.org/data.json') # database url
        response.raise_for_status()
        jsonResponse = response.json()
        for i in jsonResponse['statewise']:
            if i['state'] == "Total":
                all_del.append(i)
        return all_del        
        
    if pincode_dist.isdigit() == True:
        try:
        #     get district
            response = requests.get('https://api.postalpincode.in/pincode/'+pincode_dist)
            response.raise_for_status()
            # access JSOn content
            jsonResponse = response.json()
            pincode_dist = jsonResponse[0]['PostOffice'][0]['State']
            
            response = requests.get('https://api.covid19india.org/data.json')
            response.raise_for_status()
            jsonResponse = response.json()
            for i in jsonResponse['statewise']:
                if i['state'] == pincode_dist:
                    all_del.append(i)

        except:
            print("not available")
    else:
        response = requests.get('https://api.covid19india.org/data.json')
        response.raise_for_status()
        jsonResponse = response.json()

        for i in jsonResponse['statewise']:
            if i['state'] == pincode_dist.title():
                all_del.append(i)
    return all_del            


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# set env for secret key
load_dotenv()

secret_id = os.getenv('AI_SERVICE_SECRET_KEY')

# print(secret_id)
def check_for_secret_id(request_data):    
    try:
        if 'secret_id' not in request_data.keys():
            return False, "Secret Key Not Found."
        
        else:
            if request_data['secret_id'] == secret_id:
                return True, "Secret Key Matched"
            else:
                return False, "Secret Key Does Not Match. Incorrect Key."
    except Exception as e:
        message = "Error while checking secret id: " + str(e)
        return False,message

@app.route('/chatbot',methods=['POST'])  #main function
def main():
    params = request.get_json()
    input_query=params["data"]
    input_query = input_query[0]['text']
    key = params['secret_id']

    request_data = {'secret_id' : key}
    secret_id_status,secret_id_message = check_for_secret_id(request_data)
    print ("Secret ID Check: ", secret_id_status,secret_id_message)
    if not secret_id_status:
        return jsonify({'message':"Secret Key Does Not Match. Incorrect Key.",
                        'success':False}) 
    else:
        output=''
        val = str(input_query).lower()
        val = val.strip()
        # chcek for india cases
        if val in ['tell me corona cases','tell me about covid 19 cases','tell me about corona cases',
                'what is covid cases today','what are the covid cases today','covid cases in india','covid cases',
                'covid 19 cases','covid19 cases','india cases','covid 19 cases in india','cases in indai',
                'what are the corona cases in india','what are the covid cases','tell me corona cases in india',
                'what are the corona cases']:
            output=get_details("india")
        
        # check for pincode    
        res = val.split()
        pin=''
        for i in res:
            if len(i)== 6 and i.isdigit()==True:
                pin=i
        if pin.isdigit() == True:
            output=get_details(pin)
            
        # extract for state
        if re.search('in',val):
            val = val.split("in ")[1].strip()
            output = get_details(val)   
            
        # normal ted talk    
        if val in ['hi','hello','how are you','hey','hii']:
            output = "Hey there! How can I help you?"     
        else:
            try:
                if re.search("my name is", val) or re.search("i am", val) or re.search("my name", val):
                    try:
                        name = val.split("is ")[1].strip()
                        output = "Hello "+name+"! How can I help you?"
                    except:
                        name = val.split("am ")[1].strip()
                    output = "Hello "+name+"! How can I help you?"
            except:       
                output = "Sorry! We are unable to process your request, please enter a valid query"
        if output == '':
            output = "Sorry! We are unable to process your request, please enter a valid query"
        dict1 = {"Result":output}    
    return jsonify(dict1)     

if __name__ == '__main__':
    app.run()             