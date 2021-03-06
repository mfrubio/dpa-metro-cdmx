import luigi
import luigi.contrib.s3
import boto3
from prelabel_creation_unittest import prelabel_unittest_task
from io import StringIO
import pandas as pd
from math import floor
from train.interquartile_range import interquartile_range
from datetime import datetime
from dateutil.relativedelta import *
from calendar import monthrange

class prelabel_task(luigi.Task):
	bucket = 'dpa-metro-prelabel'
	year = luigi.IntParameter()
	month = luigi.IntParameter()

	def requires(self):
		return prelabel_unittest_task(self.year,self.month)

	def run(self):
		def months_of_history(year, month):
			day = monthrange(year, month)[1]
			d1 = datetime(year, month, day)
			return (d1.year - 2016) * 12 + d1.month

		cut_date = floor(months_of_history(self.year, self.month) * .7)

		ses = boto3.session.Session(profile_name='omar', region_name='us-east-1')
		s3_resource = ses.resource('s3')

		df = pd.DataFrame()
		for i in range(cut_date):
			reference_date = datetime(2016, 1, 1) + relativedelta(months=i)
			obj = s3_resource.Object("dpa-metro-cleaned", "year={}/month={}/{}.csv".format(str(reference_date.year), str(reference_date.month).zfill(2), str(reference_date.year)+str(reference_date.month).zfill(2)))

			file_content = obj.get()['Body'].read().decode('utf-8')
			aux = pd.read_csv(StringIO(file_content))

			df = pd.concat([df, aux])

		intquar_ran = interquartile_range()
		final = intquar_ran.calculate_range(df)

		with self.output().open('w') as output_file:
			final.to_csv(output_file)

	def output(self):
		output_path = "s3://{}/year={}/month={}/{}.csv".\
		format(self.bucket,str(self.year),str(self.month).zfill(2),str(self.year)+str(self.month).zfill(2))
		return luigi.contrib.s3.S3Target(path=output_path)

if __name__ == "__main__":
	luigi.run()

