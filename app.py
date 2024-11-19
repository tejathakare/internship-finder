from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

def load_data():
    try:
        # Read CSV with latin1 encoding and handle empty values
        df = pd.read_csv('Giinius Internship Organizers Directory.csv', encoding='latin1')
        df = df.fillna('')  # Replace NaN with empty strings
        
        # Keep only the needed columns
        needed_columns = ['Program', 'Focus Area', 'Application Deadline', 
                         'Program Start Date', 'Age/Grade/Qualification', 'State']
        df = df[needed_columns]
        
        print(f"Successfully loaded {len(df)} internship records")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
data = load_data()

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/search", methods=["GET"])
def search():
    try:
        search_term = request.args.get("search", "").lower()
        focus_area = request.args.get("focus_area", "").lower()
        state = request.args.get("state", "").lower()

        filtered_data = data.copy()

        # Apply filters
        if search_term:
            filtered_data = filtered_data[
                filtered_data.apply(lambda x: x.astype(str).str.lower().str.contains(search_term, na=False)).any(axis=1)
            ]
        if focus_area:
            # Handle multiple focus areas (comma-separated)
            focus_areas = focus_area.split(',')
            focus_area_filter = filtered_data['Focus Area'].str.lower().str.contains('|'.join(focus_areas), na=False)
            filtered_data = filtered_data[focus_area_filter]
        if state:
            # Handle multiple states (comma-separated)
            states = state.split(',')
            state_filter = filtered_data['State'].str.lower().str.contains('|'.join(states), na=False)
            filtered_data = filtered_data[state_filter]

        # Convert to list of dictionaries and handle NaN values
        result = filtered_data.replace({pd.NA: '', float('nan'): ''}).to_dict(orient='records')
        return jsonify(result)

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify([])

@app.route("/filters")
def get_filters():
    try:
        focus_areas = sorted(data['Focus Area'].dropna().unique().tolist())
        states = sorted(data['State'].dropna().unique().tolist())
        
        # Replace any NaN values with empty strings
        focus_areas = ['' if pd.isna(x) else x for x in focus_areas]
        states = ['' if pd.isna(x) else x for x in states]
        
        return jsonify({
            "focus_areas": focus_areas,
            "states": states
        })
    except Exception as e:
        print(f"Filter error: {e}")
        return jsonify({"focus_areas": [], "states": []})

if __name__ == "__main__":
    app.run(debug=True)