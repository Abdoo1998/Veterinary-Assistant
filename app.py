from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv 
from pydantic import BaseModel
import os
import time 
import json

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
assistant_id = "asst_SOQL1w6InH94YnNLIhlDhGaD"

app = FastAPI()
client = OpenAI(api_key=api_key, default_headers={"OpenAI-Beta": "assistants=v2"})

class PetInfo(BaseModel):
    name: str
    species: str
    breed: str
    age: int
    reproductive_status: str
    gender: str
    weight: float
    visit_scheduled: bool
    date_time: str = None

@app.post("/create_thread")
def create_thread():
    """Creates a new thread and returns its ID."""
    thread = client.beta.threads.create()
    return thread.id

@app.post("/process_question")
async def process_question(assistant_id: str, thread_id: str, user_question: str = None, image: UploadFile = File(None)):
    """Processes a user question within the specified thread and returns the assistant's response. 
    The user question is optional. Optionally includes an image."""
    
    # Process text question if provided
    if user_question:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_question
        )

    # Process image if provided
    if image:
        image_data = await image.read()
        with open(image.filename, "wb") as f:
            f.write(image_data)
        
        file = client.files.create(
            file=open(image.filename, "rb"),
            purpose="vision"
        )
        
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=[
                {
                    "type": "image_file",
                    "image_file": {"file_id": file.id}
                }
            ]
        )

    # If neither question nor image is provided, raise an exception
    if not user_question and not image:
        raise HTTPException(status_code=400, detail="Either a question or an image must be provided")

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run.status == "completed":
            break
        elif run.status == "failed":
            error_message = f"Run failed with error: {run.last_error}"
            print(error_message)
            raise HTTPException(status_code=500, detail=error_message)
        time.sleep(2)

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    message = messages.data[0].content[0].text.value
    return {"message": message}

@app.post("/process_pet_info")
async def process_pet_info(assistant_id: str, thread_id: str, pet_info: PetInfo):
    """Processes pet information and returns the assistant's response."""
    pet_info_dict = pet_info.dict()
    pet_info_str = json.dumps(pet_info_dict, indent=2)
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"Here's the pet information:\n\n{pet_info_str}\n\nPlease process this information and provide appropriate guidance or questions based on our veterinary assistant protocol."
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run.status == "completed":
            break
        elif run.status == "failed":
            error_message = f"Run failed with error: {run.last_error}"
            print(error_message)
            raise HTTPException(status_code=500, detail=error_message)
        time.sleep(2)

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    message = messages.data[0].content[0].text.value
    return {"message": message}
