import luigi
import luigi.contrib.s3
import boto3
from cleaned_ingest_metadata import cleaned_task_metadata
from io import StringIO
import pandas as pd
import numpy as np
from math import floor

class label_task(luigi.Task):
	bucket = 'dpa-metro-label'
	year = luigi.IntParameter()
	month = luigi.IntParameter()
	station = luigi.Parameter()

	def requires(self):
		return cleaned_task_metadata(self.year,self.month,self.station)

	def run(self):
		line = "line"
		station = "station"
		year = "year"
		month = "month"
		influx = "influx"
		q3 = "percentile_0.75"
		q1 = "percentile_0.25"
		iqr = "iqr"
		min_range = "min_range"
		max_range = "max_range"
		prom = "mean"
		date = "date"

		ses = boto3.session.Session(profile_name='omar', region_name='us-east-1')
		s3_resource = ses.resource('s3')

		obj = s3_resource.Object("dpa-metro-cleaned","year={}/month={}/station={}/{}.csv".format(str(self.year),str(self.month).zfill(2),self.station,self.station.replace(' ', '')))
		print(ses)

		file_content = obj.get()['Body'].read().decode('utf-8')
		df = pd.read_csv(StringIO(file_content))

		df[year] = self.year
		df[month] = self.month
		df[station] = self.station

		n = floor(df.shape[0] * .7)
		df = df.sort_values(by = date, axis = 0)
		df = df[0:n]

		def percentile(n):
			def percentile_(x):
				return np.percentile(x, n)
			percentile_.__name__ = 'percentile_%s' % n
			return percentile_

		def get_statistics(df):
			return df.groupby([line, station]).agg([percentile(.25), percentile(.75), 'mean'])[influx].reset_index()

		def calculate_range(df):
			stats = get_statistics(df)
			stats[iqr] = stats[q3] - stats[q1] 
			stats[min_range] = stats[prom] - 1.5 * stats[iqr]
			stats[max_range] = stats[prom] + 1.5 * stats[iqr]
			stats = stats[[line, station, min_range, max_range]]
			return stats

		def join_range(df, stats):
			return df.merge(stats, on = [line, station], how = 'left')

		def create_label(df): 
			df["label"] = np.where(df[influx] <= df[min_range], 1, np.where(df[influx] <= df[max_range], 2, 3))
			return df

		final = create_label(join_range(df, calculate_range(df)))

		with self.output().open('w') as output_file:
			final.to_csv(output_file)

	def output(self):
		output_path = "s3://{}/year={}/month={}/station={}/{}.csv".\
		format(self.bucket,str(self.year),str(self.month).zfill(2),self.station,self.station.replace(' ', ''))
		return luigi.contrib.s3.S3Target(path=output_path)

if __name__ == "__main__":
	luigi.run()

