def read_school_information(file_path="school_info.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {str(e)}"