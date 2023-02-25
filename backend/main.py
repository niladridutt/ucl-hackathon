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
from azure.storage import azure_storage
from azure.ocr import OCR
app = FastAPI()

name_of_the_subfolder = 'items'
reader = easyocr.Reader(['en'])
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
        with open(file.filename, 'wb+') as writer:
            shutil.copyfileobj(file.file, writer)
            storage.upload(file.filename, files)
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
        json_response = [{'q0': split_string[0], # 0, 2, 4, 6, 8 because 1, 3, 5, 7, 9 are the answers
                          'q1': split_string[2],
                          'q2': split_string[4],
                          'q3': split_string[6],
                          'q4': split_string[8]}]
        json_compatible_item_data = jsonable_encoder(json_response)
        return JSONResponse(content=json_compatible_item_data)


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
