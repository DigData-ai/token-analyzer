from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import requests
import os
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chat_models import ChatOpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"
model = SentenceTransformer('paraphrase-MiniLM-L6-V2')

def chat_completion_request(messages, functions=None, function_call=None, model="gpt-3.5-turbo-0613"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
    

sentences = [
    "What's the current price of Bitcoin?",
    "What's the current volume of Bitcoin?",
    "Can you tell me the latest Bitcoin price?",
    "I'm curious, how much does Bitcoin cost right now?",
    "Do you have the real-time value of Bitcoin?",
    "What's the price of Bitcoin at this moment?",
    "Could you provide me with the current value of Bitcoin?",
    "I'd like to know the present price of Bitcoin, please.",
    "Can you give me an update on the Bitcoin price?",
    "What's the going rate for Bitcoin nowadays?",
    "Is there a way to find out the live price of Bitcoin?",
    "I'm interested in knowing the current market value of Bitcoin.",
    "Could you share the current trading price of Bitcoin?",
    "Can you let me know the price of Bitcoin in the market today?",
    "How much does one Bitcoin cost at the current time?",
    "What's the value of Bitcoin right now?",
    "I'm wondering what the price tag is for Bitcoin these days.",
    "Can you provide me with the current price of Bitcoin in USD?",
    "What's the going rate for Bitcoin in the cryptocurrency market?",
    "I'd like to stay updated on the price fluctuations of Bitcoin. Where can I find the current price?",
    "Is there a reliable source to get the up-to-date price of Bitcoin?",
    "What's the price of Bitcoin as of today?",
    "I'm curious about the current value of Bitcoin. Can you help?",
    "How much do I need to pay for one Bitcoin right now?",
    "Can you fetch me the real-time price of Bitcoin?",
    "What's the market price of Bitcoin at the moment?",
    "I want to invest in Bitcoin. What's the price I should expect?",
    "Is the price of Bitcoin going up or down currently?",
    "Can you provide me with the latest price update for Bitcoin?",
    "What's the cost of buying Bitcoin today?",
    "I'm interested in trading Bitcoin. Can you give me the current price?",
    "How does the current Bitcoin price compare to its all-time high?",
    "Can you tell me the price of Bitcoin in different currencies?",
    "What's the average price of Bitcoin over the past 24 hours?",
    "Is the price of Bitcoin stable or experiencing volatility?",
    "I'm considering purchasing Bitcoin. What's the best time based on the current price?",
    "Can you give me the opening and closing prices of Bitcoin for today?",
    "What factors are influencing the current price of Bitcoin?",
    "How frequently is the Bitcoin price updated in the market?",
    "Can you share the historical price chart for Bitcoin over the past month?",
    "What's the price trend of Bitcoin in the last week?"
]


def get_live_price(message):
  message = message["function_call"]["arguments"].split("\"")[3]
  res = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={message.lower()}&vs_currencies=usd')
  res = res.json()
  res = res[message.lower()]["usd"]
  return res


def get_similarities(query):
    sentence_embedding = model.encode(sentences)
    prompt_embedding = model.encode(query)
    similarities = {}

    for i in range(len(sentences)):
        similarities[sentences[i]] = cosine_similarity(prompt_embedding.reshape(1, -1), sentence_embedding[i].reshape(1, -1))[0][0]

    return similarities

def analyzing_query(query):
    similarities = get_similarities(query)

    if max(similarities.values()) >= 0.75:
        answer = (query)
    else:
        loader = TextLoader('data.txt')
        index = VectorstoreIndexCreator().from_loaders([loader])
        answer = index.query(query, llm=ChatOpenAI())

    return (answer)

def get_feature_explanation(message):
  message = message["function_call"]["arguments"].split("\"")[3]
  return analyzing_query(message)


functions = [
    {
        "name": "get_feature_explanation",
        "description": "Get the explanation of any feature in DigData and information about Digdata , what they do and etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "description": "The feature that user wants to know about. For example: price, volume, market cap or circulating supply.",
                },
            },
            "required": ["feature"],
        },
    },
    {
        "name": "get_live_price",
        "description": "Get the current price of the token",
        "parameters": {
            "type": "object",
            "properties": {
                "cryptocurrency": {
                    "type": "string",
                    "description": "the name of the cryptocurrency",
                },
                "unit": {
                    "type": "string",
                    "enum": ["usd", "euro"],
                    "description": "The currency of the price.",
                },
            },
            "required": ["cryptocurrency", "format"],
        },
    },
]





app = FastAPI()

class Message(BaseModel):
    query: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)   

@app.get("/")
async def root(query: Message, request: Request):
    # if(request.headers["x-api-key"] != "123456789"):
    #     return {"message": "Invalid API Key"}

    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": query.query})

    chat_response = chat_completion_request(
        messages, functions=functions
    )
    assistant_message = chat_response.json()["choices"][0]["message"]
    messages.append(assistant_message)

    if assistant_message["content"] is not None:
        print(assistant_message)
        return {"message" : assistant_message}
    else:
        funcname = assistant_message["function_call"]["name"]
        my_function = globals().get(funcname)
        if my_function is not None and callable(my_function):
            print(my_function(assistant_message))
            return {"message" : my_function(assistant_message)}
        else:
            print(f"Function '{funcname}' does not exist or is not callable.")
            return {"message" : f"Function does not exist or is not callable."}