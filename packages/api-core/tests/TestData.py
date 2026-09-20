#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from sasci360apicore import data


class TestData(unittest.TestCase):
	def setUp(self):
		self.data = data.Data()
		self.tmpdir = tempfile.TemporaryDirectory()
		self.addCleanup(self.tmpdir.cleanup)

	def _write(self, name, content):
		path = os.path.join(self.tmpdir.name, name)
		with open(path, "w", encoding="utf8") as f:
			f.write(content)
		return path

	def test_create_csv_replaces_delimiter(self):
		in_file = self._write("in.txt", "a|1~b~c\na|2~d~e\n")
		out_file = os.path.join(self.tmpdir.name, "out.csv")

		self.data.create_csv(
			in_file=in_file, out_file=out_file,
			in_delimiter="~", out_delimiter=",",
			is_header=False,
		)

		with open(out_file, "r", encoding="utf8") as f:
			lines = f.readlines()

		# "|" is always replaced with "-" in addition to the configured delimiter swap
		self.assertEqual(lines, ["a-1,b,c\n", "a-2,d,e\n"])

	def test_create_csv_with_header_writes_each_line_once(self):
		# Regression: is_header is a per-call flag checked on every line, not
		# just the first - the write inside `if is_header:` had no `continue`,
		# so every line fell through to the transform-and-write below too,
		# duplicating every row in the output when is_header=True.
		in_file = self._write("in.txt", "h1~h2\na~b\n")
		out_file = os.path.join(self.tmpdir.name, "out.csv")

		self.data.create_csv(
			in_file=in_file, out_file=out_file,
			in_delimiter="~", out_delimiter=",",
			is_header=True,
		)

		with open(out_file, "r", encoding="utf8") as f:
			lines = f.readlines()

		self.assertEqual(lines, ["h1,h2\n", "a,b\n"])

	def test_create_csv_logs_and_continues_when_a_row_write_fails(self):
		in_file = self._write("in.txt", "a~b\nc~d\n")
		out_file = os.path.join(self.tmpdir.name, "out.csv")

		real_open = open

		def flaky_open(*args, **kwargs):
			handle = real_open(*args, **kwargs)
			target = kwargs.get("file", args[0] if args else None)
			if target == out_file:
				handle.write = MagicMock(side_effect=IOError("disk full"))
			return handle

		with patch("builtins.open", side_effect=flaky_open), patch.object(self.data.logger, "warning") as mock_warning:
			self.data.create_csv(
				in_file=in_file, out_file=out_file,
				in_delimiter="~", out_delimiter=",",
				is_header=False,
			)

		mock_warning.assert_called_once()
		self.assertIn("2 row(s) failed to write", mock_warning.call_args.args[0])

	def test_create_csv_missing_kwarg_returns_none(self):
		result = self.data.create_csv(in_file="missing.txt")
		self.assertIsNone(result)

	def test_create_csv_missing_in_file_returns_none(self):
		result = self.data.create_csv(
			in_file=os.path.join(self.tmpdir.name, "does-not-exist.txt"),
			out_file=os.path.join(self.tmpdir.name, "out.csv"),
			in_delimiter="~", out_delimiter=",", is_header=False,
		)
		self.assertIsNone(result)

	def test_get_schema_builds_header_for_matching_table(self):
		source = json.dumps([
			{"table_name": "Customers", "column_name": "id", "column_type": "int"},
			{"table_name": "Customers", "column_name": "name", "column_type": "varchar"},
			{"table_name": "Orders", "column_name": "order_id", "column_type": "int"},
		])

		result = self.data.get_schema(source=source, table_name="customers", delimiter="|")

		self.assertEqual(result, "id|name")

	def test_get_schema_missing_kwarg_returns_none(self):
		result = self.data.get_schema(source="{}")
		self.assertIsNone(result)

	def test_get_schema_invalid_json_returns_none(self):
		result = self.data.get_schema(source="not json", table_name="customers", delimiter="|")
		self.assertIsNone(result)

	@patch("sasci360apicore.data.saspy.SASsession")
	@patch("sasci360apicore.data.pandas.read_csv")
	@patch("sasci360apicore.data.os.listdir")
	def test_create_sas_dataset_converts_each_file_to_a_sas_table(
		self, mock_listdir, mock_read_csv, mock_sas_session_class
	):
		mock_listdir.return_value = ["customers.csv"]
		mock_read_csv.return_value = MagicMock(name="dataframe")
		mock_session = MagicMock()
		mock_session.df2sd.return_value = MagicMock(name="sasdata")
		mock_sas_session_class.return_value = mock_session

		result = self.data.create_sas_dataset(filename="customers.csv", gDirClean="/data")

		self.assertIsNotNone(result)
		mock_session.df2sd.assert_called_once()
		called_kwargs = mock_session.df2sd.call_args.kwargs
		self.assertEqual(called_kwargs["table"], "customers")
		self.assertFalse(called_kwargs["keep_outer_quotes"])

	@patch("sasci360apicore.data.saspy.SASsession")
	def test_create_sas_dataset_missing_kwarg_returns_none(self, mock_sas_session_class):
		result = self.data.create_sas_dataset(filename="customers.csv")
		self.assertIsNone(result)
		mock_sas_session_class.assert_not_called()

	@patch("sasci360apicore.data.saspy.SASsession")
	@patch("sasci360apicore.data.os.listdir")
	def test_create_sas_dataset_returns_none_on_sas_config_error(self, mock_listdir, mock_sas_session_class):
		import saspy
		mock_sas_session_class.side_effect = saspy.SASConfigNotFoundError("no config")

		result = self.data.create_sas_dataset(filename="customers.csv", gDirClean="/data")

		self.assertIsNone(result)


if __name__ == "main":
	unittest.main()
