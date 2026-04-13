import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


short_ans = 'In short answer'
user_ques = input("Enter Your Question")

hf_token = os.getenv("HF_TOKEN")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=hf_token,
)

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Instruct-0905",
    messages=[
        {
            "role": "user",
            "content": f"{user_ques} in {short_ans}"
        }
    ],
)

print(completion.choices[0].message.content)