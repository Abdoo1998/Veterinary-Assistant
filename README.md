# Veterinary Assistant API

This project implements a FastAPI-based backend for a Veterinary Assistant chatbot. It uses OpenAI's GPT model to process pet information, answer questions, and analyze images related to veterinary care.

## Features

- Create conversation threads
- Process text-based questions about pet care
- Analyze pet-related images
- Handle structured pet information input
- Integrate with OpenAI's Assistant API

## Prerequisites

- Python 3.7+
- OpenAI API key
- FastAPI
- Pydantic
- python-dotenv

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/Abdoo1998/Veterinary-Assistant.git
   cd veterinary-assistant-api
   ```

2. Install the required dependencies:
   ```
   pip install fastapi uvicorn openai python-dotenv pydantic
   ```

3. Set up your environment variables:
   Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Update the `assistant_id` in the code with your specific OpenAI Assistant ID.

## Running the Application

Run the FastAPI server using Uvicorn:

```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### 1. Create Thread

- **POST** `/create_thread`
- Creates a new conversation thread.
- Returns: Thread ID

### 2. Process Question

- **POST** `/process_question`
- Parameters:
  - `assistant_id`: String (query)
  - `thread_id`: String (query)
  - `user_question`: String (optional, form)
  - `image`: File (optional, form)
- Processes a user question or image within the specified thread.
- Returns: Assistant's response

### 3. Process Pet Information

- **POST** `/process_pet_info`
- Parameters:
  - `assistant_id`: String (query)
  - `thread_id`: String (query)
  - Request Body: PetInfo object
- Processes structured pet information and provides veterinary guidance.
- Returns: Assistant's response

## PetInfo Structure

```python
{
    "name": str,
    "species": str,
    "breed": str,
    "age": int,
    "reproductive_status": str,
    "gender": str,
    "weight": float,
    "visit_scheduled": bool,
    "date_time": str (optional)
}
```

## Error Handling

- The API includes error handling for failed runs and invalid inputs.
- Appropriate HTTP status codes and error messages are returned in case of issues.

## Notes

- This API is designed to work with OpenAI's Assistant API (Beta).
- Ensure you have the necessary permissions and credits in your OpenAI account.
- The Assistant used in this API should be configured for veterinary-related tasks.

## License

[Specify your license here]

## Contributing

[Add your contributing guidelines here]
