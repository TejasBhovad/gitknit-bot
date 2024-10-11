from typing import Dict, List

def get_response(user_input: str, channels: Dict[str, List[str]]) -> str:
    lowered: str = user_input.lower()
    print(f"User input: {lowered}")

    if lowered == '':
        return "Say something!"
    elif lowered == '/close':
        return "Closing thread!"
    else:
        return "I'm sorry, I didn't catch that."