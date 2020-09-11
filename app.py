import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# session.query(station.station).all()
# station_activ = session.query(measurement.station, func.count(measurement.station))\
#     .group_by(measurement.station)\
#     .order_by(func.count(measurement.station).desc()).all()
# station_activ
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Weather Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def weatherPrecipitation():
    """Fetch the precipitation table data from the database"""
    prcp = session.query(measurement.date,measurement.prcp).all()
    test = [{row[0]:row[1]}for row in prcp]
    return jsonify(test)

@app.route("/api/v1.0/stations")
def weatherStations():
    stats = {'stations':[stat[0] for stat in session.query(measurement.station)]}
    return jsonify(stats)

@app.route("/api/v1.0/tobs")
def weatherTobs():
    most_recent = session.query(measurement.date).order_by(measurement.id.desc()).first()[0]
    query_date = dt.datetime.strptime(most_recent, '%Y-%m-%d') - dt.timedelta(days=365)
    tobs = session.query(measurement.date,measurement.tobs).filter(measurement.date >= query_date)\
    .filter(measurement.date <= most_recent).all()
    tobs_dict = [{row[0]:row[1]} for row in tobs]
    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date = '0'):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    if end_date == '0':
        end_date = session.query(measurement.date).order_by(measurement.id.desc()).first()[0]
    temps = (session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all())
    temps_dict =  [{row[0]:[{'TMIN':row[1]},{'TAVG':row[2]},{'TMAX':row[3]}]} for row in temps]
    if temps_dict is None:
        return 'Not found', 404
    return jsonify(temps_dict)



if __name__ == "__main__":
    app.run(debug=True)
