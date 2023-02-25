from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from pydantic import BaseModel
import easyocr
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


""" Below are the examples from the FastAPI documentation, they work.
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
"""


# Create our methods

## CREATION
# Creating a folder for a new subject
@app.get("/create/{subject_id}")
def create_folder(subject_id: str):
    dirname = os.path.dirname(__file__)  # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder,
                            subject_id)  # Creating the new path
    os.mkdir(filename)
    return  # TBD


# Creating a folder for a new week
@app.get("/create/{subject_id}/{week_id}")
def create_folder(subject_id: str, week_id: int):
    dirname = os.path.dirname(__file__)  # Retrieving the current dir path
    filename = os.path.join(
        dirname, name_of_the_subfolder, subject_id, week_id)
    os.mkdir(filename)
    return  # TBD


## DELETION
# Either for a subject
@app.delete("/delete/{subject_id}")
def create_folder(subject_id: str):
    dirname = os.path.dirname(__file__)  # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder,
                            subject_id)  # Creating the new path
    shutil.rmtree(filename, ignore_errors=False)
    return  # TBD


# Or for a week
@app.delete("/delete/{subject_id}/{week_id}")
def create_folder(subject_id: str, week_id: int):
    dirname = os.path.dirname(__file__)  # Retrieving the current dir path
    filename = os.path.join(
        dirname, name_of_the_subfolder, subject_id, week_id)
    shutil.rmtree(filename, ignore_errors=False)
    return  # TBD


# Or for a specific file
@app.delete("/delete/{subject_id}/{week_id}/{file_id}")
def create_folder(subject_id: str, week_id: int, file_id: str):
    dirname = os.path.dirname(__file__)  # Retrieving the current dir path
    filename = os.path.join(
        dirname, name_of_the_subfolder, subject_id, week_id, file_id)
    os.remove(filename)
    return  # TBD


## UPLOADING
# Can only upload files
@app.post("/upload/{subject_id}/{week_id}/{file_id}")
def create_folder(subject_id: str, week_id: int, file_id: str):
    dirname = os.path.dirname(__file__)  # Retrieving the current dir path
    filename = os.path.join(
        dirname, name_of_the_subfolder, subject_id, week_id, file_id)
    """
    TBD
    """
    return  # TBD


## DASHBOARD
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    with open("temp", 'wb+') as writer:
        shutil.copyfileobj(file.file, writer)
        result = reader.readtext("temp")
        ocr_result = ""
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
        json_response = [{'q0':split_string[0], 'a0':split_string[1], 'q1':split_string[2], 'a1':split_string[3], 'q2':split_string[4], 'a2':split_string[5], 'q3':split_string[6], 'a3':split_string[7], 'q4':split_string[8], 'a4':split_string[9]}]

        json_compatible_item_data = jsonable_encoder(json_response)  
        return JSONResponse(content=json_compatible_item_data)

