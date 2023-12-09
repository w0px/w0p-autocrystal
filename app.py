from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize data as an empty dictionary
data = {}

# Your other routes and functions go here

@app.route('/update_data', methods=['POST'])
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

        

        # print(data)  # This will print the updated data

        return 'Data received successfully'
    
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
