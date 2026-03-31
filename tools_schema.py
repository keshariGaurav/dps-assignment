tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "read_school_information",
            "description": "Reads a local text file and returns its full content as string",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to a local file",
                        "default": "school_info.txt"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_principle_information",
            "description": "Reads a local text file and returns its full content as string",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to a local file",
                        "default": "school_principle.txt"
                    }
                },
                "required": []
            }
        }
    }
]