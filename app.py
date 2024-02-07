from flask import Flask, render_template, request, jsonify
from modules.helditems import get_item_name
from modules.pokemon_names import pokemon_names
from modules.maps import map_names

import requests
import os
import time
import datetime 
import json
import atexit
from threading import Lock


webhook_url_shiny = 'https://discord.com/api/webhooks/1200602877224304711/1c_fe-6dP-sSBvjQ684Ds5SO1khOUMtky8TjbN_p1ua6pwEI5AhOIG74ynXJr_hbFOk_' 
webhook_url_perfect_dv = 'https://discord.com/api/webhooks/1200603065942806608/HfQJNkS4BMba-K4_iMIyD-TyrFpSif_UKu3O850xOITUkBYNneWCSuUxHB6jUM0KavPn'
Session_webhook = "https://discord.com/api/webhooks/1201488494346915870/Yx18hrjFSCwR7fyVA5zmggaESg0VSxi4997NKsTcJY7XRvYmki2ZxzLmfruPh_cQ7uJx"

app = Flask(__name__)
change_count = [0]
data = {}
Total_Encounters = [0]
Encounters_shiny = [0]
file_path = "Total_Encounters.json"
file_path2 = "Encounters_shiny.json"
file_path3 = "Total_shinies.json"
recent_shiny_file_path = "static/Recent_Shiny_Encounters.json"
shiny_species_counter_file_path = "shiny_species_counter.json"
item_name = "-"
current_species = 0
consecutive_encounter_count = 0
last_change_count = change_count[0]
current_streak_species = 0
longest_streak = 0
shiny_species_counter = {}
species_counter = {}
shiny_counter_lock = Lock()
shinyhandling = 0
embed = {"image": {"url": ""}}
held_items_counter = {}
lowest_dv_initialized = False
lowest_dv = None


def load_shiny_species_counter():
    try:
        with open(shiny_species_counter_file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
shiny_species_counter = load_shiny_species_counter()

def read_recent_shiny_from_file():
    try:
        with open(recent_shiny_file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_recent_shiny_to_file(recent_shiny):
    with open(recent_shiny_file_path, "w") as file:
        json.dump(recent_shiny, file)

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def read_variable_from_file():
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get('Total_Encounters')
    except (FileNotFoundError, json.JSONDecodeError):
        return 0  

Total_Encounters = read_variable_from_file()

def read_variable_from_file2():
    try:
        with open(file_path2, "r") as file:
            data = json.load(file)
            return data.get('Encounters_shiny')
    except (FileNotFoundError, json.JSONDecodeError):
        return 0  

Encounters_shiny = read_variable_from_file2()

def read_variable_from_file3():
    try:
        with open(file_path3, "r") as file:
            data = json.load(file)
            return data.get('Total_shinies')
    except (FileNotFoundError, json.JSONDecodeError):
        return 0  

Total_shinies = read_variable_from_file3()

def write_variable_to_file(value):
    data = {'Total_Encounters': value}
    with open(file_path, "w") as file:
        json.dump(data, file)

def write_variable_to_file2(value):
    data = {'Encounters_shiny': value}
    with open(file_path2, "w") as file:
        json.dump(data, file)

def write_variable_to_file3(value):
    data = {'Total_shinies': value}
    with open(file_path3, "w") as file:
        json.dump(data, file)

def format_dv_encounter(encounter):
    species_name = pokemon_names.get(encounter['Species'], {'name': f'Unknown {encounter["Species"]}'})['name']
    dv_values = "/".join(map(str, encounter['DV']))
    return f"{dv_values} {species_name}"

def log_session_details():

    # Convert species counter to use Pokémon names
    species_counter_names = {pokemon_names.get(species_id, {"name": f"Unknown {species_id}"})['name']: count for species_id, count in species_counter.items()}

    encounters_list = data.get('EncounterList', [])

    if encounters_list:
        # Get the encounter with the highest combined DV values
        highest_dv_encounter = max(encounters_list, key=lambda x: sum(x['DV']))
        
        # Get the encounter with the lowest combined DV values
        lowest_dv_encounter = min(encounters_list, key=lambda x: sum(x['DV']))
    else:
        highest_dv_encounter = {'Species': 'No encounters', 'DV': [0, 0, 0, 0]}
        lowest_dv_encounter = {'Species': 'No encounters', 'DV': [0, 0, 0, 0]}

    # Create a breakdown of session encounters by species
    encounters_breakdown = "\n".join(f"{pokemon_names.get(int(species_id), {'name': f'Unknown {species_id}'})['name']}: {count}" for species_id, count in species_counter.items())
    
    held_items_breakdown = "\n".join(f"{item}: {count}" for item, count in held_items_counter.items())

    # Create a message with session details
    session_message = f"Session ended ⏰: {data.get('SessionStart', '')}\n" \
                      f"Location 🗺️: {data.get('map_name', '')}\n\n" \
                      f"Session Encounters ⚔️: \n{data.get('EncounterCount', '')}\n\n" \
                      f"Species Encounter Breakdown 📊:\n{encounters_breakdown}\n\n" \
                      f"Held Items Breakdown 🎁:\n{held_items_breakdown}\n\n" \
                      f"Longest Streak 🔁: \n{data.get('LongestStreak', 0)} {pokemon_names.get(current_streak_species)['name']}\n\n" \
                      f"Session Highest DVs 🔼:\n{format_dv_encounter(highest_dv_encounter)}\n\n" \
                      f"Session Lowest DVs 🔽:\n{format_dv_encounter(lowest_dv_encounter)}\n\n" \
                      f"Total Encounters 🌐: \n{data.get('Total_Encounters', 0)}\n" \
                      f"Total Shinies ✨: \n{data.get('Total_shinies', 0)}\n"\
                      
    
    # Create a payload for the webhook
    payload = {'content': session_message}
    headers = {'Content-Type': 'application/json'}

    # Send the message to Discord
    response = requests.post(Session_webhook, json=payload, headers=headers)

    if response.status_code == 204:
        print("Session log sent successfully")
    else:
        print(f"Failed to send session log. Status code: {response.status_code}")

atexit.register(log_session_details)

def calculate_total_unique_shinies():
    # Read the shiny_species_counter.json file
    with open(shiny_species_counter_file_path, "r") as file:
        shiny_species_counter = json.load(file)

    # Calculate the total unique shinies count
    total_unique_shinies_counter = len(shiny_species_counter)

    return total_unique_shinies_counter

start_time = time.time()
data = {'SessionStart': format_time(0)} 

@app.route('/update_data', methods=['GET', 'POST'])
def update_data():
    global start_time
    global current_species
    global consecutive_encounter_count
    global last_change_count
    global current_streak_species
    global longest_streak
    global shinyhandling
    global lowest_dv
    global lowest_dv_initialized
    perfect_dv_sent = False

    headers = {'Content-Type': 'application/json'}
    
    
    if request.method == 'POST':
        # Get the concatenated data from the request payload
        concatenated_data = request.form.get('payload')


        # Split the concatenated data into individual values
        highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef, daytime, mapgroup, mapnumber = map(int, concatenated_data.split(','))

        elapsed_time = time.time() - start_time
        item_name = get_item_name(item)
        attack = atkdef // 16
        defense = atkdef % 16
        speed = spespc // 16
        special = spespc % 16

        # Merge DV values into a single number
        dv_sum = attack + defense + speed + special

        if not lowest_dv_initialized:
            lowest_dv = [attack, defense, speed, special]
            lowest_dv_initialized = True
        else:
            if dv_sum < sum(lowest_dv):
                lowest_dv = [attack, defense, speed, special]
          

        Encounters_shiny = read_variable_from_file2()
        # Update the 'data' dictionary
        data['highestAtkDef'] = highestAtkDef
        data['highestSpeSpc'] = highestSpeSpc
        data['shinyvalue'] = shinyvalue
        data['species'] = species
        data['Attack'] = attack
        data['Defense'] = defense
        data['Speed'] = speed
        data['Special'] = special
        data['EncounterCount'] = change_count[0]
        data['SessionStart'] = format_time(elapsed_time)
        data['Total_Encounters'] = Total_Encounters
        data['item'] = item
        data['item_name'] = get_item_name(item)
        data['Encounters_shiny'] = Encounters_shiny
        data['consecutive_encounter_count'] = consecutive_encounter_count
        data['CurrentStreakSpecies'] = current_streak_species
        data['LongestStreak'] = longest_streak
        data['RecentShinyEncounters'] = read_recent_shiny_from_file()
        data['Total_shinies'] = read_variable_from_file3()
        data['daytime'] = daytime
        data['map'] = f"{mapgroup}.{mapnumber}"
        data['map_name'] = map_names.get(data['map'], "Unknown Location")
        data['lowest_dv'] = lowest_dv

        
        
        

        if 'atkdef' not in data or data['atkdef'] != atkdef:
            change_count[0] += 1  
            Total_Encounters[0] += 1
            Encounters_shiny += 1
            # Update held items counter
            if item_name and item_name not in ["0", "-"]:
                held_items_counter[item_name] = held_items_counter.get(item_name, 0) + 1

            
            if current_species == 0:
                current_species = species
                consecutive_encounter_count = 1
                current_streak_species = species
            elif current_species == species and last_change_count != change_count:
                consecutive_encounter_count += 1
            else:
                current_species = species
                consecutive_encounter_count = 1

            data['consecutive_encounter_count'] = consecutive_encounter_count
            data['atkdef'] = atkdef  # Update the 'data' dictionary

            # Update the longest streak
            if consecutive_encounter_count > longest_streak:
                longest_streak = consecutive_encounter_count
                current_streak_species = species

            data['CurrentStreakSpecies'] = current_streak_species
            data['LongestStreak'] = longest_streak

            encounter_data = {
                'Species': species,
                'DV': [data['Attack'], data['Defense'], data['Speed'], data['Special']],
            }
            data.setdefault('EncounterList', []).append(encounter_data)


            write_variable_to_file(Total_Encounters)
            write_variable_to_file2(Encounters_shiny)

            # Update species counter
            nsspecies_id = str(data.get('species'))
            if nsspecies_id:
                with shiny_counter_lock:
                    nscurrent_counter = species_counter.get(nsspecies_id, 0)
                    species_counter[nsspecies_id] = nscurrent_counter + 1

            species_id_str = str(nsspecies_id)
            species_name = pokemon_names.get(species_id_str, {'name': f'Unknown {species_id_str}'})['name']
            encounter_data = {
                'Species': species_name,
                'DV': [data['Attack'], data['Defense'], data['Speed'], data['Special']],
            }   
            data.setdefault('EncounterList', []).append(encounter_data)
        
            
        if data['shinyvalue'] == 1:
            Encounters_shiny = 0
            write_variable_to_file2(Encounters_shiny)
            Total_shinies[0] += 1
            write_variable_to_file3(Total_shinies)
            species = data['species']
            species_info = pokemon_names.get(species, {"name": "Unknown", "gif": "static/shinygif/unknown.gif"})
            stats_message = f"ATK: {data['Attack']}\nDEF: {data['Defense']}\nSPE: {data['Speed']}\nSPC: {data['Special']}"
            gif_url = species_info.get('gif', "https://www.pokencyclopedia.info/sprites/gen2/ani_crystal_shiny/ani_c-S_unknown.gif")
            shiny_stats_message = f"{stats_message}"


            payload = {
                'content': f"Shiny ✨{species_info['name']} encounter!",
                'embeds': [ 
                    {
                        "image": {
                            "url": gif_url
                        }
                    },
                    {
                        "title": " ",
                        "description": shiny_stats_message
                    }
                ]
            }
            data['shiny_time'] = datetime.datetime.utcnow().isoformat()
           
            # Update shiny species counter
            species_id = str(data.get('species'))
            if species_id:
                with shiny_counter_lock:
                    current_counter = shiny_species_counter.get(species_id, 0)
                    shiny_species_counter[species_id] = current_counter + 1

            # Save updated species counter data
            with open(shiny_species_counter_file_path, 'w') as file:
                json.dump(shiny_species_counter, file, indent=2)

            recent_shiny = {
            'Species': data['species'],
            'Attack': data['Attack'],
            'Defense': data['Defense'],
            'Speed': data['Speed'],
            'Special': data['Special'],
            'Time': data['shiny_time'],
            'ItemName': data['item_name'],
            'SpeciesCounter': shiny_species_counter.get(species_id, 0)
            }

            recent_shiny_list = read_recent_shiny_from_file()
            recent_shiny_list.insert(0, recent_shiny)  # Insert at the beginning

            # Keep only the last 3 shiny encounters
            recent_shiny_list = recent_shiny_list[:3]

            write_recent_shiny_to_file(recent_shiny_list)
            response = requests.post(webhook_url_shiny, json=payload)

            if response.status_code == 204:
                print("Message sent successfully")
            elif response.status_code == 400:
                print(f"Bad Request: {response.text}")
            else:
                print(f"Failed to send message. Status code: {response.status_code}")

            
                response = {'message': 'Data updated successfully'}
                return jsonify(response)
        
            
        
        if data['Attack'] > 14 and data['Defense'] > 14 and data['Speed'] > 14 and data['Special'] > 14 and not perfect_dv_sent:
                species = data['species']
                species_info = pokemon_names.get(species, {"name": "Unknown"})
                message = f"Perfect DV 💎{species_info['name']} encountered!"
                payload = {'content': message,}           
                headers = {'Content-Type': 'application/json'}
                perfect_dv_sent = True
                response = requests.post(webhook_url_perfect_dv, json=payload, headers=headers)

                if response.status_code == 204:
                    print("Message sent successfully")
                else:
                    print(f"Failed to send message. Status code: {response.status_code}")

                 

        return 'Data received successfully'

    elif request.method == 'GET':
        return jsonify(data)

    Total_Encounters[0] = read_variable_from_file()


@app.route('/highestDV')
def highestDV():
    # You can pass the 'species' data to the species.html template
    return render_template('highestDV.html', data=data)

@app.route('/recentencounters')
def recentencounters():
    # You can pass the 'species' data to the species.html template
    return render_template('recentencounters.html', data=data)

@app.route('/recentshinies')
def recentshinies():
    # You can pass the 'species' data to the species.html template
    return render_template('recentshinies.html', data=data)

@app.route('/species')
def species():
    # You can pass the 'species' data to the species.html template
    return render_template('species.html', data=data)

@app.route('/streak')
def streak():
    # You can pass the 'species' data to the species.html template
    return render_template('streak.html', data=data)

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/daytime')
def daytime():
    return render_template('daytime.html', data=data)

@app.route('/uniqueshinies')
def unique_shinies():
    total_unique_shinies_counter = calculate_total_unique_shinies()

    return render_template('uniqueshinies.html', data=data, total_unique_shinies_counter=total_unique_shinies_counter)

@app.route('/get_values')
def get_values():
    values = {
        'Total_shinies': data.get('Total_shinies', 0),
        'SessionStart': data.get('SessionStart', ''),
        'Total_Encounters': data.get('Total_Encounters', 0),
        'Encounters_shiny': data.get('Encounters_shiny', 0),
        'EncounterCount': data.get('EncounterCount', 0),
        'Mapname' : data.get('map_name',0)
    }
    return jsonify(values)


@app.route('/get_badge_values')
def get_badge_values():
    # Extract values from the 'data' dictionary
    latest_values = {
        'Attack': data.get('Attack', 0),
        'SV': data.get('shinyvalue', 0),
        'Defense': data.get('Defense', 0),
        'Speed': data.get('Speed', 0),
        'Special': data.get('Special', 0),
        'item_name': data.get('item_name', '-'),
        'Species': data.get('species', 0),
        'Streak':  data.get('consecutive_encounter_count', 0),
    }
    return jsonify(latest_values)

if __name__ == '__main__':
    app.run(use_reloader=False)
