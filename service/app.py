from flask import Flask, jsonify, request
from init_db import db, init_db
from models import Trips, Regions, db
from sqlalchemy import or_
from scripts import load_csv, default_initial_csv_path, group_trips_from_query, default_eps, default_min_samples

app = Flask(__name__)

init_db(app)

with app.app_context():
    db.create_all()


@app.route('/load-csv', methods=['POST'])
def load_csv_to_db():
    try:
        path = request.json.get('path', None)
        grouping = request.json.get('grouping', False) is True
        eps = request.json.get('path', default_eps)
        min_samples = request.json.get('grouping', default_min_samples)

        return load_csv(
            default_initial_csv_path if path is None else path,
            grouping,
            eps,
            min_samples
        )

    except Exception as e:
        print('Error', e)
        return jsonify({'message': 'Hubo un error cargar csv'}), 500


@app.route('/group-trips', methods=['POST'])
def group_trips():
    try:
        eps = request.json.get('eps', default_eps)
        min_samples = request.json.get('min_samples', default_min_samples)
        grouped_df = group_trips_from_query(eps, min_samples)

        all_trips = Trips.query
        for _, row in grouped_df.iterrows():
            trip = all_trips.filter_by(id=row['id']).first()
            trip.group_label = row['cluster']

        db.session.commit()

        return jsonify({'message': 'Trips succesfully grouped'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/weekly-average', methods=['POST'])
def weekly_average():
    """
    This function calculates the weekly average of trips inside a box
    returns a json with the total trips and the weekly average per region

    Returns:
        json: json with the total trips and the weekly average overall and per region 
    """
    try:
        # Gather data from request
        max_lat = request.json['max_lat']
        min_lat = request.json['min_lat']
        max_lon = request.json['max_lon']
        min_lon = request.json['min_lon']

        # Set minimums and maximums for proper filtering
        max_lat, min_lat = max(float(max_lat), float(
            min_lat)), min(float(max_lat), float(min_lat))
        max_lon, min_lon = max(float(max_lon), float(
            min_lon)), min(float(max_lon), float(min_lon))

        # Filter trips inside the box
        filtered_inside_box = Trips.query.filter(or_(
            (Trips.origin_latitude >= min_lat) &
            (Trips.origin_latitude <= max_lat) &
            (Trips.origin_longitude >= min_lon) &
            (Trips.origin_longitude <= max_lon),
            (Trips.destination_latitude >= min_lat) &
            (Trips.destination_latitude <= max_lat) &
            (Trips.destination_longitude >= min_lon) &
            (Trips.destination_longitude <= max_lon)
        ))

        regions = Regions.query.all()

        per_region_results = []
        for region in regions:
            weekly_average_trips = filtered_inside_box.filter(
                Trips.region == region.id).count() / 7
            per_region_results.append({
                'region': region.name,
                'weekly_average_trips': "{:.3f}".format(weekly_average_trips)
            })

        result = {
            'total_trips': filtered_inside_box.count(),
            'total_weekly_average': "{:.3f}".format(filtered_inside_box.count()/7),
            'region_weekly_average': per_region_results
        }

    except Exception as e:
        print('Error', e)
        return jsonify({'message': 'Hubo un error al calcular promedios semanales'}), 500

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
