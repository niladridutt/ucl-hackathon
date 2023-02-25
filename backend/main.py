from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
import os #To be able to mkdir
import shutil # To be able to remove folders+contents
from gpt.request_gpt import text_to_df, get_context_encoding, execute
app = FastAPI()

name_of_the_subfolder = 'items'


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
    dirname = os.path.dirname(__file__) # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder, subject_id) # Creating the new path
    os.mkdir(filename)
    return #TBD

# Creating a folder for a new week
@app.get("/create/{subject_id}/{week_id}")
def create_folder(subject_id: str, week_id: int):
    dirname = os.path.dirname(__file__) # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder, subject_id, week_id) # Creating the new path
    os.mkdir(filename)
    return #TBD


## DELETION
# Either for a subject
@app.delete("/delete/{subject_id}")
def create_folder(subject_id: str):
    dirname = os.path.dirname(__file__) # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder, subject_id) # Creating the new path
    shutil.rmtree(filename, ignore_errors=False)
    return #TBD

# Or for a week
@app.delete("/delete/{subject_id}/{week_id}")
def create_folder(subject_id: str, week_id: int):
    dirname = os.path.dirname(__file__) # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder, subject_id, week_id) # Creating the new path
    shutil.rmtree(filename, ignore_errors=False)
    return #TBD

# Or for a specific file
@app.delete("/delete/{subject_id}/{week_id}/{file_id}")
def create_folder(subject_id: str, week_id: int, file_id: str):
    dirname = os.path.dirname(__file__) # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder, subject_id, week_id, file_id) # Creating the new path
    os.remove(filename)
    return #TBD


## UPLOADING
# Can only upload files
@app.post("/upload/{subject_id}/{week_id}/{file_id}")
def create_folder(subject_id: str, week_id: int, file_id: str):
    dirname = os.path.dirname(__file__) # Retrieving the current dir path
    filename = os.path.join(dirname, name_of_the_subfolder, subject_id, week_id, file_id) # Creating the new path
    """
    TBD
    """
    return #TBD

@app.get("/test")
def ocr_gpt():
    import easyocr
    import numpy as np
    reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
    result = reader.readtext('test.png')
    ocr_result = ""
    for i in result:
        ocr_result += (i[1]+" ")
    df = text_to_df(ocr_result)
    context = get_context_encoding(df)
    answer = execute(context, id=2, age="university student", prompt="")
    return answer