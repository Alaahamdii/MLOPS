from pymongo import MongoClient
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from jinja2 import Template
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['Courzello_DB']
courses_collection = db['Course']

# Function to fetch data from MongoDB
def fetch_data_from_mongodb():
    data = list(courses_collection.find({}))
    return pd.DataFrame(data)

# Fetch data
data = fetch_data_from_mongodb()

# Preprocess data similar to your CSV approach
selected_columns = ['Price', 'Category', 'Language', 'Required Score', 'Numbers of Attendee']
filtered_data = data[selected_columns]

# One-hot encode categorical features
encoded_data = pd.get_dummies(filtered_data.drop(columns=['Numbers of Attendee']), columns=['Category', 'Language'])

# Define features and target variable
X = encoded_data
y = filtered_data['Numbers of Attendee']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train a Random Forest Regressor
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Make predictions on the entire dataset
predictions = model.predict(X)

# Calculate regression metrics
mse = mean_squared_error(y, predictions)
r2 = r2_score(y, predictions)

# Add predictions to the original data
filtered_data['Predicted Number of Attendees'] = predictions

# Group the data by category
grouped_data = filtered_data.groupby('Category')

# Create an HTML report
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Course Attendance Prediction Report</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        h2 {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Course Attendance Prediction Report</h1>
    <h2>Model Performance</h2>
    <p>Mean Squared Error (MSE): {{ mse }}</p>
    <p>R² Score: {{ r2 }}</p>
    <h2>Top Courses by Category</h2>
    {% for category, courses in grouped_data.items() %}
    <h3>Category: {{ category }}</h3>
    <table>
        <tr>
            <th>Price</th>
            <th>Language</th>
            <th>Required Score</th>
            <th>Predicted Number of Attendees</th>
        </tr>
        {% for index, row in courses.iterrows() %}
        <tr>
            <td>{{ row['Price'] }}</td>
            <td>{{ row['Language'] }}</td>
            <td>{{ row['Required Score'] }}</td>
            <td>{{ row['Predicted Number of Attendees'] }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endfor %}
</body>
</html>
"""

# Render the HTML
grouped_data_dict = {category: group for category, group in grouped_data}
template = Template(html_template)
html_content = template.render(mse=mse, r2=r2, grouped_data=grouped_data_dict)

# Write the HTML to a file
with open('course_attendance_report.html', 'w') as f:
    f.write(html_content)

print("Report generated: course_attendance_report.html")
