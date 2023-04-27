from pydantic import BaseModel
from fastapi import FastAPI
import openai
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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



def generate_sql_query(prompt):
    openai.api_type = "azure"
    openai.api_base = "https://test -digdata.openai.azure.com/"
    openai.api_version = "2022-12-01"
    openai.api_key = '1c60ef61808b4590b3c6c5d5c86be3ed'
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=f"###  mySQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n###\
                 {prompt}\n\nSELECT",
        temperature=0,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=["#",";"])
    openai.api_key = "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"  
    return response.choices[0].text

class Question(BaseModel):
    text: str


@app.post("/answer")
async def answer_question(question: Question):
    system_intel = "You are GPT-4, answer questions if only they are related to crypto currency else return 'it is out of my scope'."
    return {"answer": generate_response(system_intel, question.text)}


@app.post("/sql")
async def answer_question(question: Question):
    return {"answer": "SELECT" + generate_sql_query(question.text)}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
                