# Importing necessary libraries.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Setting up the connection to the SQLite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflecting the existing database into a new model.
Base = automap_base()

# Reflecting the tables from the database.
Base.prepare(autoload_with=engine)

# Saving references to each table in the database.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creating a session to interact with the database.
session = Session(engine)

# Setting up the Flask application.
app = Flask(__name__)

# Defining the routes for the Flask application.

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Endpoints:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>Provide 'start' and/or 'end' dates in the format MMDDYYYY for temperature statistics.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year."""
    # Calculating the date one year ago from the last date in the database.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Querying for the date and precipitation for the last year.
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Closing the session.
    session.close()

    # Creating a dictionary with date as the key and precipitation as the value.
    precip_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of weather stations."""
    # Querying and unraveling the results into a 1D array.
    station_results = session.query(Station.station).all()

    # Closing the session.
    session.close()

    # Converting the 1D array to a list.
    station_list = list(np.ravel(station_results))
    return jsonify(stations=station_list)

@app.route("/api/v1.0/tobs")
def temperature_monthly():
    """Return temperature observations (tobs) for the previous year."""
    # Calculating the date one year ago from the last date in the database.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Querying the primary station for all temperature observations from the last year.
    temperature_results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # Closing the session.
    session.close()

    # Unraveling the temperature results into a 1D array and converting to a list.
    temperature_list = list(np.ravel(temperature_results))

    # Returning the temperature results.
    return jsonify(temps=temperature_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temperature_stats(start=None, end=None):
    """Return minimum, average, and maximum temperatures."""
    # Selecting statements for minimum, average, and maximum temperatures.
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Parsing the start date and calculating temperature statistics for dates greater than start.
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start_date).all()

        # Closing the session.
        session.close()

        # Unraveling results into a 1D array and converting to a list.
        temperature_stats_list = list(np.ravel(results))
        return jsonify(temps=temperature_stats_list)

    # Parsing start and end dates, and calculating temperature statistics for the specified range.
    start_date = dt.datetime.strptime(start, "%m%d%Y")
    end_date = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*sel).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    # Closing the session.
    session.close()

    # Unraveling results into a 1D array and converting to a list.
    temperature_stats_list = list(np.ravel(results))
    return jsonify(temps=temperature_stats_list)

# Running the Flask application if the script is executed.
if __name__ == '__main__':
    app.run()
