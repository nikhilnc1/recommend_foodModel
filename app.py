from typing import List
from fastapi import FastAPI, Form
from pydantic import BaseModel
import requests
import pandas as pd

app = FastAPI()

# Load ratings data from Firebase
def load_data_from_firebase(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to fetch data from {url}")

ratings = load_data_from_firebase('https://intellicater-default-rtdb.firebaseio.com/Ratings.json')

# Create DataFrame from ratings data
df = pd.DataFrame(columns=['userID', 'itemID', 'rating'])
for user, items in ratings.items():
    for item, rating in items.items():
        df.loc[len(df)] = {'userID': user, 'itemID': item, 'rating': rating}

def collaborative_filtering_recommendation(data, user_id, num_recommendations=4):
    user_data = data[data['userID'] == user_id]
    user_items = list(user_data['itemID'])

    # Filter out items already rated by the user
    available_items = data[~data['itemID'].isin(user_items)]

    # Group by itemID and compute the mean rating
    item_ratings = available_items.groupby('itemID')['rating'].mean().reset_index()

    # Sort the items based on the mean rating
    top_items = item_ratings.sort_values(by='rating', ascending=False).head(num_recommendations)

    return top_items['itemID']

def hybrid_recommendation(data, user_id, num_recommendations=10):
    collaborative_filtering = collaborative_filtering_recommendation(data, user_id, num_recommendations)
    return collaborative_filtering

def recommend(userid):
    recommended_items = hybrid_recommendation(df, userid)
    return recommended_items

@app.post("/recommendation")
def recommendation(userID: str = Form(...)):
    recommended_items = recommend(userID)
    return {"menu": recommended_items}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
