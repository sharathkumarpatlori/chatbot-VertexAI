# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START aiplatform_sdk_chat]

import tokenize
from io import StringIO
from vertexai.language_models import ChatModel, InputOutputTextPair
import os
import tkinter as tk
from tkinter import filedialog

def read_file(file_path):
    # Open the source file and return the contents
    with open(file_path, 'r') as file:
        return file.read()

def count_lines(code):
    # Count the number of lines in the code
    return len(code.splitlines())

def tokenize_code(code):
    try:
        return list(tokenize.generate_tokens(StringIO(code).readline))
    except tokenize.TokenError as e:
        print(f"TokenError: {e}")
        return []

def split_into_blocks_by_lines(code, num_blocks):
    """
    Split the code into a given number of blocks based on line count.
    This ensures the number of blocks is proportional to the size of the file.
    """
    lines = code.splitlines()
    block_size = max(1, len(lines) // num_blocks)  # Calculate block size based on line count

    blocks = []
    for i in range(0, len(lines), block_size):
        block = lines[i:i + block_size]
        blocks.append("\n".join(block))

    return blocks

def determine_num_blocks(num_lines):
    """
    Dynamically determine number of blocks based on number of lines.
    Block sizes are adjusted for very small, medium, and large files.
    """
    if num_lines < 100:
        return min(5, num_lines // 10 + 1)  # Small files: max 5 blocks
    elif num_lines < 1000:
        return min(10, num_lines // 100 + 1)  # Medium files: max 10 blocks
    else:
        return max(10, num_lines // 100 + 1)  # Large files: block size adjusts to 100 lines

def generate_output_filename(source_file):
    """
    Automatically generate an output filename based on the source file name.
    Example: if source_file is 'addSubtract.cpp', the output file will be 'output_addSubtract.txt'.
    """
    base_name = os.path.basename(source_file)  # Extract file name from full path
    name_without_extension = os.path.splitext(base_name)[0]  # Remove extension
    return f"output_{name_without_extension}.txt"

def browse_file():
    """
    Open a file dialog for the user to select a source file.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select the Source Code File",
        filetypes=[("C++ Files", "*.cpp"), ("Python Files", "*.py"), ("All Files", "*.*")]
    )
    return file_path

def send_chat(file_path, output_file):
    code = read_file(file_path)
    num_lines = count_lines(code)
    
    # Determine the number of blocks dynamically based on file length
    num_blocks = determine_num_blocks(num_lines)
    
    # Split the code into a reasonable number of blocks based on line count
    blocks = split_into_blocks_by_lines(code, num_blocks)

    chat_model = ChatModel.from_pretrained("chat-bison@002")

    # Increased max_output_tokens to ensure larger code blocks are handled
    parameters = {
        "temperature": 0.2,  # Temperature controls the degree of randomness in token selection.
        "max_output_tokens": 512,  # Increased token limit to handle larger blocks of code.
        "top_p": 0.95,
        "top_k": 40,
    }

    chat = chat_model.start_chat(
        context="""You are a customer service chatbot for creating documentation of source code. 
                You only explain the customer questions of lines of code with less than 300 words.""",
        examples=[
            InputOutputTextPair(
                input_text="#include <iostream>",
                output_text="This line incorporates the contents of the <iostream> header file into the current code.",
            ),
        ],
    )

    with open(output_file, 'w') as file:
        last_processed_line = 0  # Track the last line processed to ensure no skipping

        for i, block in enumerate(blocks, 1):
            code_block = f"Block {i}:\n{block}\n{'-'*40}"
            print(f"Processing Block {i}...")  # Console output for block status

            try:
                if block.strip():
                    # Process the code block
                    response = chat.send_message(code_block, **parameters)
                    formatted_response = response.text.strip().replace('. ', '.\n')

                    # Write the block information
                    file.write(f"\n==== Start of Block {i} ====\n")
                    file.write(f"\n==== Description of Block {i} ====\n")
                    file.write(formatted_response)
                    file.write(f"\n==== End of Block {i} ====\n")

                    # Ensure no skipped lines by tracking the processed line numbers
                    processed_lines = block.splitlines()
                    current_line_number = last_processed_line + len(processed_lines)
                    last_processed_line = current_line_number

                else:
                    file.write(f"\n==== Start of Block {i} ====\n")
                    file.write(f"No code provided in Block {i}")
                    file.write(f"\n==== End of Block {i} ====\n")

                print(f"Finished Block {i}.")  # Console output to mark end of block

            except FileNotFoundError:
                print(f"Error: File {file_path} not found.")
            except Exception as e:
                print(f"An error occurred while sending block {i}: {e}")
                file.write(f"\n==== Error in Block {i} ====")
                file.write(f"\n{e}\n")
                file.write(f"\n==== End of Error in Block {i} ====\n")

if __name__ == "__main__":
    # Open file dialog to select source file
    source_file = browse_file()

    if source_file:
        # Generate the output filename based on the source file name
        output_file = generate_output_filename(source_file)

        print(f"Source File: {source_file}")
        print(f"Output File: {output_file}")

        send_chat(source_file, output_file)
    else:
        print("No file selected.")

    # [END aiplatform_sdk_chat]