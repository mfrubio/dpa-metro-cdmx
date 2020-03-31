import requests
import luigi
import luigi.contrib.s3
import boto3
import s3fs
import json
import glob
import os

class data_acq_task(luigi.Task):
    bucket = 'dpa-metro'
    fecha = '08/11/2015'

    def run(self):
        ses = boto3.session.Session(profile_name='omar', region_name='us-east-1')
        s3_resource = ses.resource('s3')

        obj = s3_resource.Bucket(self.bucket)
        print(ses)

        api_url = "https://datos.cdmx.gob.mx/api/records/1.0/search/?dataset=afluencia-diaria-de-metrobus-cdmx&rows=-1&facet=" + self.fecha
        #api_url = "https://datos.cdmx.gob.mx/api/records/1.0/search/?dataset=afluencia-diaria-del-metro-cdmx&rows=10000&sort=-fecha&facet=ano&facet=linea&facet=estacion&refine.ano=" + self.year + "&refine.estacion=" + self.station
        r = requests.get(url = api_url)
        data = r.json()
        with self.output().open('w') as output_file:
        #with s3.open(f"{'metro-dpa-dacq'}/'dpa-test' + station+'_'+req_year.json", 'w') as outfile:
            json.dump(data, output_file)

    def output(self):
        output_path = "s3://{}/YEAR={}/STATION={}/test.json".\
        format(self.bucket,self.year,self.station)

        return luigi.contrib.s3.S3Target(path=output_path)

if __name__ == '__main__':
    luigi.run()
