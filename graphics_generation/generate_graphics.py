import json
import shutil

import pixray


def generate_locations(filename="locations.json"):
    locations = json.load(open(filename, 'r'))
    for location, data in locations.items():
        location = location.lower().replace(" ", "_").replace("/", "_")
        pixray.run(
            prompts=data['appearance'],
            drawer="vqgan",
            quality="best",
            custom_loss="aesthetic",
            output=location + ".png",
            outdir="outputs/locations/" + location
        )


def generate_characters(filename="characters.json"):
    characters = json.load(open(filename, 'r'))
    for name, data in characters.items():
        _name = name.lower().replace(" ", "_")
        pixray.run(
            prompts="A portrait of " + name + ". " + data['appearance'],
            drawer="vqgan",
            quality="normal",
            aspect="portrait",
            custom_loss="aesthetic",
            output=_name + ".png",
            outdir="outputs/characters/" + _name
        )



def generate_items(filename="items.json"):
    items = json.load(open(filename, 'r'))
    for name, data in items.items():
        _name = name.lower().replace(" ", "_")
        pixray.run(
            prompts="A picture of " + name + ". " + data['description'],
            drawer="vqgan",
            quality="normal",
            aspect="square",
            custom_loss="aesthetic",
            output=_name + ".png",
            outdir="outputs/items/" + _name
        )


def collect_images(
    locations_filename="locations.json",
    characters_filename="characters.json",
    items_filename="items.json",
    location_dir="outputs/locations/",
    character_dir="outputs/characters/",
    items_dir="outputs/items/"
):
    locations = json.load(open(locations_filename, 'r'))
    for location, data in locations.items():
        location = location.lower().replace(" ", "_").replace("/", "_")
        try:
            shutil.copy(location_dir + location + "/" + location + ".png", location_dir + location + ".png")
        except shutil.SameFileError:
            print("Source and destination represents the same file.")
        except PermissionError:
            print("Permission denied.")
        except:
            print("Error occurred while copying file.")

    characters = json.load(open(characters_filename, 'r'))
    for name, data in characters.items():
        name = name.lower().replace(" ", "_")
        try:
            shutil.copy(character_dir + name + "/" + name + ".png", character_dir + name + ".png")
        except shutil.SameFileError:
            print("Source and destination represents the same file.")
        except PermissionError:
            print("Permission denied.")
        except:
            print("Error occurred while copying file.")

    items = json.load(open(items_filename, 'r'))
    for name, data in items.items():
        name = name.lower().replace(" ", "_")
        try:
            shutil.copy(items_dir + name + "/" + name + ".png", items_dir + name + ".png")
        except shutil.SameFileError:
            print("Source and destination represents the same file.")
        except PermissionError:
            print("Permission denied.")
        except:
            print("Error occurred while copying file.")


if __name__ == '__main__':
    generate_locations()
    generate_characters()
    generate_items()
    collect_images()
