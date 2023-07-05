from pydantic import BaseModel
from fastapi import FastAPI
import openai
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

openai.api_key = "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"

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_response(system_intel, prompt): 
    result = openai.ChatCompletion.create(model="gpt-3.5-turbo-0301",
                                 messages=[{"role": "system", "content": system_intel},
                                           {"role": "user", "content": prompt}])
    return result['choices'][0]['message']['content']

class Question(BaseModel):
    text: str


@app.post("/answer")
async def answer_question(question: Question):
    system_intel = "You are GPT-4, answer questions if only they are related to crypto currency else return 'it is out of my scope'."
    return {"answer": generate_response(system_intel, question.text)}

