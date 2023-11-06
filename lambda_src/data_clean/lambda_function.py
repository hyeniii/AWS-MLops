import pandas as pd
import geolocate as gl
import aws_utils as au
import configparser
from io import BytesIO, StringIO
import logging
import json
import yaml
import traceback

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def apply_reverse_geocode(row):
    try:
        if pd.isnull(row['cityname']) or pd.isnull(row['state']):
            row['cityname'], row['state'] = gl.reverse_geocode(row['latitude'], row['longitude'])
        return row
    except Exception as e:
        logger.error(f"Error in reverse geocoding: {e}", exc_info=True)
        return row

def lambda_handler(event, context):
    try:
        ############### DATA CLEAN ###############
        ## load configs ##
        config = configparser.ConfigParser()
        # Read the config.ini file
        config.read('config.ini')

        with open('data_clean_config.yaml', 'r') as file:
            dc_config = yaml.safe_load(file)

        ## connect to s3
        s3 = au.s3_client(config)
        logger.info("Connected to s3...")
        ### LOAD DATA ###
        fn1 = au.s3_get_obj(s3, config, dc_config['s3']['raw_data'])
        fn2 = au.s3_get_obj(s3, config, dc_config['s3']['raw_data2'])
        logger.info("Retrieved raw data...")

        df = pd.read_csv(StringIO(fn1['Body'].read().decode('ISO-8859-1')), sep=';', dtype={'address': str})
        df2 = pd.read_csv(StringIO(fn2['Body'].read().decode('ISO-8859-1')), sep=';',dtype={'address': str})
        # merge 2 datasets
        df = pd.concat([df, df2], ignore_index=True, axis=0)
        logger.info("Columns in the dataframe: %s", df.columns.tolist())

        ### DATA CLEANING ###
        # drop unncessary columns
        logger.info("Starting data cleaning...")
        df = df.drop(columns=dc_config['dc']['drop_columns'])

        # drop rows with no long, lat & no price (response var)
        df = df[~(df['latitude'].isna() & df['longitude'].isna())]
        df= df[~df['price'].isna()]

        # split str to list of amenities
        df.amenities = df.amenities.apply(lambda x: x.split(',') if pd.notna(x) else [])
        logger.info("Finished data cleaning...")
        ### IMPUTE DATA ###
        ## IMPUTE cityname & state ##
        # rows where 'cityname' or 'state' is null
        rows_to_geocode = df[df['cityname'].isnull() | df['state'].isnull()]
        # apply the reverse_geocode function to the filtered df
        geocoded_rows = rows_to_geocode.apply(apply_reverse_geocode, axis=1)
        # update DataFrame with the geocoded information
        df.update(geocoded_rows)

        ## IMPUTE bedroom & bathroom ##
        df['square_feet_group'] = (df['square_feet'] // 100).astype(int)
        # impute with average bed/bath in sq_feet groups
        sq_means = df.groupby('square_feet_group')[['bedrooms', 'bathrooms']].transform("mean")
        df['bedrooms'].fillna(sq_means['bedrooms'], inplace=True)
        df['bathrooms'].fillna(sq_means['bathrooms'], inplace=True)
        # remaining bathrooms - impute with average bedroom
        bd_means = df.groupby('bedrooms')[['bathrooms']].transform("mean")
        df['bathrooms'].fillna(round(bd_means['bathrooms'],0), inplace=True)

        ## IMPUTE pets_allowed ##
        df['pets_allowed'] = df['pets_allowed'].fillna("None")
        df['pets_allowed'].replace("Cats,Dogs,None", "None", inplace=True)
        logger.info("Finished imputing data...")
        ############### FEATURE ENGINEERING ##################

        # convert to number of amenities
        df['n_amenities'] = df.amenities.apply(len)
        # drop amentities list
        df = df.drop(columns=['amenities'])

        df['price_per_sq_feet'] = df.price / df.square_feet
        logger.info("Finished feature engieering...")
        ############### SAVE DATA TO S3 ###############
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        _ = au.s3_upload(s3, config, dc_config['s3']['clean_data'], csv_buffer.getvalue())

        return {
                'statusCode': 200,
                'body': json.dumps('Data cleaning and upload completed successfully.')
                }
    except Exception as e:
        # Log the exception
        tb_info = traceback.extract_tb(e.__traceback__)
        # Usually, the last call would be the cause of the error
        filename, line, func, text = tb_info[-1]
        error_message = f"An error occurred: {e} in file {filename} at line {line}"
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }

# ans = lambda_handler(0,0)
# print(ans)