import luigi
import luigi.contrib.s3
import json
from ingest.call_to_api import call_to_api
from raw_ingest_unittest import raw_unittest_task

class raw_task(luigi.Task):
	bucket = 'dpa-metro-raw'
	year = luigi.IntParameter()
	month = luigi.IntParameter()

	def requires(self):
		return raw_unittest_task(self.year,self.month)

	def run(self):
		cta = call_to_api()
		records = cta.get_information(self.year, self.month)

		with self.output().open('w') as output_file:
			json.dump(records, output_file)

	def output(self):
		output_path = "s3://{}/year={}/month={}/{}.json".\
		format(self.bucket, str(self.year), str(self.month).zfill(2), str(self.year)+str(self.month).zfill(2))
		return luigi.contrib.s3.S3Target(path=output_path)

if __name__ == '__main__':
	luigi.run()
