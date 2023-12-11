from flask import Flask, render_template, request, jsonify
import requests
import os
import time
import json
webhook_url = 'https://discord.com/api/webhooks/1180644024789508209/10PducB3djhbNRO-NIz2Tplz88-qvW6pCVuVbPcaPRzQ7p5anWqgy-dRxIJwMiZ1P03U'
app = Flask(__name__)
change_count = [0]
data = {}
Total_Encounters = [0]
file_path = "Total_Encounters.json"

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def write_counter(counter):
    counter_file_path = 'counter.txt'

    with open(counter_file_path, 'w') as file:
        file.write(str(counter))

def read_variable_from_file():
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get('Total_Encounters')
    except (FileNotFoundError, json.JSONDecodeError):
        return 0  

Total_Encounters = [read_variable_from_file()]

def write_variable_to_file(value):
    data = {'Total_Encounters': value}
    with open(file_path, "w") as file:
        json.dump(data, file)

start_time = time.time()
data = {'SessionStart': format_time(0)} 


@app.route('/update_data', methods=['GET', 'POST'])
def update_data():
    global start_time

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

        # Update the 'data' dictionary
        data['highestAtkDef'] = highestAtkDef
        data['highestSpeSpc'] = highestSpeSpc
        data['item'] = item
        data['shinyvalue'] = shinyvalue
        data['species'] = species
        data['Attack'] = attack
        data['Defense'] = defense
        data['Speed'] = speed
        data['Special'] = special
        data['EncounterCount'] = change_count[0]
        data['SessionStart'] = format_time(elapsed_time)
        data['Total_Encounters'] = Total_Encounters[0]

        if 'atkdef' not in data or data['atkdef'] != atkdef:
            change_count[0] += 1  # Increment change count
            Total_Encounters[0] += 1
            data['atkdef'] = atkdef  # Update the 'data' dictionary

        
        write_variable_to_file(Total_Encounters[0])

        if data['shinyvalue'] == 1:
            message = "shiny encounter"
            payload = {'content': message}
            headers = {'Content-Type': 'application/json'}

            response = requests.post(webhook_url, json=payload, headers=headers)

            if response.status_code == 204:
                print("Message sent successfully")
            else:
                print(f"Failed to send message. Status code: {response.status_code}")

        if data['Attack'] == 15 and data['Defense'] == 15 and data['Speed'] == 15 and data['Special'] == 15:
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

@app.route('/species')
def species():
    # You can pass the 'species' data to the species.html template
    species_value = data.get('species', '')
    return render_template('species.html', data=data)

@app.route('/')
def index():
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
