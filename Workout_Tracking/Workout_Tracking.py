import requests
import datetime

# To let your sheety data secured 
BEARER_AUTH = "__Your Authentication key from sheety__"


# Nutritionix Data
API_KEY = "__Your Api key from Nutritionix api__"
APP_ID = "__App id from Nutritionix also__"
GENDER = "male"
AGE = "21"


# SET UP THE DATE AND TIME
time = datetime.datetime.now()
date = f"{time.day}/{time.month}/{time.year}"
current_time = time.strftime("%X")


# MAIN WORK
user_input = input("Tell me which exercises you did : ")

# Nutritionix endpiont
ai_endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"


ai_headers = {
    "x-app-id":APP_ID,
    "x-app-key":API_KEY
}

ai_params = {
    "gender" : GENDER,
    "age" : AGE
}

query = {
    "query" : user_input
}


response = requests.post(ai_endpoint,params=ai_params,headers=ai_headers,data=query)
data = response.json()['exercises']


add_row_endpoint = "https://api.sheety.co/79b40ecb8666873fbce41e4a3d706f5d/myWorkouts/sheet1"

bearer_headers = {
    "Authorization" : f"Bearer {BEARER_AUTH}"
}


for i in range(len(data)):
    
    exercise = data[i]['name'].title()
    calories = data[i]['nf_calories']
    duration = data[i]['duration_min'] 
    
    body = {
        "sheet1":{
            "date" : date,
            "time" : current_time,
            "exercise" : exercise,
            "duration" : duration,
            "calories" : calories
            }
    }
    response = requests.post(url=add_row_endpoint,json=body,headers=bearer_headers)
    # print(response.status_code)
