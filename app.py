from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
change_count = [0]

# Initialize data as an empty dictionary
data = {}



@app.route('/update_data', methods=['GET', 'POST'])
def update_data():
    if request.method == 'POST':
        # Get the concatenated data from the request payload
        concatenated_data = request.form.get('payload')

        # Split the concatenated data into individual values
        highestAtkDef, highestSpeSpc, item, shinyvalue, species, spespc, atkdef = map(int, concatenated_data.split(','))

        # Do something with the data (e.g., store in a database, update variables, etc.)
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

        # Check if atkdef has changed
        if 'atkdef' not in data or data['atkdef'] != atkdef:
            change_count[0] += 1  # Increment change count
            data['atkdef'] = atkdef  # Update the 'data' dictionary

        return 'Data received successfully'

    elif request.method == 'GET':
        # You can modify this logic to return the data in a format suitable for your JavaScript
        return jsonify(data)

    
#route to handle the 'species' value
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
