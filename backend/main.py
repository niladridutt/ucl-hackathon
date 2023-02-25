from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from pydantic import BaseModel
from typing import List
import numpy as np
import shutil
import os  # To be able to mkdir
import shutil  # To be able to remove folders+contents
from gpt.request_gpt import text_to_df, get_context_encoding, execute
import pickle
from azure_components.storage import azure_storage
from azure_components.ocr import OCR
app = FastAPI()

name_of_the_subfolder = 'items'
# reader = easyocr.Reader(['en'])
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = azure_storage()
ocr = OCR()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/uploadfiles/")
async def create_upload_file(files: List[UploadFile] = File(...)):
    result = ""
    for file in files:
        file_name = ""
        if "jpeg" in file.filename:
            file_name = "test.png"
        elif "png" in file.filename:
            file_name = "test.png"
        elif "jpg" in file.filename:
            file_name = "test.png"
        elif "pdf" in file.filename:
            file_name = "test.pdf"
        with open(file_name, 'wb+') as writer:
            shutil.copyfileobj(file.file, writer)
            with open(file_name, 'rb') as file_:
                storage.delete(file_name)
                storage.upload(file_name, file_)
                ocr_result = ocr.get_ocr(file.filename)
                result += ocr_result
    df = text_to_df(result)
    context = get_context_encoding(df)
    with open('context.pickle', 'wb') as handle:
        pickle.dump(context, handle, protocol=pickle.HIGHEST_PROTOCOL)
    dummy_response = [
        {"Success": "true"}]
    json_compatible_item_data = jsonable_encoder(dummy_response)
    return JSONResponse(content=json_compatible_item_data)


@app.get("/test")
def ocr_gpt():
    with open('context.pickle', 'rb') as handle:
        context = pickle.load(handle)
        answer = execute(context, id=0, age="university student", prompt="")
        # Formatting as JSON
        # TODO: should we keep "1.", "2."... and "Answer:" in the strings
        # q/a/q/a...
        split_string = answer.split('\n')
        """
        json_response = [{'q0': split_string[0], 'a0': split_string[1],
                          'q1': split_string[2], 'a1': split_string[3],
                          'q2': split_string[4], 'a2': split_string[5],
                          'q3': split_string[6], 'a3': split_string[7],
                          'q4': split_string[8], 'a4': split_string[9]}]
        """
        json_response = [{'q0': split_string[0], # One \n between q and a, two between a and next q 
                          'q1': split_string[3],
                          'q2': split_string[6],
                          'q3': split_string[9],
                          'q4': split_string[12],
                          'q5': split_string[15],
                          'q6': split_string[18],
                          'q7': split_string[21],
                          'q8': split_string[24],
                          'q9': split_string[27]}]
        json_compatible_item_data = jsonable_encoder(json_response)
        return JSONResponse(content=json_compatible_item_data)

"""
@app.get('/check_answers/{q0}/{a0}/{q1}/{a1}/{q2}/{a2}/{q3}/{a3}/{q4}/{a4}')
def giving_back_score(q0: str, a0: str, q1: str, a1: str, q2: str, a2: str, q3: str, a3: str, q4: str, a4: str):
    # Format them back to a single string for GPT
    string_input = '1. '+q0+'\n'+'Answer: '+a0+'\n'+'2. '+q1+'\n'+'Answer: '+a1+'\n'+'3. '+q2+'\n'+'Answer: '+a2+'\n'+'4. '+q3+'\n'+'Answer: '+a3+'\n'+'5. '+q4+'\n'+'Answer: '+a4
    with open('context.pickle', 'rb') as handle:
        context = pickle.load(handle)
        answer = execute(context, id=3, age="university student", prompt=string_input)
        split_string = answer.split('\n')
        json_response = [{'f0': split_string[0], # f for feedback
                          'f1': split_string[1],
                          'f2': split_string[2],
                          'f3': split_string[3],
                          'f4': split_string[4]}]
        json_compatible_item_data = jsonable_encoder(json_response)
        return JSONResponse(content=json_compatible_item_data)
"""

@app.get('/check_answers/{questions_answers}')
def giving_back_score(questions_answers):
    # Format them back to a single string for GPT
    string_input = '1. '+questions_answers[0]['question']+'\n'+'Answer: '+questions_answers[0]['answer']+'\n'+'\n'+'2. '+questions_answers[1]['question']+'\n'+'Answer: '+questions_answers[1]['answer']+'\n'+'\n'+'3. '+questions_answers[2]['question']+'\n'+'Answer: '+questions_answers[2]['answer']+'\n'+'\n'+'4. '+questions_answers[3]['question']+'\n'+'Answer: '+questions_answers[3]['answer']+'\n'+'\n'+'5. '+questions_answers[4]['question']+'\n'+'Answer: '+questions_answers[4]['answer']+'\n'+'\n'+'6. '+questions_answers[5]['question']+'\n'+'Answer: '+questions_answers[5]['answer']+'\n'+'\n'+'7. '+questions_answers[6]['question']+'\n'+'Answer: '+questions_answers[6]['answer']+'\n'+'\n'+'8. '+questions_answers[7]['question']+'\n'+'Answer: '+questions_answers[7]['answer']+'\n'+'\n'+'9. '+questions_answers[8]['question']+'\n'+'Answer: '+questions_answers[8]['answer']+'\n'+'\n'+'10. '+questions_answers[9]['question']+'\n'+'Answer: '+questions_answers[9]['answer']
    with open('context.pickle', 'rb') as handle:
        context = pickle.load(handle)
        answer = execute(context, id=3, age="university student", prompt=string_input)
        split_string = answer.split('\n')
        json_response = [{'f0': split_string[0], # f for feedback
                          'f1': split_string[2],
                          'f2': split_string[4],
                          'f3': split_string[6],
                          'f4': split_string[8],
                          'f5': split_string[10], # f for feedback
                          'f6': split_string[12],
                          'f7': split_string[14],
                          'f8': split_string[16],
                          'f9': split_string[18]}]
        json_compatible_item_data = jsonable_encoder(json_response)
        return JSONResponse(content=json_compatible_item_data)