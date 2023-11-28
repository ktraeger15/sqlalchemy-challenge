# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from statistics import mean

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to Climate App Homepage <br/><br/>"
        f"Available Routes: <br/>"
        f"precipitation <br/> stations <br/> tobs <br/> <start> <br/> <start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find the most recent date in the data set.
    #source: https://stackoverflow.com/questions/20937866/sqlalchemy-get-the-object-with-the-most-recent-date
    date_most_recent = session.query(measurement.date).order_by(desc('date')).first()
    
    #Calculate one year after most recent date for filer 
    #Source: https://www.itsolutionstuff.com/post/how-to-subtract-year-to-date-in-pythonexample.html
    date = datetime.strptime(date_most_recent[0], "%Y-%m-%d")
    year_diff = str((date - relativedelta(years=1)).date())

    #Query for date and precipitation with filter for one year after most recent date
    #Source for statment attribute: https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.statement
    date_and_prcp = (session.query(measurement.date, measurement.prcp)).filter(measurement.date > year_diff).all()
    all_data = []
    for date, prcp in date_and_prcp:
       date_prcp_dict = {}
       date_prcp_dict[date] = prcp
       all_data.append(date_prcp_dict)
   
    return jsonify(all_data)
   
    
@app.route("/api/v1.0/stations")
def stations():
    
    station_list = []
    stations = session.query(station.station).all()
    #for loop to fill in station list in correct format
    for item in stations:
        station_list.append(item[0])
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
     # Find the most recent date in the data set.
    #source: https://stackoverflow.com/questions/20937866/sqlalchemy-get-the-object-with-the-most-recent-date
    date_most_recent = session.query(measurement.date).order_by(desc('date')).first()
    
    #Calculate one year after most recent date for filer 
    #Source: https://www.itsolutionstuff.com/post/how-to-subtract-year-to-date-in-pythonexample.html
    date = datetime.strptime(date_most_recent[0], "%Y-%m-%d")
    year_diff = str((date - relativedelta(years=1)).date())

    
    #query to count and group stations
    query = sqlalchemy.select([measurement.station,sqlalchemy.\
                           func.count(measurement.station)])\
                           .group_by(measurement.station)

    most_active_stations = engine.execute(query).fetchall()
    #lambda function to sort by second element in the inner lists
    most_active_stations.sort(reverse = True, key=lambda x: x[1])
    
    #saves most active station id from previous list
    most_active_station_id = most_active_stations[0][0]

    #query with filter for temperatures from most active station 
    temps_from_most_active_station = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.station== most_active_station_id)\
        .filter(measurement.date>year_diff).all()
    temps_from_most_active_station = [tuple(row) for row in temps_from_most_active_station]
    
    return jsonify(temps_from_most_active_station)

@app.route("/api/v1.0/<start>")
def start(start):
    temp_list = []
     #query with start date filter
    temps = session.query(measurement.tobs).filter(measurement.date>=start).all()
    #for loop to fill in temp_list in correct format
    for temp in temps:
        temp_list.append(temp[0])
    
    output_list = [min(temp_list), mean(temp_list) , max(temp_list)]
    
    return jsonify(output_list)


@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start,end):
    temp_list = []
    #query with start and end date filters
    temps = session.query(measurement.tobs).filter(measurement.date>=start).filter(measurement.date<=end).all()
    #for loop to fill in temp_list in correct format
    for temp in temps:
        temp_list.append(temp[0])
    
    output_list = [min(temp_list), mean(temp_list) , max(temp_list)]
    
    return jsonify(output_list)
    
if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    