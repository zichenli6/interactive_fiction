from xml.dom.pulldom import CHARACTERS
from django.shortcuts import render
from django.http import HttpResponse
import time

from .game import *

game = build_game()
parser = Parser(game)
narration_history = game.describe()
characters = game.get_current_characters()

# Create your views here.
def home(request):
    return HttpResponse("Home Page")

def parse_command(request):
    global narration_history, characters
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
            characters[idx]["dialogues"].append("I am good! How are you?")
        

    context = {
        "narration": narration_history,
        "location": "game/" + parser.game.curr_location.name.lower().replace(" ", "_") + ".png",
        "characters": characters
    }

    return render(request, 'game.html', context)