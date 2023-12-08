from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initialize data as an empty dictionary
data = {}

# Your other routes and functions go here

@app.route('/update_data', methods=['POST'])
def update_data():
    if request.method == 'POST':
        
        received_data = request.get_json()

        # Access individual values
        encounterCount = received_data.get('encounterCount')
        enemy_addr = received_data.get('enemy_addr')
        item = received_data.get('item')
        timeSinceLastShiny = received_data.get('timeSinceLastShiny')
        species = received_data.get('species')
        spespc = received_data.get('spespc')  # Add this line to get 'spespc'

        # Do something with the data (e.g., store in a database, update variables, etc.)

        # Update the 'data' dictionary
        data['encounterCount'] = encounterCount  # Use the value received from Lua
        data['enemy_addr'] = enemy_addr
        data['item'] = item
        data['timeSinceLastShiny'] = timeSinceLastShiny
        data['species'] = species
        data['spespc'] = spespc

        print(data)  # This will print the updated data

        return 'Data received successfully'

@app.route('/')
def index():
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
