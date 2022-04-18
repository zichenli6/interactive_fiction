from django.shortcuts import render
from django.http import HttpResponse

from .game import *

game = build_game()
parser = Parser(game)
narration_history = game.describe()

# Create your views here.
def home(request):
    return HttpResponse("Home Page")

def parse_command(request):
    global narration_history
    if request.method == "POST": 
        if "command" in request.POST:
            command = request.POST["command"]
            end_game, narration = parser.parse_command(command)
            narration_history += narration + "\n"

    context = {
        "narration": narration_history,
        "location": "game/" + parser.game.curr_location.name.lower().replace(" ", "_") + ".png"
    }

    return render(request, 'game.html', context)