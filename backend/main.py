from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
from typing import List
import shutil
from gpt.request_gpt import text_to_df, get_context_encoding, execute
import pickle
from azure_components.storage import azure_storage
from azure_components.ocr import OCR
app = FastAPI()

name_of_the_subfolder = 'items'
questions = []
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
    answer = execute(context, id=0, age="university student", prompt="")
    split_string = answer.split('\n')
    json_response = [{'q0': split_string[0], # One \n between q and a, two between a and next q
                      'q1': split_string[3],
                      'q2': split_string[6],
                      'q3': split_string[9],
                      'q4': split_string[12]}]
    global questions
    questions = [split_string[0], split_string[3], split_string[6], split_string[9], split_string[12]]
    json_compatible_item_data = jsonable_encoder(json_response)
    return JSONResponse(content=json_compatible_item_data)


@app.post('/check_answers/')
async def giving_back_score(request: Request):
    questions_answers = await request.json()
    global questions
    string_input = ""
    for i in range(5):
        string_input += (questions[i].replace("%s."%str(i+1), "Q%s."%str(i+1))+'\n'+'Answer: '+questions_answers[i]['answer']+'\n'+'\n')
    with open('context.pickle', 'rb') as handle:
        context = pickle.load(handle)
        answer = execute(context, id=3, age="university student", prompt=string_input)
        split_string = answer.split('\n\n')
        json_response = [{'f0': split_string[0], # f for feedback
                          'f1': split_string[1],
                          'f2': split_string[2],
                          'f3': split_string[3],
                          'f4': split_string[4]}]
        json_compatible_item_data = jsonable_encoder(json_response)
        return JSONResponse(content=json_compatible_item_data)