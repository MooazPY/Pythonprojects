import requests

questions = [
    
]

parameters = {
    "amount" : 10,
    "type" : "boolean"
}

response = requests.get(url="https://opentdb.com/api.php",params=parameters)

response.raise_for_status()

for i in range(10):
    
    question = (response.json()['results'][i]['question'])
    answer = (response.json()['results'][i]['correct_answer'])
    package = {
        "question" : question,
        "correct_answer" : answer
    }
    questions.append(package)
    
    
question = "NO MORE QUESTIONS"
answer = "NONE"
package = {
        "question" : question,
        "correct_answer" : answer
    }
questions.append(package)

