from data import get_df


df = get_df()

with open("res/instruction.txt", "r", encoding="utf-8") as f:
    instruction = f.read()

model = "gpt-4o-mini"
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_relevant_people",
            "description": "Get the most relevant people for a given employee issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "enum": list(df.department.unique()),
                        "description": "The department the contact person should be in."
                    },
                    "position": {
                        "type": "string",
                        "enum": list(df.position.unique()),
                        "description": "The position the contact person should be in."
                    },
                    "responsibility": {
                        "type": "string",
                        "enum": list(df.responsibilities.str.split(", ").explode().unique()),
                        "description": "The responsibility the contact person should have."
                    },
                    "program": {
                        "type": "string",
                        "enum": list(df.programs.str.split(", ").explode().dropna().unique()),
                        "description": "The program which is related to the issue."
                    },
                    "location": {
                        "type": "string",
                        "enum": list(df.location.unique()),
                        "description": "The location where the contact person should be located."
                    }
                },
                "required": []
            }
        }
    }
]
