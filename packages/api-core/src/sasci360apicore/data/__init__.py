#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import json
import logging
import os
import pandas
import saspy
from pathlib import Path
from typing import Optional


class Data:
	"""

	"""

	def __init__(self) -> None:
		self.logger = logging.getLogger(__name__)

	def create_csv(self, **kwargs) -> None:
		"""
		Read unzipped file line-by-line, replace delimiter and output csv file
		:keyword in_file: file, required -
		:keyword out_file: file, required -
		:keyword in_delimiter: str, required -
		:keyword out_delimiter: str, required -
		:keyword is_header: bool, required -
		:return: None
		"""
		result = None
		error = 0
		error_msg = ""
		try:
			in_file = kwargs["in_file"]
			out_file = kwargs["out_file"]
			in_delimiter = kwargs["in_delimiter"]
			out_delimiter = kwargs["out_delimiter"]
			is_header = kwargs["is_header"]

			with open(file=in_file, mode="r", encoding="utf8") as in_f, open(file=out_file, mode="a", encoding="utf8") as out_f:
				rows = 0
				for line in in_f:
					# print column header line in csv file if flag is yes
					if is_header:
						out_f.write(line + "\n")
						rows = 1
					try:
						line = line.replace("|", "-").replace(in_delimiter, out_delimiter)
						out_f.write(line)
						rows += 1
					except IOError as e:
						error = error + 1
						error_msg = error_msg + "\nerror in row: " + str(rows) + " - " + str(e)
		except (KeyError, OSError) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		return result

	def create_sas_dataset(self, **kwargs) -> Optional[saspy.SASdata]:
		"""
		Create SAS Dataset
		:keyword in_file: file, required -
		:return:
		"""
		result = None
		try:
			filename = kwargs["filename"]
			g_dir_clean = kwargs["gDirClean"]

			path = Path(os.getcwd() + g_dir_clean)
			s = saspy.SASsession()
			dataframe_collection = {}

			for item in os.listdir(path=path):
				file_name = os.path.splitext(filename)[0]
				file_path = path.joinpath(str(file_name))
				table_name = str(file_name).replace("_", "")
				dataframe_collection[table_name] = pandas.read_csv(filepath_or_buffer=file_path, sep="|", delimiter="|", encoding="utf8")

			for key in dataframe_collection.keys():
				result = s.df2sd(df=dataframe_collection[key], table=key, keep_outer_quotes=False)
		except (KeyError, OSError, saspy.SASConfigNotFoundError, saspy.SASConfigNotValidError) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		return result

	def get_schema(self, **kwargs):
		"""

		:param kwargs:
		:return:
		"""
		result = None
		try:
			source = kwargs["source"]
			table_name = kwargs["table_name"]
			delimiter = kwargs["delimiter"]

			json_meta = json.loads(source)
			column_header = ""
			sql_table = "create table " + table_name + "("
			sql_insert = "insert into " + table_name + " values ("
			sql_column = ""
			sql_insert_column = ""

			for item in json_meta:
				meta_table = item["table_name"]
				if table_name.lower() == meta_table.lower():
					column = item["column_name"]
					column_type = item["column_type"]
					sql_column = sql_column + "\n  " + column + " " + column_type + ", "
					sql_insert_column = sql_insert_column + "%s,"
					column_header = column_header + column + delimiter
			# finish create table statement

			sql_table += sql_table + sql_column[:-2] + ");\n\n"
			sql_insert += sql_insert + sql_insert_column[:-1] + ")"

			# remove last delimiter and return line
			result = column_header[:-len(delimiter)]
		except (KeyError, json.JSONDecodeError) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		return result


if __name__ == "__main__":
	Data()
