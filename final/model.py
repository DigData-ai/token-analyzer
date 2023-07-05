import json
import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

openai.api_key = "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"

def chat_completion_request(messages, functions=None, function_call=None, model="gpt-4-turbo-0613"):
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
    
def get_live_price(message):
  message = message["function_call"]["arguments"].split("\"")[3]
  res = requests.get(f'https://api.coingecko.com/api/v3/coins/{message.lower()}/market_chart?vs_currency=usd&days=1&interval=minutes')
  res = res.json()
  res = res['prices'][0]
  return res

def get_animals_position(message):
  response = requests.get('https://jsonplaceholder.typicode.com/todos/1')
  json_data = response.json()
  return json_data["title"]


functions = [
    {
        "name": "get_animals_position",
        "description": "Get the current position of the current animal",
        "parameters": {
            "type": "object",
            "properties": {
                "position": {
                    "type": "string",
                    "description": "The current position of the given animal for example: sleeping, running, jumping and etc.",
                },
                "animal": {
                    "type" : "string",
                    "description" : "The name of the animal , for example cat, dog, rabbit and etc."
                },
            },
            "required": ["animal", "position"],
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

