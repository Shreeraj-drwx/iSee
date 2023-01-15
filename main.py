import PySimpleGUI as sg
import time
from seeed_dht import DHT
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from math import radians, sin, cos, sqrt, atan2

top_10_index = 0

def main():

    global top_10_index

    sg.theme('DarkAmber')
    
    layout = [
        [sg.Text("Temperature: ", font=("Helvetica", 12)), sg.Text("", key="-TEMP-", font=("Helvetica", 12))],
        [sg.Text("Humidity: ", font=("Helvetica", 12)), sg.Text("", key="-HUMI-", font=("Helvetica", 12))],
        [sg.Text("Condition: ", font=("Helvetica", 12)), sg.Text("", key="-COND-", font=("Helvetica", 12))],
        [sg.Text("Compatible Pair: ", font=("Helvetica", 12)), sg.Multiline("", key="-PAIR-", font=("Helvetica", 12), size=(20, 3))],
        [sg.Button("Next Pair", font=("Helvetica", 12)), sg.Exit(font=("Helvetica", 12))]
    ]
    
    window = sg.Window("Temperature and Humidity", layout, size=(480, 320))
    
    # Loading the dataframe
    data = pd.read_csv("data.csv")

    # Extracting the features (X) and labels (y)
    X = data[['donor_time_remaining','donor_latitude','donor_longitude','receiver_time_remaining','receiver_latitude','receiver_longitude']]

    # Function to calculate the distance between two points (latitude, longitude) on the Earth
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    # Finding the distance between every pair of donors and receivers
    data["distance"] = data.apply(lambda row: haversine_distance(row["donor_latitude"], row["donor_longitude"], row["receiver_latitude"], row["receiver_longitude"]), axis=1)

    # Sorting the donor and receiver pairs based on their distances
    data = data.sort_values("distance")

    # Add the match label
    data["match"] = (data["donor_time_remaining"] > data["receiver_time_remaining"]).astype(int)

    # splitting the dataset into training and testing sets
    data["distance"] = data.apply(lambda x: haversine_distance(x["donor_latitude"],x["donor_longitude"],x["receiver_latitude"],x["receiver_longitude"]), axis=1)
    X = data[['donor_time_remaining','distance']]

    # load the model
    clf = joblib.load('final_trained_model.pkl')

    # Use the trained model to predict the compatibility of each pair
    compatible_scores = clf.predict_proba(data[['donor_time_remaining','distance']])[:,1]

    # Create a new column in the data DataFrame to hold the compatibility scores
    data['compatible_score'] = compatible_scores

    # Sort the data by the compatibility score and distance
    data = data.sort_values(by=['compatible_score','distance'],ascending=[False,True])

    # Get the top 10 compatible pairs
    top_10_compatible_pairs = data.head(10)

    # Grove - Temperature&Humidity Sensor connected to port D5
    sensor = DHT('11', 5)

    threshold_lower = 16
    threshold_higher = 24

    while True:
        humi, temp = sensor.read()
        condition = 'Stable'
        if temp <= threshold_higher and temp >= threshold_lower:
            conditon = 'Stable'
        #-2 and +2 done to have the temperature 2 C above and below good temperature
        elif temp <= threshold_higher + 2 and temp >= threshold_lower - 2:
            condition = 'Slightly Unstable'
        else:
            condition = 'Severely Unstable'
        
        event, values = window.read(timeout=1000)
        
        window["-TEMP-"].update(str(temp) + 'C')
        window["-HUMI-"].update(str(humi) + '%')
        window["-COND-"].update(condition)
        window["-PAIR-"].update(top_10_compatible_pairs.iloc[top_10_index]['donor_name'] + ' is ' + str(round(top_10_compatible_pairs.iloc[top_10_index]['distance'], 1)) + ' Km far away from ' + top_10_compatible_pairs.iloc[top_10_index]['receiver_name'])

        if event == "Next Pair":
            top_10_index = (top_10_index + 1) % top_10_compatible_pairs.shape[0]

        if event in (None, "Exit"):
            break

    window.refresh()
    window.close()

if __name__ == '__main__':
    main()
