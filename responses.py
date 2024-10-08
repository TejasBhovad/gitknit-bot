from random import choice,randint
from typing import Dict, List



def get_response(user_input: str, channels: Dict[str, List[str]]) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return "Say something!"
    elif lowered == 'hello':
        return "Hello there!"
    elif lowered == 'bye':
        return "Goodbye!"
    elif lowered == 'roll':
        return f"You rolled a {randint(1, 6)}"
    elif lowered == 'flip':
        return choice(['Heads', 'Tails'])

    # Example usage of channels in a response
    elif lowered == 'list channels':
        return f"Channels in this server: {channels}"
    else:
        return "I'm sorry, I didn't catch that."
