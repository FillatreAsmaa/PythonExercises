# -*- coding: utf-8 -*-

import web # Import the library web to create the web service
import pandas as pd # import the library pandas
import json # import the library json for JSON files
from GeoBases import GeoBase # import GeoBase to retrieve airport countries

# Columns names and filenames
filenameBooking="bookings.csv" # name of the bookings file
usedColumns = ['arr_port','pax'] # columns used to process the file

geo_o = GeoBase(data='ori_por', verbose=False) # load the GeoBase data

# Create a function that retrieves the country name from the airport code
# If the airport code is unknown, it returns the default value "UNKNOWN"
# I use the strip function to remove whitespaces in airport codes (otherwise, no airport code is recognized)
def strCountryName(x):
    return geo_o.get(x.strip(), 'city_name_ascii',default='UNKNOWN')
    
# Define the function that writes the JSON file
def writeJsonFile(topNumber,filenameJSON):
    # read the CSV file, keeping only columns 'arr_port' and'pax'
    df = pd.read_csv(filenameBooking,sep='^', usecols=usedColumns, nrows=1000) 
    dfTop=df['pax'].groupby(df['arr_port']).sum().reset_index().sort_values(by='pax', ascending=False)[:topNumber]
        
    dfTop['Rank']=range(1,topNumber+1,1) # Generate integers up to topNumber+1, but not including topNumber+1
    dfTop = dfTop.reindex(columns=['Rank','arr_port','pax'])
    dfTopJSON=dfTop.rename(columns={'arr_port': 'Airport','pax': 'Number of bookings'})
        
    # I "map" the function 'strCountryName' to each row of the column 'Airport' to create a new column named 'Country'       
    dfTopJSON['Country']=dfTopJSON['Airport'].map(strCountryName)    

    # Write the data inside a json file        
    jsonData = dfTopJSON.to_json(path_or_buf=filenameJSON, orient='columns') 


# Define the url coding    
urls = (
    '/top/(.*)', 'get_top'
)

app = web.application(urls, globals())
      
# number is the number of tops to return     
class get_top:
    def GET(self, number):
        topNumber=int(float(number)) # number of tops I retrieve (cast to float and integer to process number like 2.3)
        # If negative or null value, return an information to user       
        if topNumber <= 0: 
            return "Requested number of top is negative or null! Please retry."
        filenameJSON = "top"+str(topNumber)+".json" # name of the JSON file
        writeJsonFile(topNumber,filenameJSON) # write the JSON file
        web.header('Content-Type', 'application/json') # Precise the content type of the returned data
        json_data=open(filenameJSON) # Open the json file
        data = json.load(json_data) # Read the data inside the json file
        return json.dumps(data) # Return the JSON content
        
# Launch the webservice
if __name__ == "__main__":
    app.run()    