import requests
import luigi
import luigi.contrib.s3
import json
from calendar import monthrange

class raw_task(luigi.Task):
	bucket = 'dpa-metro-raw'
	year = luigi.IntParameter()
	month = luigi.IntParameter()
	station = luigi.Parameter()

	def run(self):
		days_in_month = monthrange(self.year, self.month)[1]

		records = []
		for day in range(days_in_month):
			fecha = str(self.year)+"-"+str(self.month).zfill(2)+"-"+str(day+1).zfill(2)
			api_url = "https://datos.cdmx.gob.mx/api/records/1.0/search/?dataset=afluencia-diaria-del-metro-cdmx&sort=-fecha&facet=fecha&facet=linea&facet=estacion&refine.fecha="+fecha+"&refine.estacion="+self.station

			r = requests.get(url = api_url)
			data = r.json()

			for obs in data["records"]:
				records.append(obs["fields"])

		with self.output().open('w') as output_file:
			json.dump(records, output_file)

	def output(self):
		output_path = "s3://{}/year={}/month={}/station={}/{}.json".\
		format(self.bucket,str(self.year),str(self.month).zfill(2),self.station,self.station.replace(' ', ''))
		return luigi.contrib.s3.S3Target(path=output_path)

if __name__ == '__main__':
	luigi.run()
