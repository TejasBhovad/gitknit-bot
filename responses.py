from random import choice,randint


def get_response(user_input:str)->str:
    lowered:str= user_input.lower()

    if lowered == '':
        return "Say something!"
    elif lowered == 'hello':
        return "Hello there!"
    elif lowered == 'bye':
        return "Goodbye!"
    elif lowered == 'roll':
        return f"You rolled a {randint(1,6)}"
    elif lowered == 'flip':
        return choice(['Heads','Tails'])
    else:
        return "I'm sorry, I didn't catch that"
