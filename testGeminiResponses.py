import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part

# TODO(developer): Update and un-comment below line
PROJECT_ID = "code-analyse"
vertexai.init(project=PROJECT_ID, location="us-central1")

model = GenerativeModel("gemini-1.5-flash-002")

# Define the context as part of the user prompt
context_text = "You are a customer service chatbot for creating documentation of source code. You only explain the customer questions of lines of code with less than 300 words."

# Define examples as part of the user prompt
examples_text = """
Input: #include <iostream>
Output: This line incorporates the contents of the <iostream> header file into the current code.

Input: #include <vector>
Output: This line incorporates the contents of the <vector> header file into the current code.
"""

# Define the user's prompt
user_prompt_content = Content(
    role="user",
    parts=[Part.from_text(f"{context_text}\n\n{examples_text}\nWhat does the following line of code do? #include <string>")]
)

# Define the generation configuration
generation_config = {
    "temperature": 0.2,
    "max_output_tokens": 512,
    "top_p": 0.95,
    "top_k": 40,
}

# Send the prompt and context to the model
response = model.generate_content(
    [user_prompt_content],
    generation_config=generation_config,
)

print(response.text)