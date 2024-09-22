"""
This script sets up a tool for finding relevant contact persons based on specific employee issues, such as department, position, responsibility, program, and location. It integrates a GPT-based model ("gpt-4o-mini") with predefined functions that use the structured contact data from the dataframe to recommend suitable individuals.

The tool structure includes:
1. Loading a dataframe containing employee contact information.
2. Reading and storing a set of instructions from a text file.
3. Defining a tool called `get_relevant_people`, which matches employees based on various criteria, including department, position, responsibility, program, and location.
"""

# Importing the get_df function from the data module to retrieve a dataframe containing employee contact information.
from data import get_df

# Loading the dataframe containing the employee contact information. 
# This dataframe includes columns such as department, position, responsibilities, programs, and location.
df = get_df()

# Reading an instruction file (stored in 'res/instruction.txt') which contains some predefined guidelines or instructions 
# related to the tool or contact searching process. The file is read as a UTF-8 encoded string.
with open("res/instruction.txt", "r", encoding="utf-8") as f:
    instruction = f.read()  # Storing the file's content into the 'instruction' variable.

# Defining the model that will be used for processing, in this case, it's a GPT-based model named "gpt-4o-mini".
model = "gpt-4o-mini"

# Setting up a list of tools for processing user queries. Here we define one tool, `get_relevant_people`, 
# which will help find relevant contact persons for employee issues based on several parameters.
tools = [
    {
        "type": "function",  # The tool type is 'function' which allows executing specific tasks related to employee contact matching.
        "function": {
            "name": "get_relevant_people",  # The name of the function.
            "description": "Get the most relevant people for a given employee issue.",  # A brief description of what the function does.
            
            # Defining the input parameters that the function will take. These parameters are used to filter the contacts.
            "parameters": {
                "type": "object",  # The parameter type is an object (a set of key-value pairs).
                "properties": {
                    # Filters by the department where the contact should be located.
                    "department": {
                        "type": "string",  # Type of the parameter is a string.
                        "enum": list(df.department.unique()),  # Unique departments are extracted from the dataframe to limit options.
                        "description": "The department the contact person should be in."  # Description of this parameter.
                    },
                    # Filters by the position of the contact person.
                    "position": {
                        "type": "string",  # Type of the parameter is a string.
                        "enum": list(df.position.unique()),  # Unique positions are extracted from the dataframe to limit options.
                        "description": "The position the contact person should be in."  # Description of this parameter.
                    },
                    # Filters by the responsibility of the contact person.
                    "responsibility": {
                        "type": "string",  # Type of the parameter is a string.
                        "enum": list(df.responsibilities.str.split(", ").explode().unique()),  # Extracting and splitting responsibilities to get individual options.
                        "description": "The responsibility the contact person should have."  # Description of this parameter.
                    },
                    # Filters by the program the contact person should be related to.
                    "program": {
                        "type": "string",  # Type of the parameter is a string.
                        "enum": list(df.programs.str.split(", ").explode().dropna().unique()),  # Extracting unique programs and splitting them into individual entries.
                        "description": "The program which is related to the issue."  # Description of this parameter.
                    },
                    # Filters by the location where the contact person is based.
                    "location": {
                        "type": "string",  # Type of the parameter is a string.
                        "enum": list(df.location.unique()),  # Unique locations are extracted from the dataframe to limit options.
                        "description": "The location where the contact person should be located."  # Description of this parameter.
                    }
                },
                # None of these parameters are required, which means they can be provided optionally to refine the search.
                "required": []
            }
        }
    }
]