#  Import modules & dependencies

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#  Initializing database connection, integration

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

#  Establish Table References

Measurements = Base.classes.measurement
Station = Base.classes.station

#  Create a new session, then Flask

session = Session(engine)

app = Flask(__name__)

#  Setting Flask Routes

#  Index Route Response

@app.route("/")
def welcome():
    return (
        f"Welcome! You have reached the Hawaiian Weather API Resource <br/>"
        f" <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Step 1:  Use Session Method to connect Python to database
    session = Session(engine)

    # Step 2:  Session Query to pull in data for our dictionary (and subsequent JSON conversion)
    results = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date >= '2016-08-23').all()
    session.close()

    # Step 3:  Use Python List Comprehensions to load data into a dictionary object
    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precip.append(precip_dict)

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    #Query
    results = session.query(Station.station).all()
    session.close()

    #Converting list of tuples into normal list vai np.ravel method, then converting into JSON
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Next Query:  Dates and tobs of the most active station for the last year, identified in part 1
    results = session.query(Measurements.date, Measurements.tobs, Measurements.station).\
                            filter(Measurements.station == 'USC00519281').\
                            filter(Measurements.date >= '2016-08-17').all()
    session.close()

    temp_observations = []
    for entry in results:
        tobs_dict = {}
        tobs_dict[entry[0]] = entry[1]
        temp_observations.append(tobs_dict)

    return jsonify(temp_observations)
   

@app.route("/api/v1.0/<start>")
# Calculate TMin, TAvg, and TMax for all dates >= start date
def after(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    min_temp = session.query(func.min(Measurements.tobs)).filter(Measurements.date >= start).all()
    max_temp = session.query(func.max(Measurements.tobs)).filter(Measurements.date >= start).all()
    avg_temp = session.query(func.avg(Measurements.tobs)).filter(Measurements.date >= start).all()
    session.close()
    return(
        f"Minimum temp: {min_temp}<br/>"
        f"Maximum temp: {max_temp}<br/>"
        f"Average temp: {avg_temp}")

@app.route("/api/v1.0/<start>/<end>")
# Calculate TMin, TAvg, and TMax for all dates between start and end date
def between(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    min_temp = session.query(func.min(Measurements.tobs)).filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    max_temp = session.query(func.max(Measurements.tobs)).filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    avg_temp = session.query(func.avg(Measurements.tobs)).filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    session.close()
    return(
        f"Minimum temp: {min_temp}<br/>"
        f"Maximum temp: {max_temp}<br/>"
        f"Average temp: {avg_temp}")

if __name__ == "__main__":
    app.run(debug=True)