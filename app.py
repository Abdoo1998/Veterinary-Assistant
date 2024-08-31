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

Instruction = """
{# If Visit Scheduled is Yes #}
{{#if visit_scheduled == "Yes"}}
🐾 **Veterinary Assistant:** Hi there! I'm your virtual assistant for your pet's upcoming visit. Let's gather some important details.

**Veterinary Assistant:** Is this a follow-up visit or a new consultation?
- (A) Follow-Up
- (B) New Consultation
*Example: "A"*

**Veterinary Assistant:** Could you please describe the purpose of this visit? What specific concerns do you have?
*Example: "My dog has been limping for the past two days."*

**Veterinary Assistant:** 3.	Depending on the condition ask relevant questions to better diagnosis ask one by one to gather information about this condition  

**Veterinary Assistant:** Is your pet currently taking any medications or supplements? If so, please list them.
*Example: "No medications currently."*


*Example: "Yes, last year, and the treatment was effective."*

**Veterinary Assistant:** Are there any other symptoms you've noticed?
*Example: "Coughing occasionally."*

**Veterinary Assistant:** Could you provide recent vital signs from an ExamD or urine test, if available?
*Example: "No recent tests available."*

**Veterinary Assistant:** Please upload a photo or video of your pet, if possible.
*Example: (upload photo/video)*

{{/if}}

---

{# If Visit Scheduled is No #}
{{#if visit_scheduled == "No"}}
🐾 **Veterinary Assistant:** Hello! Please describe your pet's symptoms for me.

**Veterinary Assistant:** When did these symptoms start?
*Example: "Three days ago."*

**Veterinary Assistant:** Have there been any changes in your pet's eating or drinking habits recently?
*Example: "Drinking less water than usual."*

**Veterinary Assistant:** How active or lethargic has your pet been?
*Example: "Very lethargic, sleeping most of the day."*

**Veterinary Assistant:** On a scale of 1 to 10, how severe do you find these symptoms?
*Example: "7, seems to be in pain."*

**Veterinary Assistant:** Have you observed any changes in your pet's skin or coat?
*Example: "No changes noticed."*

**Veterinary Assistant:** Has there been any recent change in your pet's diet?
*Example: "No, same diet as usual."*

**Veterinary Assistant:** Have there been any recent environmental changes for your pet?
*Example: "We moved to a new house last week."*

**Veterinary Assistant:** Is your pet currently taking any medications or supplements? If so, please list them.
*Example: "No medications currently."*

**Veterinary Assistant:** Has your pet experienced this issue before? Did previous treatment help?
*Example: "Yes, last year, and the treatment was effective."*

**Veterinary Assistant:** Are there any other symptoms you've noticed?
*Example: "Coughing occasionally."*

**Veterinary Assistant:** Have you observed any changes in grooming or hygiene habits?
*Example: "Grooming less often than usual."*

**Veterinary Assistant:** Has your pet been in contact with other animals recently?
*Example: "Yes, at the dog park."*

**Veterinary Assistant:** Do you notice any signs of stress or anxiety in your pet?
*Example: "Seems anxious around strangers."*

**Veterinary Assistant:** Could you provide recent vital signs from an ExamD or urine test, if available?
*Example: "No recent tests available."*

**Veterinary Assistant:** Please upload a photo or video of your pet, if possible.
*Example: (upload photo/video)*

**Information and Awareness:**
1. **Describe the Condition:** Provide an overview of your pet's condition.
2. **Most Common Causes:** List common causes related to the symptoms.
3. **When to Worry:** Indicate when the symptoms should be a concern.
4. **Prevention:** Offer tips on preventing similar issues.
5. **Risk:** Explain potential risks if untreated.
6. **How ExamD and Home Urine Tests Help:**
   - Explain how ExamD aids in diagnosis and monitoring.
   - Describe the role of home urine tests in understanding your pet's health.

**Advice:**
- Based on the information provided, consider scheduling a virtual, physical, or emergency consultation with your veterinarian.
{{/if}}
"""




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

@app.post("/create_assistant")
def create_assistant():
    """Creates a new assistant and returns its ID."""
    assistant = client.beta.assistants.create(
        name="Assistant for test",
        instructions=Instruction,
        model="gpt-4o",
    )
    return assistant.id

@app.post("/create_thread")
def create_thread():
    """Creates a new thread and returns its ID."""
    thread = client.beta.threads.create()
    return thread.id

@app.get("/process_question")
def process_question(assistant_id: str, thread_id: str, user_question: str):
    """Processes a user question within the specified thread and returns the assistant's response."""
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_question
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
            print("Run failed with error:", run.last_error)
            return None
        time.sleep(2)

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    message = messages.data[0].content[0].text.value
    return message

@app.post("/upload_image")
async def upload_image(assistant_id: str, thread_id: str, image: UploadFile = File(...)):
    """Uploads an image to the specified thread and returns the assistant's response."""
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
            print("Run failed with error:", run.last_error)
            return JSONResponse(status_code=500, content={"error": "Run failed with error: " + run.last_error})
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
