
import datetime as dt

import numpy as np
import pandas as pd
import sqlalchemy
from flask import Flask, jsonify, url_for
from sqlalchemy import Column, Float, Integer, String, create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

print("Welcome to Kim's Flask app")


#create engine
engine = create_engine("sqlite:///hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
print(Base.classes.keys())
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# View measurement table
first_row = session.query(Measurement).first()
first_row.__dict__

##
session.query(Measurement, Measurement.date).order_by(Measurement.date.desc()).first()


# Design a query to retrieve the last 12 months of precipitation data.
conn = engine.connect()
read_df=pd.read_sql("select * from measurement where date between '2016-08-23' and '2017-08-23' order by date ",conn)

#Select only the date and prcp values.
meas_df = read_df[["date", "prcp"]]
meas_chart = meas_df.set_index("date")

#Sort the DataFrame values by date.
meas_chart = meas_chart.sort_values(["date"], ascending=True)

#Gather the Station Data
stat=pd.read_sql("select * from measurement where date between '2016-08-23' and '2017-08-23' order by id desc ",conn)
stat_df = pd.DataFrame(stat)

#Design a query to calculate the total number of stations.
numstat_df = stat_df.groupby("station").count()

county = numstat_df["id"].count()

totcount_df = stat_df.groupby("station").count()["id"].reset_index()
totcount_df = totcount_df.sort_values(["id"], ascending=False)
totcount_df = totcount_df.rename(columns={"id": "total count"})

# 	Which station has the highest number of observations?
totcount_df['total count'].max()

tobs_df = stat_df[["station", "tobs"]]

app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""

    return (

        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start - 01/01/2015<br/>"
        f"/api/v1.0/start/end - 08/23/2016 - 08/23/2017"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")

# Return a JSON list of stations from the dataset.

def stations():
 

     #Query for the stations
     stations = session.query(Station.station, Station.name).all()

     return jsonify(stations)


# Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")

def tobs():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and temperatures for the last year
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).all()

    # Dict with date as the key and tobs as the value
    tobs = {date: tobs for date, tobs in tobs}
    return jsonify(tobs)


#  Return a JSON list of the minimum temperature, the average temperature,
#  and the max temperature for a given start AND start-end range.
@app.route("/api/v1.0/start - 01/01/2015")
def start():

    start_year = dt.date(2015, 1, 1)

    start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_year).all()


    return jsonify(start)


@app.route("/api/v1.0/start/end - 08/23/2016 - 08/23/2017")


def startend():

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    startend = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= prev_year).all()

   
    return jsonify(startend)


if __name__ == '__main__':
    app.run(debug=True)
