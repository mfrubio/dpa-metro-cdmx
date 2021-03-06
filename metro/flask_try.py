from flask import Flask
from flask_restplus import Api, Resource
import pandas as pd
from io import StringIO
import json
import boto3

app = Flask(__name__)
api = Api(app)

@api.route("/date/<string:date>")
class GetPredictions(Resource):
    def get(self, date):
        year = date[:4]
        month = date[4:]

        ses = boto3.session.Session(profile_name='omar', region_name='us-east-1')
        s3_resource = ses.resource('s3')

        obj = s3_resource.Object("dpa-metro-predictions", "year={}/month={}/{}.csv".format(str(year), str(month).zfill(2), str(year)+str(month).zfill(2)))

        file_content = obj.get()['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(file_content))

        dfJson = df.to_json(orient='table')

        return dfJson
