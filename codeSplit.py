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


import re

from vertexai.language_models import ChatModel, InputOutputTextPair

def read_file(file_path):
    # Open the source file and return the contents
    with open(file_path, 'r') as file:
        return file.read()

def split_into_blocks(code, num_blocks):
    blocks = []
    current_block = []
    open_braces = 0
    lines = code.split('\n')

    for line in lines:
        stripped_line = line.strip()
        current_block.append(line)
        open_braces += stripped_line.count('{')
        open_braces -= stripped_line.count('}')
        
        if open_braces == 0 and current_block:
            blocks.append('\n'.join(current_block))
            current_block = []

    if current_block:
        blocks.append('\n'.join(current_block))

    # Merge blocks into the desired number of parts
    merged_blocks = []
    block_size = max(1, len(blocks) // num_blocks)

    for i in range(0, len(blocks), block_size):
        merged_blocks.append('\n'.join(blocks[i:i + block_size]))

    # Ensure we only have the specified number of blocks
    while len(merged_blocks) < num_blocks:
        merged_blocks.append("")

    return merged_blocks

def count_methods_cpp(code):
    method_pattern = re.compile(r'^\s*[\w\[\]]+\s+[\w:~]+\s*\([^)]*\)\s*(?:const)?\s*(?:noexcept)?\s*(?:override)?\s*(?:final)?\s*{', re.MULTILINE)
    return len(method_pattern.findall(code))

def send_chat(file_path, output_file):
    code = read_file(file_path)
    num_methods = count_methods_cpp(code)
    num_blocks = num_methods  # Use the number of methods as the number of blocks
    blocks = split_into_blocks(code, num_blocks)
    
    #tokens = tokenize_code(code); blocks = split_into_blocks(code, num_blocks);  block_strings = blocks_to_string(blocks)

    chat_model = ChatModel.from_pretrained("chat-bison@002")

    parameters = {
            "temperature": 0.2, # Temperature controls the degree of randomness in token selection.
            "max_output_tokens": 256, # Token limit determines the maximum amount of text output.
            "top_p": 0.95,
            "top_k": 40,
    }

    chat = chat_model.start_chat(
        context="""You are a customer service chatbot for creating documentation of source code . 
                You only explain  the customer questions of lines  of code with less than 300 words""",
        examples=[
            InputOutputTextPair(
                input_text="#include <iostream>",
                output_text="This line incorporates the contents of the <iostream> header file into the current code.",
            ),
        ],
    )

    with open(output_file, 'w') as file:
        for i, block in enumerate(blocks, 1):
            code_block = f"Block {i}:\n{block}\n{'-'*40}"
            try:
                if block.strip():
                    response = chat.send_message(code_block, **parameters)  # code blocks are sent here
                    print(f"writing the documentation of block {i} to output file")
                    file.write(f"\n==== Start of Block {i} ====")
                    file.write(f"\n==== Description of Block {i} ====")
                    file.write(response.text.strip())
                    file.write(f"\n==== End of Block {i} ====\n")
                else:
                    file.write(f"\n==== Start of Block {i} ====\n")
                    file.write(f"No code provided in Block {i}")
                    file.write(f"\n==== End of Block {i} ====\n")
                print(f"Documentation of block {i} is finished")
            except FileNotFoundError:
                print(f"Error: File {filename} not found.")
            except Exception as e:
                print(f"An error occurred while sending block {i}: {e}")
    
    # [END generativeaionvertexai_chat]

if __name__ == "__main__":
    filename = "C:\\Users\\shara\\source\\repos\\innovirtual-phase0\\GUI\\App\\InnoVirtual.cpp" 
    output_file = 'output.txt'  # Path to the output file
    send_chat(filename, output_file)

    # [END aiplatform_sdk_chat]

'''
import tokenize 
from io import StringIO

def tokenize_code(code):
    return list(tokenize.generate_tokens(StringIO(code).readline))

def blocks_to_string(blocks):
    result = []
    for block in blocks:
        block_string = "".join(token.string for token in block)
        result.append(block_string)
    return result

def determine_num_blocks(code, lines_per_block=30):
    num_lines = len(code.split('\n'))
    return max(1, num_lines // lines_per_block)

"C:\\Users\\shara\\source\\repos\\innovirtual-phase0\\GUI\\Object\\IVObjectWidget.cpp" 
"C:\\Users\\shara\\OneDrive\\Desktop\\minMaxAvg.cpp"
'''
