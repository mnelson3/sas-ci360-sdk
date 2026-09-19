#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import requests
from sasci360apimarketinggateway.base import Base


class DataDownload(Base):
	"""
	Data Download Module
	Contains the operations to download data tables for customer behavior, identities, metadata, and so on. The tables that you have access to are based on the licenses you have and the data that is available in the tables
		1. get_base_tables(self, **kwargs) -> requests.Response
		2. get_detail_tables(self, **kwargs) -> requests.Response
		3. get_identity_tables(self, **kwargs) -> requests.Response
		4. get_reprocessed_tables(self, **kwargs) -> requests.Response
	"""

	def __init__(self, algorithm, api, encoding, host, secret_key, tenant_id) -> None:
		super().__init__(algorithm, api, encoding, host, secret_key, tenant_id)

	@staticmethod
	def _finish_query_string(query_string: str) -> str:
		return query_string[:-1] if len(query_string) > 1 else ""

	def get_base_tables(self, **kwargs) -> requests.Response:
		"""
		Download Discover Base Tables and Analytical Base Tables
		:keyword start: int, optional - The start index of the items to return to the current response
		:keyword limit: int, optional - The maximum number of items to return to the current response
		:keyword date_range_start_time_stamp: str, optional - The start timestamp to use. The timestamp must be in UTC format: YYYY-MM-DDThh:mm:ss.sssZ
		:keyword date_range_end_time_stamp: str, optional - The end timestamp to use. The timestamp must be in UTC format: YYYY-MM-DDThh:mm:ss.sssZ
		:keyword schema_version: int, optional - The schema that the tables use
		:return: Returns the links to download the Discover Base Tables (DBTs) and Analytical Base Tables (ABTs). These tables are updated about every four hours. Only completed sessions are available for download.
		:rtype: requests.Response
		"""
		token = self.token
		api = self.api
		host = self.host
		query_string = "?"
		if "start" in kwargs:
			query_string += "start={0}&".format(kwargs["start"])
		if "limit" in kwargs:
			query_string += "limit={0}&".format(kwargs["limit"])
		if "date_range_start_time_stamp" in kwargs:
			query_string += "dateRangeStartTimeStamp={0}&".format(kwargs["date_range_start_time_stamp"])
		if "date_range_end_time_stamp" in kwargs:
			query_string += "dataRangeEndTimeStamp={0}&".format(kwargs["date_range_end_time_stamp"])
		if "schema_version" in kwargs:
			query_string += "schemaVersion={0}&".format(kwargs["schema_version"])
		action = "GET"
		data = None
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/discoverService/dataDownload/eventData/dbtReport{0}".format(self._finish_query_string(query_string))
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)

	def get_detail_tables(self, **kwargs) -> requests.Response:
		"""
		Download the Detail tables
		:keyword start: int, optional - The start index of the items to return to the current response
		:keyword limit: int, optional - The maximum number of items to return to the current response
		:keyword date_range_start_time_stamp: str, optional - The start timestamp to use. The timestamp must be in UTC format: YYYY-MM-DDThh:mm:ss.sssZ
		:keyword date_range_end_time_stamp: str, optional - The end timestamp to use. The timestamp must be in UTC format: YYYY-MM-DDThh:mm:ss.sssZ
		:keyword include_all_hour_status: bool, optional - Specifies whether to download all data in the requested range, regardless of a set’s internal status
		:keyword sub_hourly_data_range_in_minutes: int, optional - The number of minutes that are contained in each partition. Typically, you set this value from 10 up to 60
		:keyword schema_version: int, optional - The schema that the tables use
		:keyword category: str, optional - When you download tables with schema 4 or later, this value corresponds to the set of tables to be downloaded. When the parameter is not set, the default value is DISCOVER
		:return: Returns links to download the Detail tables, which contain the most detailed set of data that is available for user interactions. These tables also contain the source records that are processed and combined to make up reporting and Discover base tables (DBTs).
		:rtype: requests.Response
		"""
		token = self.token
		api = self.api
		host = self.host
		query_string = "?"
		if "start" in kwargs:
			query_string += "start={0}&".format(kwargs["start"])
		if "limit" in kwargs:
			query_string += "limit={0}&".format(kwargs["limit"])
		if "date_range_start_time_stamp" in kwargs:
			query_string += "dateRangeStartTimeStamp={0}&".format(kwargs["date_range_start_time_stamp"])
		if "date_range_end_time_stamp" in kwargs:
			query_string += "dateRangeEndTimeStamp={0}&".format(kwargs["date_range_end_time_stamp"])
		if "include_all_hour_status" in kwargs:
			query_string += "includeAllHourStatus={0}&".format(kwargs["include_all_hour_status"])
		if "sub_hourly_data_range_in_minutes" in kwargs:
			query_string += "subHourlyDataRangeInMinutes={0}&".format(kwargs["sub_hourly_data_range_in_minutes"])
		if "schema_version" in kwargs:
			query_string += "schemaVersion={0}&".format(kwargs["schema_version"])
		if "category" in kwargs:
			query_string += "category={0}&".format(kwargs["category"])
		action = "GET"
		data = None
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/discoverService/dataDownload/eventData/detail/partitionedData{0}".format(self._finish_query_string(query_string))
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)

	def get_identity_tables(self, **kwargs) -> requests.Response:
		"""
		Download identity tables, metadata tables, and SAS 360 Plan Tables
		:keyword start: int, optional - The start index of the items to return to the current response
		:keyword limit: int, optional - The maximum number of items to return to the current response
		:keyword schema_version: int, optional - The schema that the tables use
		:keyword category: str, optional - When you download tables with schema 4 or later, this value corresponds to the set of tables to be downloaded. When the parameter is not set, the default value is DISCOVER
		:return: Returns links to download the identity tables, metadata tables, and plan tables from the system.
		:rtype: requests.Response
		"""
		token = self.token
		api = self.api
		host = self.host
		query_string = "?"
		if "start" in kwargs:
			query_string += "start={0}&".format(kwargs["start"])
		if "limit" in kwargs:
			query_string += "limit={0}&".format(kwargs["limit"])
		if "schema_version" in kwargs:
			query_string += "schemaVersion={0}&".format(kwargs["schema_version"])
		if "category" in kwargs:
			query_string += "category={0}&".format(kwargs["category"])
		action = "GET"
		data = None
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/discoverService/dataDownload/eventData/detail/nonPartitionedData{0}".format(self._finish_query_string(query_string))
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)

	def get_reprocessed_tables(self, **kwargs) -> requests.Response:
		"""
		Download reprocessed data
		:keyword start: int, optional - The start index of the items to return to the current response
		:keyword limit: int, optional - The maximum number of items to return to the current response
		:keyword mart_type: str, required - Name of the set of data tables
		:keyword day_offset: int, optional - The previous number of days to display reset data for
		:return: Returns links to download data sets that have already been reprocessed by the system (but not those ranges that are currently being reprocessed). Data can be reprocessed because a job failed or if the system specifically requested that a data set be reprocessed.
		:rtype: requests.Response
		"""
		if kwargs.get("mart_type") is None:
			raise ValueError("mart_type is required.")

		token = self.token
		api = self.api
		host = self.host
		query_string = "?"
		if "start" in kwargs:
			query_string += "start={0}&".format(kwargs["start"])
		if "limit" in kwargs:
			query_string += "limit={0}&".format(kwargs["limit"])
		query_string += "martType={0}&".format(kwargs["mart_type"])
		if "day_offset" in kwargs:
			query_string += "dayOffset={0}&".format(kwargs["day_offset"])
		action = "GET"
		data = None
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/discoverService/dataDownload/eventData/partitionedData/resets{0}".format(self._finish_query_string(query_string))
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)


if __name__ == "__main__":
	DataDownload()
