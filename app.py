from flask import Flask, render_template, request
import json


app = Flask(__name__)

# Initialize data as an empty dictionary
data = {}

# Your other routes and functions go here

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initialize data as an empty dictionary
data = {}

# Your other routes and functions go here

from flask import Flask, request, jsonify

app = Flask(__name__)

# Your other routes and functions go here

@app.route('/update_data', methods=['POST'])
def update_data():
    if request.method == 'POST':
        # Get the concatenated data from the request payload
        concatenated_data = request.form.get('payload')

        # Split the concatenated data into individual values
        encounterCount, enemy_addr, item, lastShinyTime, species, spespc = map(int, concatenated_data.split(','))

        # Do something with the data (e.g., store in a database, update variables, etc.)

        # Update the 'data' dictionary
        data['encounterCount'] = encounterCount
        data['enemy_addr'] = enemy_addr
        data['item'] = item
        data['lastShinyTime'] = lastShinyTime
        data['species'] = species
        data['spespc'] = spespc

        print(data)  # This will print the updated data

        return 'Data received successfully'
        
@app.route('/')
def index():
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
