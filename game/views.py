from django.shortcuts import render
from django.views.generic.edit import FormView
from game.forms import ProfileForm

from .game import *
from .dialoGPT import *


game = build_game()
parser = Parser(game)
narration_history = game.describe()
characters = game.get_current_characters()
items = game.get_current_items()
profile_path = "media/images/profile.png"

player = {
    "name": "Player",
    "persona": "I am an explorer from earth. I like to travel to different places and learn about strong but interesting things. I am always excited about exploring the unknown.",
    "appearance": "I am wearing jeans. The jeans are loose but strong. I am wearing windbreaker. The windbreaker is long, black and looks very cold. I am wearing a hat. I'm wearing a hat. The hat is brown and partly hides my face."
}
tokenizer, model = load_models()
chat_history_ids_list = [tokenizer.encode("", return_tensors='pt').long().to(device) for _ in characters]


class ProfileFormView(FormView):
    template_name = "profile.html"
    form_class = ProfileForm
    success_url = "/game"

    def form_valid(self, form):
        global player, profile_path
        player = {
            "name": "Player",
            "persona": form.data["persona"],
            "appearance": form.data["appearance"]
        }
        instance = form.save()
        try:
            profile_path = instance.image.path
        except:
            pass
        return super(ProfileFormView, self).form_valid(form)


def parse_command(request):
    global narration_history, characters, items, player, tokenizer, model, chat_history_ids_list
    if request.method == "POST": 
        if "command" in request.POST:
            command = request.POST["command"]
            narration, current_characters, current_items = parser.parse_command(command)
            narration_history += narration + "\n"
            if current_characters is not None:
                items = current_items
                characters = current_characters
                chat_history_ids_list = [
                    tokenizer.encode("", return_tensors='pt').long().to(device) for _ in characters
                ]
            if current_items is not None:
                items = current_items
        elif "message" in request.POST:
            idx = int(request.POST['characterId'][0]) - 1
            characters[idx]["dialogues"].append(request.POST['message'])
            chat_history_ids, response = get_dialogue(
                tokenizer, model, player, characters[idx], request.POST['message'], chat_history_ids_list[idx]
            )
            characters[idx]["dialogues"].append(response.strip("\n"))
            chat_history_ids_list[idx] = chat_history_ids
    context = {
        "narration": narration_history,
        "location": parser.game.curr_location.name,
        "location_img": "game/locations/" + parser.game.curr_location.name_cleaned + ".png",
        "characters": characters,
        "items": items,
        "profile_img": "images/" + profile_path.split("/")[-1]
    }

    return render(request, 'game.html', context)
