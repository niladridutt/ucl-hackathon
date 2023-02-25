from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from pydantic import BaseModel
import easyocr
from typing import List
import numpy as np
import shutil
import os  # To be able to mkdir
import shutil  # To be able to remove folders+contents
from gpt.request_gpt import text_to_df, get_context_encoding, execute
import pickle

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


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/uploadfiles/")
async def create_upload_file(files: List[UploadFile] = File(...)):
    ocr_result = ""
    for file in files:
        with open(file.filename, 'wb+') as writer:
            shutil.copyfileobj(file.file, writer)
            result = reader.readtext(file.filename)
            for i in result:
                ocr_result += (i[1] + " ")
    df = text_to_df(ocr_result)
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
        json_response = [{'q0': split_string[0], 'a0': split_string[1],
                          'q1': split_string[2], 'a1': split_string[3],
                          'q2': split_string[4], 'a2': split_string[5],
                          'q3': split_string[6], 'a3': split_string[7],
                          'q4': split_string[8], 'a4': split_string[9]}]

        json_compatible_item_data = jsonable_encoder(json_response)
        return JSONResponse(content=json_compatible_item_data)
