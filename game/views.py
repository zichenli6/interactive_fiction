from tokenize import TokenInfo
from xml.dom.pulldom import CHARACTERS
from django.shortcuts import render
from django.http import HttpResponse
import time

from .game import *
from dialoGPT import *

game = build_game()
parser = Parser(game)
narration_history = game.describe()
characters = game.get_current_characters()

player = {
    "name": "Player",
    "persona": "I am an explorer from earth. I like to travel to different places and learn about strong but interesting things. I am always excited about exploring the unknown.",
    "appearance": "I am wearing jeans. The jeans are loose but strong. I am wearing windbreaker. The windbreaker is long, black and looks very cold. I am wearing a hat. I'm wearing a hat. The hat is brown and partly hides my face."
}
tokenizer, model = load_models()


# Create your views here.
def home(request):
    return HttpResponse("Home Page")

def parse_command(request):
    global narration_history, characters, player, tokenizer, model
    if request.method == "POST": 
        if "command" in request.POST:
            command = request.POST["command"]
            narration, current_characters = parser.parse_command(command)
            narration_history += narration + "\n"
            if current_characters is not None:
                characters = current_characters
        elif "message" in request.POST:
            idx = int(request.POST['characterId'][0]) - 1
            characters[idx]["dialogues"].append(request.POST['message'])
            time.sleep(2)
            get_dialogue(tokenizer, model, player, characters[idx], request.POST['message'])
            characters[idx]["dialogues"].append("I am good! How are you?")

    context = {
        "narration": narration_history,
        "location": "game/locations/" + parser.game.curr_location.name_cleaned + ".png",
        "characters": characters
    }

    return render(request, 'game.html', context)