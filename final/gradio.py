import gradio as gr
from gradio.components import Radio

inputs = [
    gr.inputs.Textbox(lines=5, label="Question/Prompt", placeholder="Type a question or SQL prompt here..."),
]

outputs = gr.outputs.Textbox(label="Answer")

title = "DigData Spade"
description = "GPT-4 is a question answering system that can answer questions related to crypto currency. \
    It can also generate SQL queries from a prompt."

examples = [
    ["What is the price of Bitcoin?", "Question-Answer"],
    ["What is the price of Ethereum?", "Question-Answer"],
    ["What is the price of Dogecoin?", "Question-Answer"],
    ["What is the price of Cardano?", "Question-Answer"],
]

gr.Interface(generate_response, inputs, outputs, title=title, description=description, examples=examples).launch()