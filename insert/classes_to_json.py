import json


def extract_unique_tags(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        unique_tags = set()

        for course in data:
            if "tags" in course and isinstance(course["tags"], list):
                for tag in course["tags"]:
                    unique_tags.add(tag)

        return list(unique_tags)

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file")
    except Exception as e:
        print(f"An unexpected error occured:{e}")


file_path = "data/json/classes.json"
unique_tags_list = extract_unique_tags(file_path)
if unique_tags_list is not None:
    print(unique_tags_list)
