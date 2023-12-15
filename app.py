from flask import Flask, render_template, request, jsonify
from modules.helditems import item_names

import requests
import os
import time
import json

webhook_url = 'https://discord.com/api/webhooks/1180644024789508209/10PducB3djhbNRO-NIz2Tplz88-qvW6pCVuVbPcaPRzQ7p5anWqgy-dRxIJwMiZ1P03U'
app = Flask(__name__)
change_count = [0]
data = {}
Total_Encounters = [0]
Encounters_shiny = [0]
file_path = "Total_Encounters.json"
file_path2 = "Encounters_shiny.json"
item_name = "none"
current_species = 0
consecutive_encounter_count = 0
last_change_count = change_count[0]
current_streak_species = 0
longest_streak = 0

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

def write_variable_to_file(value):
    data = {'Total_Encounters': value}
    with open(file_path, "w") as file:
        json.dump(data, file)

def write_variable_to_file2(value):
    data = {'Encounters_shiny': value}
    with open(file_path2, "w") as file:
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

        def get_item_name(item):
            # Check if the item value is in the dictionary
            if item in item_names:
                return item_names[item]
            elif item == '0':
                return 'None'
            else:
                return [item]

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
        data['ConsecutiveEncounterCount'] = consecutive_encounter_count
        data['CurrentStreakSpecies'] = current_streak_species
        data['LongestStreak'] = longest_streak

        if 'atkdef' not in data or data['atkdef'] != atkdef:
            change_count[0] += 1  # Increment change count
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

            data['ConsecutiveEncounterCount'] = consecutive_encounter_count
            data['atkdef'] = atkdef  # Update the 'data' dictionary

            # Update the longest streak
            if consecutive_encounter_count > longest_streak:
                longest_streak = consecutive_encounter_count
                current_streak_species = species

            data['CurrentStreakSpecies'] = current_streak_species
            data['LongestStreak'] = longest_streak


        # print (data['item_name'])
        write_variable_to_file(Total_Encounters)
        write_variable_to_file2(Encounters_shiny)

        if data['shinyvalue'] == 1:
            message = f"Shiny encounter! Consecutive encounters of {data['species']}: {consecutive_encounter_count}"
            Encounters_shiny = 0
            write_variable_to_file2(Encounters_shiny)
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

@app.route('/species')
def species():
    # You can pass the 'species' data to the species.html template
    species_value = data.get('species', '')
    return render_template('species.html', data=data)

@app.route('/streak')
def streak():
    # You can pass the 'species' data to the species.html template
    return render_template('streak.html', data=data)

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/get_badge_values')
def get_badge_values():
    # Extract values from the 'data' dictionary
    latest_values = {
        'Attack': data.get('Attack', 0),
        'Defense': data.get('Defense', 0),
        'Speed': data.get('Speed', 0),
        'Special': data.get('Special', 0),
        'item_name': data.get('item_name', 'None'),
        'Species': data.get('species', 0),
    }
    return jsonify(latest_values)

if __name__ == "__main__":
    app.run(debug=True)
