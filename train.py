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

# Preprocess data with the new attribute 'Rating'
selected_columns = ['Price', 'Category', 'Language', 'Required Score', 'Rating', 'Numbers of Attendee']
filtered_data = data[selected_columns].copy()

# Handle missing or invalid ratings by replacing them with the mean rating
filtered_data.loc[:, 'Rating'] = filtered_data['Rating'].fillna(filtered_data['Rating'].mean())

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
filtered_data.loc[:, 'Predicted Number of Attendees'] = predictions

# Sort the data by predicted number of attendees in descending order
sorted_data = filtered_data.sort_values(by='Predicted Number of Attendees', ascending=False)

# Create an enhanced HTML report with better display
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
        h2, h3 {
            margin-top: 20px;
        }
        .highlight {
            background-color: #f9f9f9;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Course Attendance Prediction Report</h1>
    <h2>Model Performance</h2>
    <p>Mean Squared Error (MSE): {{ mse }}</p>
    <p>R² Score: {{ r2 }}</p>
    <h2>Top 10 Courses by Predicted Attendance</h2>
    <table>
        <tr>
            <th>Price</th>
            <th>Category</th>
            <th>Language</th>
            <th>Required Score</th>
            <th>Rating</th>
            <th>Predicted Number of Attendees</th>
        </tr>
        {% for index, row in top_courses.iterrows() %}
        <tr class="highlight" if loop.index % 2 == 0>
            <td>{{ row['Price'] }}</td>
            <td>{{ row['Category'] }}</td>
            <td>{{ row['Language'] }}</td>
            <td>{{ row['Required Score'] }}</td>
            <td>{{ row['Rating'] }}</td>
            <td>{{ row['Predicted Number of Attendees'] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Select the top 10 courses
top_courses = sorted_data.head(10)

# Render the HTML
template = Template(html_template)
html_content = template.render(mse=mse, r2=r2, top_courses=top_courses)

# Write the HTML to a file
with open('enhanced_course_attendance_report.html', 'w') as f:
    f.write(html_content)

print("Enhanced report generated: enhanced_course_attendance_report.html")
