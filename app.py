from flask import Flask, render_template, request, jsonify
from modules.helditems import get_item_name

import requests
import os
import time
import datetime 
import json

webhook_url = 'https://discord.com/'
app = Flask(__name__)
change_count = [0]
data = {}
Total_Encounters = [0]
Encounters_shiny = [0]
file_path = "Total_Encounters.json"
file_path2 = "Encounters_shiny.json"
file_path3 = "Total_shinies.json"
recent_shiny_file_path = "Recent_Shiny_Encounters.json"
shiny_species_counter_file_path = "shiny_species_counter.json"
item_name = "-"
current_species = 0
consecutive_encounter_count = 0
last_change_count = change_count[0]
current_streak_species = 0
longest_streak = 0
shiny_species_counter = {}

try:
    with open(shiny_species_counter_file_path, "r") as file:
        shiny_species_counter = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    shiny_species_counter = {}

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

    
    if request.method == 'POST':
        # Get the concatenated data from the request payload
        concatenated_data = request.form.get('payload')


        # Split the concatenated data into individual values
        highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef = map(int, concatenated_data.split(','))

        elapsed_time = time.time() - start_time

        attack = atkdef // 16
        defense = atkdef % 16
        speed = spespc // 16
        special = spespc % 16
           

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
    

        if 'atkdef' not in data or data['atkdef'] != atkdef:
            change_count[0] += 1  
            Total_Encounters[0] += 1
            Encounters_shiny += 1
            
            
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

            write_variable_to_file(Total_Encounters)
            write_variable_to_file2(Encounters_shiny)          
            

        if data['shinyvalue'] == 1:
                        
            Encounters_shiny = 0
            write_variable_to_file2(Encounters_shiny)
            Total_shinies[0] += 1
            write_variable_to_file3(Total_shinies)
            species = data['species']
            message = f"Shiny encounter!"
            data['shiny_time']= datetime.datetime.utcnow().isoformat()

             # Update shiny species counter
            species = int(data['species'])
            shiny_species_counter[species] = shiny_species_counter.get(species, 0) + 1
            data['speciescounter'] = shiny_species_counter.get(species, 0)

            # Write shiny species counter to file
            with open(shiny_species_counter_file_path, "w") as counter_file:
                json.dump(shiny_species_counter, counter_file)
            
                    
            recent_shiny = {
            'Species': data['species'],
            'Attack': data['Attack'],
            'Defense': data['Defense'],
            'Speed': data['Speed'],
            'Special': data['Special'],
            'Time': data['shiny_time'],
            'ItemName': data['item_name'],
            'SpeciesCounter': data['speciescounter']
            }


            recent_shiny_list = read_recent_shiny_from_file()
            recent_shiny_list.insert(0, recent_shiny)  # Insert at the beginning

            # Keep only the last 3 shiny encounters
            recent_shiny_list = recent_shiny_list[:3]

            write_recent_shiny_to_file(recent_shiny_list)
            payload = {'content': message}
            headers = {'Content-Type': 'application/json'}

            response = requests.post(webhook_url, json=payload, headers=headers)

            if response.status_code == 204:
                print("Message sent successfully")
            else:
                print(f"Failed to send message. Status code: {response.status_code}")
        
            



        if data['Attack'] > 14 and data['Defense'] > 14 and data['Speed'] > 14 and data['Special'] > 14:
            message = f"perfect DV {data['species']} encountered"
            payload = {'content': message}
            headers = {'Content-Type': 'application/json'}

            response = requests.post(webhook_url, json=payload, headers=headers)

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

@app.route('/recent_shiny_data')
def get_recent_shiny_data():
    recent_shiny_data = read_recent_shiny_from_file()
    return jsonify({'RecentShinyEncounters': recent_shiny_data})

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

if __name__ == "__main__":
    app.run(debug=True)
