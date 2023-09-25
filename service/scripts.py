import pandas as pd
from flask import jsonify
from models import db, Trips, Regions

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def format_dataframe(df):
    """
    This function formats the dataframe to be loaded into the database.
    Currently the accepted input for a coordinate is a POINT (longitude latitude) type.
    Here we separate both values and format them to have 7 decimal places.
    Also we add a column with the time of day in minutes.

    Parameters:
        df (pd.DataFrame): dataframe to format
    Returns:
        df (pd.DataFrame): formatted dataframe
    """
    df[['origin_longitude', 'origin_latitude']
       ] = df['origin_coord'].str.extract(r'POINT \((.*?) (.*?)\)')
    df[['destination_longitude', 'destination_latitude']
       ] = df['destination_coord'].str.extract(r'POINT \((.*?) (.*?)\)')

    df['time_of_day_minutes'] = df['datetime'].dt.hour * \
        60 + df['datetime'].dt.minute

    df['origin_longitude'] = df['origin_longitude'].apply(
        lambda x: f'{float(x):.7f}')
    df['origin_latitude'] = df['origin_latitude'].apply(
        lambda x: f'{float(x):.7f}')
    df['destination_longitude'] = df['destination_longitude'].apply(
        lambda x: f'{float(x):.7f}')
    df['destination_latitude'] = df['destination_latitude'].apply(
        lambda x: f'{float(x):.7f}')

    return df


default_eps = 0.5
default_min_samples = 10


def group_trips_from_df(df, eps, min_samples) -> pd.DataFrame:
    """
    This function uses DBSCAN to group the trips in the dataframe.

    Parameters:
        df (pd.DataFrame): dataframe to group
        eps (float): eps value for DBSCAN
        min_samples (int): min_samples value for DBSCAN
    Returns:
        df (pd.DataFrame): dataframe with the cluster column included
    """

    X = df[['origin_latitude', 'origin_longitude',
            'destination_latitude', 'destination_longitude', 'time_of_day_minutes']]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(X_scaled)

    df['cluster'] = clusters

    return df


def group_trips_from_query(eps, min_samples) -> pd.DataFrame:
    """
    This function uses DBSCAN to group the trips using a query as the origin.

    Parameters:
        eps (float): eps value for DBSCAN
        min_samples (int): min_samples value for DBSCAN
    Returns:
        df (pd.DataFrame): dataframe with the cluster column included
    """

    query = 'Select id, origin_latitude, origin_longitude, destination_latitude, destination_longitude, datetime from trips'
    X = pd.read_sql(query, db.engine)

    X['time_of_day_minutes'] = X['datetime'].dt.hour * \
        60 + X['datetime'].dt.minute

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X[[
        'origin_latitude',
        'origin_longitude',
        'destination_latitude',
        'destination_longitude',
        'time_of_day_minutes'
    ]])

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(X_scaled)

    X['cluster'] = clusters

    return X


default_initial_csv_path = "initial_data/trips.csv"


def load_csv(path, grouping=False, *args, **kwargs):
    """
    This function loads the csv file into the database
    Parameters:
        path (str): path to the csv file
    Returns:
        result (json): json with the status of the operation
    """
    eps = kwargs.get('eps', default_eps)
    min_samples = kwargs.get('min_samples', default_min_samples)

    try:
        df = pd.read_csv(path, parse_dates=['datetime'])

        df = format_dataframe(df)

        if grouping:
            df = group_trips_from_df(df, eps, min_samples)

        for _, row in df.iterrows():
            region = Regions.query.filter_by(name=row['region']).first()

            if region is None:
                region = Regions(name=row['region'])
                db.session.add(region)
                db.session.flush()

            group_value = row['cluster'] if grouping else None

            trip = Trips(
                region=region.id,
                origin_longitude=row['origin_longitude'],
                origin_latitude=row['origin_latitude'],
                destination_longitude=row['destination_longitude'],
                destination_latitude=row['destination_latitude'],
                datetime=row['datetime'],
                datasource=row['datasource'],
                group_label=group_value,
            )

            db.session.add(trip)

        db.session.commit()

        return jsonify({'message': 'CSV data successfully loaded into the database'}), 200

    except Exception as e:
        print('Error!!', e)
        return jsonify({'error': str(e)}), 500
