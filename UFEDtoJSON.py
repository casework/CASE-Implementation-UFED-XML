#---	class UFEDtoJSON.py

import uuid
import os
import re
import sys
#from UFED_case_generator import *
from dependencies.CASE_Mapping_Python import base, case, drafting, uco
from datetime import datetime, date
from typing import Dict, List, Optional, Union

class UFEDtoJSON():
	'''
	It represents all attributes and methods to process the traces extracted from XML reports to generate
	the JSON-LD file complied with the last version of UCO/CASE ontologies.
	'''
	TAB = '\t'

# default value for string value not provided
#
	NP = ''

# default value for integer value not provided
#
	INT = '0'

# default value for date value not provided
#
	DATE = '1900-01-01T08:00:00'

# default value for Hash Method value not provided
#
	HASH_M = 'MD5'

# default value for Hash Method value not provided
#
	HASH_V = '1' * 76

# default value for the property referrerUrl of the URLHistoryFacet class
#
	REF_URL = 'http:www.empty.com/referrer_url'

# default value for the location where a forensic action was carried out
#
	LOC = 'Unknown location'


	def __init__(
		self,
		json_output=None,
		app_name=None,
		app_user_name=None,
		app_user_account=None,
		case_bundle=None):
		'''
		The main class to deal with the artifacts extracted from the XML report
		and call the CASE-Mapping-Python library to convert them into the
		UCO/CASE representation by the generation of a JSON-LD file
		'''
		self.bundle = case_bundle
		self.FileOut = json_output
		self.phone_number_list = []
		self.phoneNameList = []
		self.phone_uuid_list = []
		
		self.appNameList = []
		self.appObjectList = []
		self.domain_name_list = []
		self.domain_observable_list = []
		self.appAccountUsernameList = []
		self.appAccountNameList = []
		self.accountName = []
		self.uuidaccountName = []

		self.chat_name_participants_list = []
		self.chat_id_participants_list = []
		self.chat_id_account_list = []

		self.EMAILaccountObjectList = []
		self.EMAILaddressList = []
		self.phoneOwnerNumber = ''
		self.object_phone_owner = ''
		self.FILEuuid = {}
		self.FILEpath = {}
		self.FILEid = []

		self.EXTRA_INFOdictPath = {}
		self.EXTRA_INFOdictSize = {}
		self.EXTRA_INFOdictTableName = {}
		self.EXTRA_INFOdictOffset = {}
		self.EXTRA_INFOdictNodeInfoId = {}

		self.U_ACCOUNTapp = app_name
		self.U_ACCOUNTappUserName = app_user_name
		self.U_ACCOUNTappUserAccount = app_user_account

		self.DEVICE_object = None

		self.UrlList = {}

		self.LocationList = []
		self.LocationIDList = []

		self.CELL_SITE_gsm ={}

		self.WIRELESS_NET_ACCESS ={}

		self.LOCATION_lat_long_coordinate = {}
		self.SEARCHED_ITEMvalue = []


		self.SYS_MSG_ID = ''
	
	@staticmethod
	def __createUUID():
		'''
		Observables in CASE have a unique identification number, based on Globally Unique Identifier.  
		Each time a Trace is generated this static method in invoked, it doen't depends on any object
		'''
		return str(uuid.uuid4())

	def __check_application_name(self, name):
		"""It stores all the application connected with any Trace, in order to avoid duplications.
		:param name: Tte name of the application (string)
		:return: observableApp.
		"""
		if name in self.appNameList:
			idx = self.appNameList.index(name)
			observable_app = self.appObjectList[idx]
		else:
			observable_app = self.__generateTraceAppName(name)
			self.appNameList.append(name)
			self.appObjectList.append(observable_app)
		return observable_app

	def __checkAccountName(self, account, name, uuidApp):
		self.accountName = []
		self.uuidaccountName = []
		id = account + '###' + name
		if id not in self.accountName:
			uuid = self.__generate_application_account_facet(account, name, uuidApp)
			self.accountName.append(id)
			self.uuidaccountName.append(uuid)

	def __checkGeoCoordinates(self, latitude, longitude, elevation, category):
		latitude = latitude.strip()
		longitude = longitude.strip()
		observable_location = None
		if latitude != '' and longitude != '':
			id_geo_loc = latitude + '@' + longitude
			if id_geo_loc in self.LOCATION_lat_long_coordinate.keys():
				observable_location = self.LOCATION_lat_long_coordinate[id_geo_loc]
			else:
				observable_location = self.__generate_trace_geo_location(latitude,
					longitude, elevation, category)
				self.LOCATION_lat_long_coordinate[id_geo_loc] = observable_location
		return observable_location

	def __checkSearchedItems(self, value):
		itemFound = True
		if value not in self.SEARCHED_ITEMvalue:
			self.SEARCHED_ITEMvalue.append(value)
			itemFound = False
		
		return itemFound

	def __checkUrlAddress(self, address):
		if address in self.UrlList.keys():
			observable_url = self.UrlList.get(address)
		else:
			observable_url = self.__generateTraceURLFullValue(address)
			self.UrlList[address] = observable_url
		return observable_url

	def __checkChatParticipant(self, chat_id, chat_name, chat_source, id_app):
		if chat_id.strip() in self.chat_id_participants_list:
			idx = self.chat_id_participants_list.index(chat_id.strip())
			observable_chat_account = self.chat_id_account_list[idx]
		else:
			self.chat_name_participants_list.append(chat_name.strip())
			observable_chat_account = self.__generate_application_account_facet(chat_id.strip(),
				chat_name.strip(), id_app)
			self.chat_id_participants_list.append(chat_id.strip())
			self.chat_id_account_list.append(observable_chat_account)
		return observable_chat_account

	def __checkPhoneNumber(self, contact_phone_num, contact_name):
		if contact_phone_num not in self.phone_number_list:
			self.phone_number_list.append(contact_phone_num)
			self.phoneNameList.append(contact_name)
			mobileOperator = ""
			uuid = self.__generate_phone_account_facet(mobileOperator,
				contact_name, contact_phone_num)
			self.phone_uuid_list.append(uuid)

	def cleanDate(self, originalDate):
		aMonths = {
			'Jan': '01',
			'Feb': '02',
			'Mar': '03',
			'Apr': '04',
			'May': '05',
			'Jun': '06',
			'Jul': '07',
			'Aug': '08',
			'Sep': '09',
			'Oct': '10',
			'Nov': '11',
			'Dec': '12'
		}
		
		if 	not originalDate:
			return None
		
		originalDate = originalDate.strip()

		for k,v in aMonths.items():
			if originalDate.find(k) > -1:
				originalDate = originalDate.replace(k, v)
				break
		originalDate = originalDate.replace("/", "-")
		originalDate = originalDate.replace("(", "-")
		originalDate = originalDate.replace(")", "-")
		originalDate = originalDate.replace(' ', 'T', 1)
		originalDate = originalDate.replace('UTC', '')
		originalDate = originalDate.replace('AM', '')
		originalDate = originalDate.replace('PM', '')
		if re.search('^[0-9]{4}', originalDate):
			pass
		else:
			originalDate = re.sub('-([0-9][0-9])T', '-20\g<1>T', originalDate)
			originalDate = str(originalDate[6:10]) + originalDate[2:6] + originalDate[0:2] + \
				originalDate[10:]
		startTZ = originalDate.find("+")
		if startTZ > -1:
			originalDate = originalDate[:startTZ]
		firstChars = originalDate[:10]
		firstChars = firstChars.replace(".", "-")
		originalDate = firstChars + originalDate[10:]
		originalDate = originalDate.strip()
		if originalDate[-1] == '-':
			originalDate = originalDate[0:-1]
		originalDate = originalDate.replace('.000', '')
		originalDate = originalDate.replace('.', ':')
		if re.search('T\d{2}\.', originalDate):
			originalDate = originalDate.replace('.', ':')
		if re.search('(\d{2}:\d{2}:\d{2})$', originalDate):
			pass
		else:
			originalDate = re.sub('(\d{2}:\d{2})$', '\g<1>:00', originalDate)
		if re.search('T(\d):', originalDate):
			originalDate = re.sub('T(\d):', 'T0\g<1>:', originalDate)
		if re.search(':(\d):', originalDate):
			originalDate = re.sub(':(\d):', ':0\g<1>:', originalDate)
		if re.search(':(\d)$', originalDate):
			originalDate = re.sub(':(\d)$', ':0\g<1>', originalDate)
		if re.search('T\d{2}:\d{2}:\d{2}(.+)$', originalDate):
			originalDate = re.sub('(T\d{2}:\d{2}:\d{2})(.+)$', '\g<1>', originalDate)
		if originalDate.find('+') > -1:
			originalDate = datetime.strptime(originalDate,
				'%Y-%m-%dT%H:%M:%S.%f%z')
		else:
			originalDate = datetime.strptime(originalDate,
				'%Y-%m-%dT%H:%M:%S')
		return originalDate

	def cleanJSONtext(self, originalText):
		new_text = originalText.strip()
		if new_text == '':
			return ''
		else:
			new_text = new_text.replace('"', "").replace('\n', '').replace('\r', '')
			new_text = new_text.replace('\t', " ").replace("\\'", "'").replace("\\", "")
			return new_text

	def __generateContextUfed(self, ufedVersion, deviceReportCreateTime,
			deviceExtractionStartTime, deviceExtractionEndTime, examinerName,
			imagePath, imageSize, imageMetadataHashSHA, imageMetadataHashMD5):

		# generate Trace/Tool for the Acquisition and Extraction Actions
		object_tool = self.__generateTraceTool('UFED PA', 'Acquisition',
			'Cellebrite', ufedVersion, []);
		
		# generate Trace/Identity for the Performer, D.F. Expert, of the Actions
		object_identity = self.__generateTraceIdentity(examinerName, '', '')
		
		# generate Trace/Role for the Performer, D.F. Expert, of the Actions
		object_role = self.__generateTraceRole('Digital Forensic Expert')
		
		# generate Trace/Relation between the above Role and the Identity traces
		# the Relationshi accept ObservableObjects only, so this statement
		# raises an error of Type
		# self.__generateTraceRelation(object_identity, object_role,
		# 	'has_role', '', '', None, None);
		
#---	The XML report contains the attribute DeviceInfoExtractionStartDateTime
#		that is the Acquisition Start Date and similarly for the Acquisition
#		End Date, The CreationReportDate is the Start and the End of the Extraction
#		Forensic Action.

		object_device_list = []
		object_device_list.append(self.DEVICE_object)
		object_provenance_device = self.__generateTraceProvencance(object_device_list,
			'Mobile device', '', deviceExtractionStartTime)

# generate Trace/File for each file extracted by the Acuisition action
# idFileList contains the uuid of these files and it is used for
# creating the Provenance_Record of the Result/Output of the Acquisition
# action. 2021-08-02: actually the XML report doesn't include the Acquisition info
#
		object_files_acquisition = []
		for i, img_path in enumerate(imagePath):
			if imageMetadataHashSHA[i].strip() == '':
				object_file_acquisition = self.__generateTraceFile(img_path,
				imageSize[i], 'MD5', imageMetadataHashMD5[i], 'Uncategorized', '', '', '', '',
				'', '', '', '', '', '', '', '', '', '', '')
				 
			else:
				object_file_acquisition = self.__generateTraceFile(img_path,
				imageSize[i], 'SHA256', imageMetadataHashSHA[i], 'Uncategorized',
				'', '', '', '', '', '', '', '', '', '', '', '', '', '', '')
			
			object_files_acquisition.append(object_file_acquisition)
		
		object_provenance_acquisition_files = \
			self.__generateTraceProvencance(object_files_acquisition,
        	'Acquisition files', '', deviceExtractionStartTime)
		object_provenance_acquisition_files_list = []
		object_provenance_acquisition_files_list.append(object_provenance_acquisition_files)
		object_provencance_acquisition_action = \
		self.__generateTraceInvestigativeAction('acquisition',
			'Forensic mobile device acquisition', deviceExtractionStartTime,
			deviceExtractionEndTime, object_tool, '', object_identity,
			object_provenance_device, object_provenance_acquisition_files_list);
		object_files_extraction = []
		for uuidFile in self.FILEuuid.values():
			object_files_extraction.append(uuidFile)
		object_provenance_extraction_files = \
		self.__generateTraceProvencance(object_files_extraction, 'Extraction',
			'', deviceReportCreateTime);
		object_provenance_extraction_files_list = []
		object_provenance_extraction_files_list.append(object_provenance_extraction_files)

		self.__generateTraceInvestigativeAction('extraction',
			'Forensic mobile device extraction', deviceReportCreateTime,
			deviceReportCreateTime, object_tool, '', object_identity,
			object_provenance_acquisition_files, object_provenance_extraction_files_list);

	def __generate_chain_of_evidence(self, IdTrace, uuidTrace):
# Search traceId in EXTRA_INFOdictNodeInfo a dictionary whose keys are the id
# that represents the link between a Trace and its file(s)
#
		table = self.EXTRA_INFOdictTableName.get(IdTrace, '_?TABLE')
		offset = self.EXTRA_INFOdictOffset.get(IdTrace, '_?OFFSET')
#--- This is the case where the infoNode sub element of extraInfo contains the id
#--- reference to the file. More then one infoNode can exist, the value of the key
#--- contains the id file separated by @
		if self.EXTRA_INFOdictNodeInfoId.get(IdTrace, '').strip() == '':
			path = self.EXTRA_INFOdictPath.get(IdTrace, '_?PATH')
			size = self.EXTRA_INFOdictSize.get(IdTrace, '_?SIZE')
			if path != '_?PATH':
				uuidFile = self.__generateTraceFile(path, size, '',
						'', 'Uncategorized', '', '', '', '', '',
						'', '', '', '', '', '', '', '', '', '')
				self.FILEuuid[IdTrace] = uuidFile
				self.__generateTraceRelation(uuidTrace, uuidFile, 'Contained_Within',
					table, offset, None, None);
		else:
			nodeInfoIdList = self.EXTRA_INFOdictNodeInfoId.get(IdTrace, '@@@').split('@@@')
			for node in nodeInfoIdList:
				if node.strip() != '':
					if node in self.FILEid:
						uuidFile = self.FILEuuid.get(node, '_?UUID')
						self.__generateTraceRelation(uuidTrace, uuidFile, 'Contained_Within',
							table, offset, None, None);
					# else:
					# 	print ('nodeInfo ' + node + ' not found')

	def write_device(self, deviceId, devicePhoneModel, deviceOsType, deviceOsVersion,
            devicePhoneVendor, deviceMacAddress, deviceIccid, deviceImsi,
            deviceImei, deviceBluetoothAddress, deviceBluetoothName):
		'''
		Generate Device Facet for the mobile phone
		'''
		self.DEVICE_object = self.__generateTraceDevice(
			deviceMacAddress,
			deviceId,
			devicePhoneModel,
			deviceOsType,
			deviceOsVersion,
			devicePhoneVendor,
			deviceMacAddress,
			deviceIccid,
			deviceImsi,
			deviceImei,
			deviceBluetoothAddress,
			deviceBluetoothName
		)

	def __generateTraceAppName(self, app_name):
		'''
		Generate Application Facet
		'''
		observable = uco.observable.ObservableObject()
		facet_application = uco.observable.ApplicationFacet(
			application_identifier=app_name
		)
		observable.append_facets(facet_application)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __get_max_len_call_element(self, call_roles_to, call_roles_from,
					call_names_to, call_names_from, call_identifiers_to,
					call_identifiers_from):
		maxLen = len(call_roles_to)
		
		if len(call_roles_from) > maxLen:
			maxLen = len(call_roles_from)
		if len(call_names_to) > maxLen:
			maxLen = len(call_names_to)
		if len(call_names_from) > maxLen:
			maxLen = len(call_names_from)
		if len(call_identifiers_to) > maxLen:
			maxLen = len(call_identifiers_to)
		if len(call_identifiers_from) > maxLen:
			maxLen = len(call_identifiers_from)
		return maxLen

	def write_call(
		self,
		call_id: List[str],
		call_status: List[str] = None,
		call_source: List[str] = None,
		call_start_time: List[datetime] = None,
		call_direction: List[str] = None,
		call_duration: List[int] = None,
		call_roles_to: Union[List[str], None] = None,
		call_role_from: List[str] = None,
		call_names_to: Dict = None,
		call_name_from: List[str] = None,
		call_outcome: List[str] = None,
		call_identifiers_to: Union[List[str], None] = None,
		call_identifier_from: List[str] = None,
	):
		'''
		Convert any kind of call, further the traditional phone call, is processed, so the
		phone_regex_pattern is not necessary mandatory any more.
		'''
		phone_regex_pattern = '^\+?[0-9]+$'
		for i, call_id in enumerate(call_id):
			id_party_to = ''
			id_party_from = ''
			id_party = ''
			maxLen = self.__get_max_len_call_element(call_roles_to[i], call_role_from[i],
					call_names_to[i], call_name_from[i], call_identifiers_to[i],
					call_identifier_from[i])
# All these arrays should have the same size, the check fill in the values.
# if this is not the case, the loops make the dimension of all arrays the same
			for j in range(maxLen - len(call_roles_to[i])):
				call_roles_to[i].append('')
			for j in range(maxLen - len(call_role_from[i])):
				call_role_from[i].append('')
			for j in range(maxLen - len(call_names_to[i])):
				call_names_to[i].append('')
			for j in range(maxLen - len(call_name_from[i])):
				call_name_from[i].append('')
			for j in range(maxLen - len(call_identifiers_to[i])):
				call_identifiers_to[i].append('')
			for j in range(maxLen - len(call_identifier_from[i])):
				call_identifier_from[i].append('')
			if maxLen == 0:
				call_roles_to[i].append('')
				call_role_from[i].append('')
				call_names_to[i].append('')
				call_name_from[i].append('')
				call_identifiers_to[i].append('')
				call_identifier_from[i].append('')
			if (len(call_role_from[i]) > 1):
				if call_role_from[i][0].strip() == '':
					id_party_from = call_identifier_from[i][1]
					name_from = call_name_from[i][1]
					id_party_to = call_identifiers_to[i][0]
					name_to = call_names_to[i][0]
				else:
					id_party_from = call_identifier_from[i][0]
					name_from = call_name_from[i][0]
					id_party_to = call_identifiers_to[i][1]
					name_to = call_names_to[i][1]
			else:
					if call_role_from[i][0].strip() == '':
						id_party_from = self.phoneOwnerNumber
						name_from = 'PHONE OWNER'
						id_party_to = call_identifiers_to[i][0]
						id_party = id_party_to
						name_to = call_names_to[i][0]
					else:
						id_party_from = call_identifier_from[i][0]
						id_party = id_party_from
						id_party_to = self.phoneOwnerNumber
						name_from = call_name_from[i][0]
						name_to = 'PHONE OWNER'
			resPattern = re.match(phone_regex_pattern, id_party.strip())

			if resPattern:
				if id_party_to in self.phone_number_list:
					idx = self.phone_number_list.index(id_party_to)
					uuid_party_to = self.phone_uuid_list[idx]
				else:
	# if the mobile operator is available in the XML report, an uco-identity:Identity
	# will be defined as Organisation.
					mobileOperator = "-"
					uuid_party_to = self.__generate_phone_account_facet(mobileOperator,
										name_to, id_party_to)

				if id_party_from in self.phone_number_list:
					idx = self.phone_number_list.index(id_party_from)
					uuid_party_from = self.phone_uuid_list[idx]
				else:
					mobileOperator = "-"
					uuid_party_from = self.__generate_phone_account_facet(mobileOperator,
						name_from, id_party_from)
			else:
				idAppIdentity = self.__check_application_name(call_source[i].strip())
				if id_party_from.strip() in self.chat_id_participants_list:
					idx = self.chat_id_participants_list.index(id_party_from.strip())
					uuid_party_from = self.chat_id_account_list[idx]
				else:
					self.chat_name_participants_list.append(name_from.strip())
					uuid_party_from = self.__generate_application_account_facet(id_party_from.strip(),
						name_from.strip(), idAppIdentity)
					self.chat_id_participants_list.append(id_party_from.strip())
					self.chat_id_account_list.append(uuid_party_from)
				if id_party_to.strip() in self.chat_id_participants_list:
					idx = self.chat_id_participants_list.index(id_party_to.strip())
					uuid_party_to = self.chat_id_account_list[idx]
				else:
					self.chat_name_participants_list.append(name_to.strip())
					uuid_party_to = self.__generate_application_account_facet(id_party_to.strip(),
						name_to.strip(), idAppIdentity)
					self.chat_id_participants_list.append(id_party_to.strip())
					self.chat_id_account_list.append(uuid_party_to)
			object_phone_call = self.__generate_call_facet(call_direction[i].lower(),
				call_start_time[i], uuid_party_from, uuid_party_to, call_duration[i],
            	call_status[i], call_outcome[i])
			self.__generate_chain_of_evidence(call_id, object_phone_call)

	def __generateTraceWebBookmark(self, wb_id, wb_source, wb_timeStamp, wb_path, wb_url):
		'''
		It generates the uco-observable:BrowserBookmarkFacet objectt
		'''
		web_bookmark_object = uco.observable.ObservableObject()
		#object_url = self.__checkUrlAddress(wb_url)
		objet_app = self.__check_application_name(wb_source)
		
		if wb_timeStamp.strip() == '':
			wb_timeStamp = None
		else:
			wb_timeStamp = self.cleanDate(wb_timeStamp)
		facet_web_bookmark = uco.observable.BrowserBookmarkFacet(
			application_id=objet_app,
			urlTargeted=wb_url,
			bookmarkPath=wb_path,
			accessedTime=wb_timeStamp
    	)
		web_bookmark_object.append_facets(facet_web_bookmark)
		self.bundle.append_to_uco_object(web_bookmark_object)
		return web_bookmark_object

	def __generateTraceBluetooth(self, bt_id, bt_status, bt_value):
		if bt_value.strip() == '':
			return None
		
		bluetooth_object = uco.observable.ObservableObject()
		facet_bluetooth = uco.observable.BluetoothAddressFacet(address=bt_value)
		bluetooth_object.append_facets(facet_bluetooth)
		self.bundle.append_to_uco_object(bluetooth_object)
		return bluetooth_object

	def __generateTraceCalendar(self, calendar_id, status, group, subject,
			details, startDate, endDate, repeatUntil, repeatInterval, repeatRule):
		startDate = self.cleanDate(startDate)
		endDate = self.cleanDate(endDate)
		subject = self.cleanJSONtext(subject)
		details = self.cleanJSONtext(details)
		calendar_object = uco.observable.ObservableObject()
		# what are group and details?
		#print(f"group={group}\ndetails={details}")
		facet_calendary = uco.observable.CalendarEntryFacet(
			subject=subject,
			start_time=startDate,
			end_time=endDate,
			recurrence=repeatInterval,
		)
		calendar_object.append_facets(facet_calendary)
		self.bundle.append_to_uco_object(calendar_object)
		return calendar_object

	def __generate_trace_cell_site(self, cell_id, cell_status,
			cell_longitude, cell_latitude, cell_timeStamp, cell_mcc,
			cell_mnc, cell_lac, cell_cid, cell_nid, cell_bid, cell_sid):
		cell_timeStamp = self.cleanDate(cell_timeStamp)
		observableLocation = self.__checkGeoCoordinates(cell_latitude, cell_longitude, '', 'Cell Tower')
		cell_id = cell_mcc.strip() + '@' + cell_mnc.strip() +'@' + \
			cell_lac.strip() + '@' + cell_cid.strip()
		if cell_id == '@@@':
			return None
		if cell_id in self.CELL_SITE_gsm.keys():
			return self.CELL_SITE_gsm.get(cell_id)
		else:
			cell_site_object = uco.observable.ObservableObject()
			facet_cell_site = uco.observable.CellSiteFacet(
				cell_site_country_code=cell_mcc,
				cell_site_network_code=cell_mnc,
				cell_site_location_area_code=cell_lac,
				cell_site_identifier=cell_cid
			)
			cell_site_object.append_facets(facet_cell_site)
			self.bundle.append_to_uco_object(cell_site_object)
			self.CELL_SITE_gsm[cell_id] = cell_site_object
			if observableLocation:
				observable_relationship = uco.observable.ObservableRelationship(
					source=cell_site_object,
					target=observableLocation,
					start_time=cell_timeStamp,
					kind_of_relationship="Located_At",
					directional=True)
				self.bundle.append_to_uco_object(observable_relationship)
			return cell_site_object

	def __generate_application_account_facet(self, partyId, partyName, idApp):
		partyName = self.cleanJSONtext(partyName)
		partyId = self.cleanJSONtext(partyId)
		observable = uco.observable.ObservableObject()
		facet_account = uco.observable.AccountFacet(identifier=partyId)
		facet_app_account = uco.observable.ApplicationAccountFacet(application=idApp)
		facet_digital_account = uco.observable.DigitalAccountFacet(display_name=partyName)
		observable.append_facets(facet_account, facet_app_account, facet_digital_account)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceChat(self, body, idApplication, timeStamp, idFrom,
		idToList, status, outcome, direction, attachmentNames, attachmentUrls):
		TOlist = []
		for item in idToList:
			if item != idFrom:
				TOlist.append(item)
		if TOlist == []:
			TOlist.append(idFrom)
		body = self.cleanJSONtext(body)
		observable_message = self.__generate_trace_message(body, idApplication,
			idFrom, TOlist, timeStamp, status, 'CHAT Message')
# Each Message, within a specific Chat can have more than one attachment,
# both the Filenames and the Urls of the Attachment are separated by a triple hash tag #
		listFileNames = attachmentNames.split('###');
		listFileUrls = attachmentUrls.split('###');
		nName = len(listFileNames)
		nUrl = len(listFileUrls)
		if nName > nUrl:
			for i in range(nName - nUrl):
				listFileUrls.append('')
		if nName < nUrl:
			for i in range(nUrl - nName):
				listFileNames.append('')
		for i, file_name in enumerate(listFileNames):
			if (file_name.strip() != '') or \
			 	(listFileUrls[i].strip() != ''):
				fileUuid = self.__generateTraceFile(file_name,
				'', '', '', 'Uncategorized', '', '', '', listFileUrls[i],
				'', '', '', '', '', '', '', '', '', '', '')
				if uuid != '':
					self.__generateTraceRelation(fileUuid, observable_message,
						'Connected_To', '', '', None, None)
		return observable_message

	def __generateTraceDevice(self, deviceMAC, deviceSN, deviceModel,
		deviceOS, deviceOSVersion, deviceManufacturer, deviceWiFi, deviceICCID,
		deviceIMSI, deviceIMEI, deviceBluetoothAddress, deviceBluetoothName):
		device_object = uco.observable.ObservableObject()
		facet_device = uco.observable.DeviceFacet(
			device_type="Mobile phone",
			model=deviceModel,
			serial=deviceSN
		)
		sim_card_facet = uco.observable.SimCardFacet(
    		ICCID=deviceICCID,
    		IMSI=deviceIMSI)		
		if deviceManufacturer:
			manufacturer_object = self.__generateTraceIdentity(None, deviceManufacturer, None)
			facet_operating_system = uco.observable.OperatingSystemFacet(
				os_version=deviceOSVersion, os_manufacturer=manufacturer_object)
		else:
			facet_operating_system = uco.observable.OperatingSystemFacet(
				os_version=deviceOSVersion)
		facet_bluetooth = uco.observable.BluetoothAddressFacet(address=deviceBluetoothAddress)
		facet_wifi = uco.observable.WifiAddressFacet(wifi_mac_address=deviceWiFi)
		device_object.append_facets(facet_device, sim_card_facet, facet_operating_system,
    	facet_bluetooth,facet_wifi)
		self.bundle.append_to_uco_object(device_object)
		return device_object

	def __generate_trace_cookie(self, cookie_id, cookie_status,
					cookie_source, cookie_name, cookie_path, cookie_domain,
					cookie_creationTime, cookie_lastAccessedTime, cookie_expiry):
		cookie_creationTime = self.cleanDate(cookie_creationTime)
		cookie_lastAccessedTime = self.cleanDate(cookie_lastAccessedTime)
		cookie_expiry = self.cleanDate(cookie_expiry)
		cookie_name = self.cleanJSONtext(cookie_name)
		cookie_object = uco.observable.ObservableObject()
		observable_source = self.__check_application_name(cookie_source)
		observable_domain = self.__check_application_name(cookie_domain)
		facet_cookie = uco.observable.BrowserCookieFacet(
			name=cookie_name,
			path=cookie_path,
			created_time=cookie_creationTime,
			last_access_time=cookie_lastAccessedTime,
			expiration_time=cookie_expiry
			)
		cookie_object.append_facets(facet_cookie)
		self.bundle.append_to_uco_object(cookie_object)
		return cookie_object

	def __generateTraceDeviceEvent(self, event_id, event_status,
		event_timeStamp, event_type, event_text):
		event_timeStamp = self.cleanDate(event_timeStamp)
		event_text = self.cleanJSONtext(event_text)
		device_event_object = uco.observable.ObservableObject()
		facet_event = uco.observable.EventRecordFacet(
			event_type=event_type,
			event_record_text=event_text,
			observable_created_time=event_timeStamp
		)
		device_event_object.append_facets(facet_event)
		self.bundle.append_to_uco_object(device_event_object)
		return device_event_object

	def __generateTraceInstalledApp(self, INSTALLED_APPid, INSTALLED_APPstatus, INSTALLED_APPname,
	    INSTALLED_APPversion, INSTALLED_APPidentifier, INSTALLED_APPpurchaseDate):
		INSTALLED_APPtimeStamp = self.cleanDate(INSTALLED_APPpurchaseDate)
# If installed_app_purchase_date is not empy a complete ApplicationFacet and ans ApplicationVerions are generated,
# otherwise on a partial APplicatinFacet is generate and no Chain of Evidence is created (return None)
		observable = uco.observable.ObservableObject()
		if INSTALLED_APPtimeStamp:
			object_app_version = uco.observable.ObservableApplicationVersion(
				install_date=INSTALLED_APPtimeStamp)
			#self.bundle.append_to_uco_object(object_app_version)
			facet_application = uco.observable.ApplicationFacet(
				application_identifier=INSTALLED_APPname,
				installed_version_history=[object_app_version]
			)
			observable.append_facets(facet_application)
			self.bundle.append_to_uco_object(observable)
			return observable
		else:
			facet_application = uco.observable.ApplicationFacet(
				application_identifier=INSTALLED_APPname)
			observable.append_facets(facet_application)
			self.bundle.append_to_uco_object(observable)
			return None

	def __generateTraceEmail(self, EMAILid, EMAILstatus, EMAILsource,
		EMAILidentifierFROM, EMAILidentifiersTO, EMAILidentifiersCC,
		EMAILidentifiersBCC, EMAILbody, EMAILsubject, EMAILtimeStamp,
		EMAILattachmentsFilename):
		#print(f'EMAILidentifierFROM={EMAILidentifierFROM}')
		if EMAILidentifierFROM.strip() in self.EMAILaddressList:
			idx = self.EMAILaddressList.index(EMAILidentifierFROM.strip())
			idFROM = self.EMAILaccountObjectList[idx]
		else:
			self.EMAILaddressList.append(EMAILidentifierFROM.strip())
			observable_email_account = self.__generateTraceEmailAccount(EMAILidentifierFROM.strip())
			self.EMAILaccountObjectList.append(observable_email_account)
			idFROM = observable_email_account
		itemsTO = []
		for i, email_identifier in enumerate(EMAILidentifiersTO):
			if email_identifier.strip() != '':
				if email_identifier.strip() in self.EMAILaddressList:
					idx = self.EMAILaddressList.index(email_identifier.strip())
					itemsTO.append(self.EMAILaccountObjectList[idx])
				else:
					self.EMAILaddressList.append(email_identifier.strip())
					observable_email = \
						self.__generateTraceEmailAccount(email_identifier.strip())
					self.EMAILaccountObjectList.append(observable_email)
					itemsTO.append(observable_email)
		itemsCC = []
		for i, email_identifier_cc in enumerate(EMAILidentifiersCC):
			if email_identifier_cc.strip() != '':
				if email_identifier_cc.strip() in self.EMAILaddressList:
					idx = self.EMAILaddressList.index(email_identifier_cc.strip())
					itemsCC.append(self.EMAILaccountObjectList[idx])
				else:
					self.EMAILaddressList.append(email_identifier_cc.strip())
					observable_email = self.__generateTraceEmailAccount(email_identifier_cc.strip())
					self.EMAILaccountObjectList.append(observable_email)
					itemsCC.append(observable_email)
		itemsBCC = []
		for i, email_identifier_bcc in enumerate(EMAILidentifiersBCC):
			if email_identifier_bcc.strip() != '':
				if email_identifier_bcc.strip() in self.EMAILaddressList:
					idx = self.EMAILaddressList.index(email_identifier_bcc.strip())
					itemsBCC.append(self.EMAILaccountObjectList[idx])
				else:
					self.EMAILaddressList.append(email_identifier_bcc.strip())
					observable_email = self.__generateTraceEmailAccount(email_identifier_bcc.strip())
					self.EMAILaccountObjectList.append(observable_email)
					itemsBCC.append(observable_email)
		body = self.cleanJSONtext(EMAILbody)
		subject = self.cleanJSONtext(EMAILsubject)
		EMAILtimeStamp = self.cleanDate(EMAILtimeStamp)
		
		email_object = uco.observable.ObservableObject()
		application_object = self.__check_application_name(EMAILsource)
		facet_email_message = uco.observable.EmailMessageFacet(
			msg_to=itemsTO,
			msg_from=idFROM,
			cc=itemsCC,
			bcc=itemsBCC,
			subject=subject,
			body=body,
            sent_time=EMAILtimeStamp,
            application=application_object
        )
		email_object.append_facets(facet_email_message)
		self.bundle.append_to_uco_object(email_object)
		self.__generate_chain_of_evidence(EMAILid, email_object)
		
		for i, email_attachment in enumerate(EMAILattachmentsFilename):
			if email_attachment.strip() != '':
				fileUuid = self.__generateTraceFile(email_attachment,
				'', '', '', 'Uncategorized', '', '', '', '',
  				'', '', '', '', '', '', '', '', '', '', '')
				self.__generateTraceRelation(fileUuid, email_object, 'Attached_To',
				'', '', None, None)
		return email_object

	def __generateTraceEmailAccount(self, address):
		address = self.cleanJSONtext(address)
		email_address_object = self.__generateTraceEmailAddress(address)

		email_account_object = uco.observable.ObservableObject()
		facet_email_account = uco.observable.EmailAccountFacet(email_address_object)
		facet_account = uco.observable.AccountFacet(identifier="-")
		email_account_object.append_facets(facet_account, facet_email_account)
		
		self.bundle.append_to_uco_object(email_account_object)
		
		return email_account_object

	def __generateTraceEmailAddress(self, address):
		address = self.cleanJSONtext(address)
		email_address_object = uco.observable.ObservableObject()
		facet_email_address = uco.observable.EmailAddressFacet(
			email_address_value=address
		)
		email_address_object.append_facets(facet_email_address)
		
		self.bundle.append_to_uco_object(email_address_object)
		return email_address_object

	def __generateTraceFile(self, FILEpath, FILEsize, FILEhashType,
		FILEHashValue, FILETag, FILEtimeC, FILEtimeM, FILEtimeA, FILElocalPath,
		FILEiNode, FILEiNodeTimeM, FILEgid, FILEuid, FILEexifLatitudeRef, FILEexifLatitude,
		FILEexifLongitudeRef, FILEexifLongitude, FILEexifAltitude, FILEexifMake, FILEexifModel):
		head, tail = os.path.split(FILEpath)
		file_object = uco.observable.ObservableObject()
		tail = self.cleanJSONtext(tail)
		path = FILEpath.replace('"', "").replace('\n', '').replace('\r', '')
		path = path.replace("\\", "/")
		dotPos = tail.find('.')
		if dotPos > -1:
			sExt = tail[dotPos:]
		else:
			sExt = ''
		if FILEHashValue.upper() == 'N/A':
			FILEHashValue = UFEDtoJSON.HASH_V
		if FILEHashValue.strip() == '':
				FILEHashValue = UFEDtoJSON.HASH_V
		if FILEhashType.strip() == '':
			FILEhashType = UFEDtoJSON.HASH_M
		if FILEhashType.upper() == '_NOT_PROVIDED_':
			FILEhashType = UFEDtoJSON.HASH_M
		if FILETag.upper() == '_NOT_PROVIDED_':
			FILETag = 'Uncategorized';
		FILEsize = re.sub('[^0-9]','', FILEsize)
		if FILEsize.strip() == '':
			FILEsize = int(UFEDtoJSON.INT)
		else:
			FILEsize = int(FILEsize)

		if FILEHashValue != UFEDtoJSON.HASH_V:
			facet_content = uco.observable.ContentDataFacet(hash_method=FILEhashType, hash_value=FILEHashValue)
			file_object.append_facets(facet_content)


		FILEtimeC = self.cleanDate(FILEtimeC)
		FILEtimeM = self.cleanDate(FILEtimeM)
		FILEtimeA = self.cleanDate(FILEtimeA)
		FILEiNodeTimeM = self.cleanDate(FILEiNodeTimeM)
		FILEiNode = FILEiNode.strip()
		if FILEiNode.strip() == '':
			FILEiNode = UFEDtoJSON.INT
		if FILEiNode.find('0x') > - 1:
			FILEiNode = int(FILEiNode, 16)
		else:
			FILEiNode = int(FILEiNode)
		FILEuid = FILEuid.strip()
		if FILEuid.strip() == '':
			FILEuid = UFEDtoJSON.INT
		if FILEuid.find('0x') > - 1:
			FILEuid = int(FILEuid, 16)
		else:
			FILEuid = int(FILEuid)
		FILEgid = FILEgid.strip()
		if FILEgid.strip() == '':
			FILEgid = UFEDtoJSON.INT
		if FILEgid.find('0x') > - 1:
			FILEgid = int(FILEgid, 16)
		else:
			FILEgid = int(FILEgid)
		localPath = FILElocalPath.replace('"', "").replace('\n', '').replace('\r', '')
		localPath = localPath.replace("\\", "/")
		if FILEexifLatitude.strip() != '':
			exif_data = {"Make":FILEexifMake,
				"Model":FILEexifModel, "LatitudeRef":FILEexifLatitudeRef,
				"Latitude":FILEexifLatitude, "LongitudeRef":FILEexifLongitudeRef,
				"Longitude":FILEexifLongitude, "Altitude":FILEexifAltitude}
			facet_exif = uco.observable.EXIFFacet(**exif_data)
			file_object.append_facets(facet_exif)
		facet_ext_inode = uco.observable.ExtInodeFacet(inode_change_time=FILEiNodeTimeM,
			inode_id=FILEiNode, sgid=FILEgid, suid=FILEuid)
		file_object.append_facets(facet_ext_inode)
		facet_file = uco.observable.FileFacet(file_mime_type=FILETag, file_name=tail,
			file_path=path, file_extension=sExt, file_size_bytes=FILEsize,
			file_accessed_time=FILEtimeA, file_created_time=FILEtimeC,
            file_modified_time=FILEtimeM)
		file_object.append_facets(facet_file)
		self.bundle.append_to_uco_object(file_object)
		return file_object

	def __generateTraceIdentity(self, name, family_name, birthDate):
		birthDate = self.cleanDate(birthDate)
		identity_object = uco.identity.Identity()
		identity_facet = uco.identity.SimpleNameFacet(
			given_name=name,
			family_name=family_name
		)
		if birthDate:
			identity_birth = uco.identity.BirthInformationFacet(
    			birthdate=birthDate
    		)
			identity_object.append_facets(identity_birth, identity_facet)
		else:
			identity_object.append_facets(identity_facet)

		self.bundle.append_to_uco_object(identity_object)
		return identity_object

	def __generateTraceLocationDevice(self, loc_id, loc_status,
			loc_longitude, loc_latitude, loc_elevation,
			loc_timeStamp, loc_category, item):
		uuidLocation = self.__checkGeoCoordinates(loc_latitude, loc_longitude,
							loc_elevation, loc_category)
		return uuidLocation

	def __generate_phone_account_facet(
		self,
		phone_num: str,
		source: Optional[str] = None,
		name: Optional[str] = None,
	):
		'''
		Generate the PhoneAccountFacet and the associated Identity based on its name.
		'''
		identity = None
		if source != "":
			identity = uco.identity.Identity()
			identity_name = uco.identity.SimpleNameFacet(
    			given_name=source
			)
			self.bundle.append_to_uco_object(identity)
			
		observable = uco.observable.ObservableObject()
		account_facet = uco.observable.AccountFacet(identifier=name, issuer_id=identity)
		phone_account_facet = uco.observable.PhoneAccountFacet(phone_number=phone_num)
		observable.append_facets(account_facet, phone_account_facet)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceInvestigativeAction(self, name, description, start_time, end_time,
		object_instrument, str_location, object_performer, object_input,
		object_list_result):
		start_time = self.cleanDate(start_time)
		end_time = self.cleanDate(end_time)
		object_location = self.__generateTraceLocation(str_location)
		investigation = case.investigation.InvestigativeAction(
			description=description,
			start_time=start_time,
			end_time=end_time,
			performer=object_performer,
			instrument=object_instrument,
			location=object_location,
			objects=object_input,
			results=object_list_result
		)
		self.bundle.append_to_uco_object(investigation)

	def __generate_call_facet(self, direction, startTime, idFROM, idTO,
			duration, status, outcome):
		nTime = 0
		if duration != "":
			aTime = duration.split(":")
			if len(aTime) == 3:
				if aTime[2].find('.') > -1:
					aTime[2] = aTime[2][0:aTime[2].find('.')]
				if aTime[2].find(',') > -1:
					aTime[2] = aTime[2][0:aTime[2].find(',')]
				nTime = int(aTime[0])*3600 + int(aTime[1])*60 + int(aTime[2])
			if len(aTime) == 2:
				nTime = int(aTime[0])*60 + int(aTime[1])
			if len(aTime) == 1:
				nTime = int(aTime[0])
		duration = str(nTime)
		duration = duration.lstrip('0')
		if duration == "":
			duration = "0"
		point = duration.find('.')
		if point > - 1:
			duration = duration[0:point]
		duration = int(duration)
		observable_app = self.__check_application_name("Native")
		call_object = uco.observable.ObservableObject()
		startTime = self.cleanDate(startTime)
		facet_call = uco.observable.CallFacet(call_type=direction,
			start_time=startTime, application=observable_app, call_from=idFROM,
			call_to=idTO, call_duration=duration)
		call_object.append_facets(facet_call)
		self.bundle.append_to_uco_object(call_object)
		return call_object

	def __generateTracePhoneOwner(self, source, name, phone_num):
		identity_object = None
		# if source:
		# 	identity_object = self.__generateTraceIdentity(None, source, None)
		# 	facet_identity = SimpleNameFacet(given_name="(Owner) " + source)
		# 	identity_object.append_facets(facet_identity)
		# 	self.bundle.append_to_uco_object(identity_object)
		account_object = uco.observable.ObservableObject()
		name = ''.join([name, ' (owner)'])
		facet_account = uco.observable.AccountFacet(identifier=name, issuer_id=identity_object)
		facet_phone_account = uco.observable.PhoneAccountFacet(phone_number=phone_num)
		account_object.append_facets(facet_account, facet_phone_account)
		self.bundle.append_to_uco_object(account_object)
		self.object_phone_owner = account_object
		self.phone_number_list.append(phone_num)
		self.phone_uuid_list.append(self.object_phone_owner)

	def __generateTraceProvencance(self, uco_core_objects, description,
		exhibitNumber, creationTime):
 		case_provenance = case.investigation.ProvenanceRecord(
 			exhibit_number=exhibitNumber,
			uco_core_objects=uco_core_objects
		)
 		self.bundle.append_to_uco_object(case_provenance)
 		return case_provenance

	def __generateTraceRelation(self, source, target, relation, table, offset,
		start_date, end_date):
		if isinstance(start_date, str):
			start_date = self.cleanDate(start_date)
		if isinstance(end_date, str):
			end_date = self.cleanDate(end_date)
		object_relationship = uco.observable.ObservableRelationship(
			source=source,
			target=target,
			start_time=start_date,
			end_time=end_date,
			kind_of_relationship=relation,
			directional=True)
		self.bundle.append_to_uco_object(object_relationship)
		return object_relationship

	def __generateTraceRole(self, role):
		object_role = uco.role.Role(name=role)
		self.bundle.append_to_uco_object(object_role)
		return object_role

	def __generateTraceSocialMedia_Item(self, sm_item_id, sm_status,
					sm_source, sm_timeStamp, sm_body,
					sm_title, sm_url, sm_identifier, sm_name, sm_reactionsCount,
					sm_sharesCount, sm_activityType, sm_commentCount, sm_account):
		if sm_source.strip() != '':
			observable_app = self.__check_application_name(sm_source.strip())
		else:
			observable_app = None
		sm_timeStamp = self.cleanDate(sm_timeStamp)
		sm_title = self.cleanJSONtext(sm_title)
		sm_body = self.cleanJSONtext(sm_body)
		sm_url = self.cleanJSONtext(sm_url)
		if sm_url != '':
			observable_url = self.__checkUrlAddress(sm_url)
		else:
			observable_url = None
		if (sm_body == '' and sm_source.strip() == ''):
			return None
		
		n_reactions = None
		if sm_reactionsCount.strip():
			n_recations = int()
		
		n_shares = None
		if sm_sharesCount.strip():
			n_shares = int(sm_sharesCount)
		
		n_comments = None
		if sm_commentCount.strip():
			n_comments = int(sm_commentCount)
		
		social_media_activity_object = uco.observable.ObservableObject()
		facet_social_media_activity = drafting.entities.SocialMediaActivityFacet(
			body=sm_body,
			page_title=sm_title,
			author_identifier=sm_identifier,
			author_name=sm_name,
			activity_type=sm_activityType,
			reactions_count=n_reactions,
			shares_count=n_shares,
			comments_count=n_comments,
			account_identifier=sm_account,
			created_time=sm_timeStamp,
			application=observable_app,
			url=observable_url
        )
		social_media_activity_object.append_facets(facet_social_media_activity)
		self.bundle.append_to_uco_object(social_media_activity_object)
		return social_media_activity_object

	def __generateTraceSearched_Item(self, search_id, search_status,
					search_app, search_timestamp, search_value, search_result):
		
		search_value = self.cleanJSONtext(search_value)
		if search_value.strip() == '' and search_result.strip() == '':
			return None
		search_result = self.cleanJSONtext(search_result)
		search_timestamp = self.cleanDate(search_timestamp)
		observable = None
		if not self.__checkSearchedItems(search_value):						
			#observable_app = self.__check_application_name(search_app)
			observable = uco.observable.ObservableObject()
			facet_searched_item = SearchedItem(
			search_value=search_value, search_result=search_result, application=observable_app,
			search_launch_time=search_timestamp)
			observable.append_facets(facet_searched_item)
			self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceWireless_Net(self, wnet_id, wnet_status, wnet_ssid, wnet_bssid):
		wnet_id = wnet_bssid.strip() + '@' + wnet_ssid.strip()
		if wnet_id == '@':
			return None
		else:
			if wnet_id in self.WIRELESS_NET_ACCESS.keys():
				observable = self.WIRELESS_NET_ACCESS.get(wnet_id)
			else:
				observable = uco.observable.ObservableObject()
				facet_wnet_connection = uco.observable.WirelessNetworkConnectionFacet(
					wn_base_station=wnet_bssid,
					wn_ssid=wnet_ssid)
				observable.append_facets(facet_wnet_connection)
				self.bundle.append_to_uco_object(observable)
				self.WIRELESS_NET_ACCESS[wnet_id] = observable
			return observable


	def __generate_trace_message(self, body, id_app, phone_uuid_from, phone_uuid_to,
			time_stamp, status, type):
		time_stamp = self.cleanDate(time_stamp)
		body = self.cleanJSONtext(body)
		if body.strip() == '' and \
			phone_uuid_to == '' and \
			phone_uuid_from == '' :
			return ''
		
		message_object = uco.observable.Message(
    		has_changed=True,
		)
		facet_message = uco.observable.MessageFacet(
			msg_to=phone_uuid_to,
			msg_from=phone_uuid_from,
			message_text=body,
			sent_time=time_stamp,
	        application=id_app,
	        message_type=type
		)
		message_object.append_facets(facet_message)
		self.bundle.append_to_uco_object(message_object)
		return message_object

	def __generateTraceSMSMessageFacet(self, body, id_app, phone_uuid_from, phone_uuid_to,
			time_stamp, status):
		time_stamp = self.cleanDate(time_stamp)
		body = self.cleanJSONtext(body)

		if body.strip() == '' and \
			phone_uuid_to == '' and \
			phone_uuid_from == '' :
			return ''
		
		message_object = uco.observable.ObservableObject()
		sms_message_facet = uco.observable.SMSMessageFacet(
			msg_to=phone_uuid_to,
			msg_from=phone_uuid_from,
			message_text=body,
			sent_time=time_stamp,
	        application=id_app,
	        message_type="SMS")
		message_object.append_facets(sms_message_facet)	
		self.bundle.append_to_uco_object(message_object)
		return message_object


	def __generateTraceSms(self, SMSid, SMSstatus, SMStimeStamp,
							SMSpartyRoles, SMSpartyIdentifiers,
							SMSsmsc, SMSpartyNames, SMSfolder, SMSbody, SMSsource):
		
		for i, sms_id in enumerate(SMSid):
			phone_observable_to = []
			phone_observable_from = None
			for j, sms_party_identifier in enumerate(SMSpartyIdentifiers[i]):
				if sms_party_identifier.strip() != '':
					if sms_party_identifier in self.phone_number_list:
						idx = self.phone_number_list.index(sms_party_identifier)
						#userId = self.phone_number_list[idx]
						phone_party_observable = self.phone_uuid_list[idx]
					else:
						self.phone_number_list.append(sms_party_identifier)
						self.phoneNameList.append(SMSpartyNames[i][j])
						mobileOperator = ""
						phone_party_observable = self.__generate_phone_account_facet(mobileOperator,
							SMSpartyNames[i][j], sms_party_identifier)
						self.phone_uuid_list.append(phone_party_observable)
				
					if SMSpartyRoles[i][j] == 'To':
						phone_observable_from = self.object_phone_owner
						phone_observable_to.append(phone_party_observable)
					else:
						phone_observable_from = phone_party_observable
						phone_observable_to.append(self.object_phone_owner)
			phone_smsc_observable = None
			if SMSsmsc[i].strip() != '':
				if SMSsmsc[i].strip() in self.phone_number_list:
					idx = self.phone_number_list.index(SMSsmsc[i].strip())
					#userId = self.phone_number_list[idx]
					phone_smsc_observable = self.phone_uuid_list[idx]
				else:
					self.phone_number_list.append(SMSsmsc[i].strip())
					self.phoneNameList.append('SMSC')
					mobileOperator = ""
					phone_smsc_observable = self.__generate_phone_account_facet(mobileOperator,
						'SMSC', SMSsmsc[i].strip())
					self.phone_uuid_list.append(phone_smsc_observable)

			if SMSfolder[i] == 'Inbox':
				if phone_observable_from is None:
					phone_observable_from = phone_smsc_observable
			else:
				if phone_observable_to == []:
					phone_observable_to = phone_smsc_observable

			# if self.object_phone_owner is not None:
			# if phone_observable_to is not self.object_phone_owner:
			# phoneUuidTo = phoneUuidTo[0:-1]

			body = self.cleanJSONtext(SMSbody[i])
#--- the xsd:dateTime has the structure YYYY-MM-DDTHH:MM:SS (UTCxxx
#--- the character "/" is not allowed
			#SMStimeStamp[i] = self.cleanDate(SMStimeStamp[i])

			id_app_name = self.__check_application_name("Native")

			#direction = ''
			observable_message = self.__generateTraceSMSMessageFacet(body, id_app_name,
				phone_observable_from, phone_observable_to, SMStimeStamp[i], SMSstatus[i])

			if observable_message is not None:
				self.__generate_chain_of_evidence(sms_id, observable_message)

	def __generate_thread_messages(self, chatTraceId, chat_messages, chat_participants):
		observable = uco.observable.ObservableObject()
		facet_message_thread = uco.observable.MessagethreadFacet(
			messages=chat_messages,
			participants=chat_participants,
		)
		observable.append_facets(facet_message_thread)
		self.bundle.append_to_uco_object(observable)
		return observable

	def __generateTraceTool(self, name, type, creator, version, confList):
		tool_creator_object = uco.identity.Organization(
			name="Cellebrite"
		)
		self.bundle.append_to_uco_object(tool_creator_object)

		tool_acquisition = uco.tool.Tool(
    		name=name,
    		tool_version=version,
    		tool_type=type,
    		tool_creator=tool_creator_object
		)
		self.bundle.append_to_uco_object(tool_acquisition)
		return tool_acquisition

	def __generateTraceURLFullValue(self, URL_Value):
		'''
		It generates the uco-observable:URLFacet Object
		'''
		url_object = uco.observable.ObservableObject()
		facet_url = uco.observable.UrlFacet(url_address=URL_Value)
		url_object.append_facets(facet_url)
		self.bundle.append_to_uco_object(url_object)
		return url_object

	def __generateTraceURL(self, URL_Value):
		
		URL_Value = self.cleanJSONtext(URL_Value)
		startHttp = URL_Value.strip().find('http')
		
		if startHttp > - 1:
			URL_Value = URL_Value[startHttp:]
		uuid = self.__checkUrlAddress(URL_Value)
		return uuid

	def __generateTraceLocation(self, Location):
		"""
		to be included in case_builder classes
		Location = Location.strip()
		if Location in self.LocationList:
			idx = self.LocationList.index(Location)
			uuid = self.LocationIDList[idx]
		else:
			uuid = "kb:" + UFEDtoJSON.__createUUID()
			self.LocationList.append(Location)
			self.LocationIDList.append(uuid)
			object_dict = {
				"@id":uuid,
				"@type":"uco-location:Location",
				"uco-core:hasFacet":[
					{
						"@type":"uco-location:SimpleAddressFacet",
						"uco-location:locality":Location
					}
				]
			}
			object_str = json.dumps(object_dict, indent = 4)
			self.FileOut.write(object_str + ',\n')
		return uuid
		"""

	def __generate_trace_geo_location (self, latitude, longitude, altitude, type):

		geo_location_object = uco.observable.ObservableObject()
		id = latitude + '@' + longitude
		self.LOCATION_lat_long_coordinate[id] = geo_location_object

		latitude_decimal = float(latitude)
		longitude_decimal = float(longitude)
		
		if altitude != '':
			altitude_decimal = float(altitude)
		else:
			altitude_decimal = 0.00

		facet_location = uco.location.LatLongCoordinatesFacet(
			latitude=latitude_decimal,
			longitude=longitude_decimal,
			altitude=altitude_decimal)
		geo_location_object.append_facets(facet_location)
		
		self.bundle.append_to_uco_object(geo_location_object)
		return geo_location_object

	def __generateTraceWebPages(self, WEB_PAGEid, WEB_PAGEstatus, WEB_PAGEsource, WEB_PAGEurl,
				WEB_PAGEtitle, WEB_PAGEvisitCount, WEB_PAGElastVisited):
		"""
			URLHistoryFacet and urlHistoryEntry
		"""
		for i, web_page_id in enumerate(WEB_PAGEid):
			WEB_PAGElastVisited[i] = self.cleanDate(WEB_PAGElastVisited[i])
			observable_app = self.__check_application_name(WEB_PAGEsource[i].strip())
			observable_url = self.__generateTraceURL(WEB_PAGEurl[i])
			title = self.cleanJSONtext(WEB_PAGEtitle[i])
			
			if WEB_PAGEvisitCount[i].strip() == '':
				visit_count = '0'
			else:
				visit_count = WEB_PAGEvisitCount[i]
			visit_count = int(visit_count)
			history_entries = []
			#print(f"WEB_PAGElastVisited = {WEB_PAGElastVisited[i]}")
			#print(f"type WEB_PAGElastVisited = {type(WEB_PAGElastVisited[i])}")
			# if WEB_PAGElastVisited[i]:
			history_entry = {
			    "uco-observable:pageTitle": title,
			    #"uco-observable:lastVisit": WEB_PAGElastVisited[i],
    			"uco-observable:url": observable_url,
    			"uco-observable:visitCount": visit_count,
			}
			# else:
			# 	history_entry = {
			# 	    "uco-observable:pageTitle": title,
	    	# 		"uco-observable:url": observable_url,
	    	# 		"uco-observable:visitCount": visit_count,
			# 	}	
			url_history_entry_object = uco.observable.ObservableObject()
			history_entries.append(history_entry)
			url_history_facet = uco.observable.UrlHistoryFacet(
    			browser=observable_app,
    			history_entries=history_entries
			)
			url_history_entry_object.append_facets(url_history_facet)
			self.bundle.append_to_uco_object(url_history_entry_object)
			
			self.__generate_chain_of_evidence(web_page_id, url_history_entry_object)

	def write_extra_info(self, EXTRA_INFOdictPath, EXTRA_INFOdictSize, EXTRA_INFOdictTableName,
				EXTRA_INFOdictOffset, EXTRA_INFOdictNodeInfoId):
		'''
		Under certain circumstances these data are necessary to rebuild the Chain of Evidence.
		'''
		self.EXTRA_INFOdictPath = EXTRA_INFOdictPath
		self.EXTRA_INFOdictSize = EXTRA_INFOdictSize
		self.EXTRA_INFOdictTableName = EXTRA_INFOdictTableName
		self.EXTRA_INFOdictOffset = EXTRA_INFOdictOffset
		self.EXTRA_INFOdictNodeInfoId = EXTRA_INFOdictNodeInfoId

	def write_contact(self, CONTACTid, CONTACTstatus, CONTACTsource,
            CONTACTname, CONTACTuserIds, CONTACTphoneNums, CONTACTaccount):
		for i, contact in enumerate(CONTACTid):
			for j, phoneNum in enumerate(CONTACTphoneNums[i]):
				if phoneNum.strip() != '':
					self.__checkPhoneNumber(phoneNum.strip(), CONTACTname[i])
			
			if CONTACTuserIds[i][0].strip() != '':
				idApp = self.__check_application_name(CONTACTsource[i])
				self.__checkAccountName(CONTACTuserIds[i][0].strip(), CONTACTname[i], idApp)
					

	def write_header(
		self,
		xml_report: str
	):
		'''
		core:Bundle is the main class that contains all the other classes included in the
		uco-core:object property list.
		'''
		c_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		bundle_created_time = datetime.strptime(c_time, "%Y-%m-%dT%H:%M:%S")
		self.bundle = uco.core.Bundle(
    		description="A Cellebrite XML report generated by UFED PA",
    		name=" ".join(["JSON","LD", "representation", "of", os.path.basename(xml_report)]),
    		specVersion="UCO/CASE 1.3",
    		tag="Artifacts extracted from a mobile device",
    		object_created_time=bundle_created_time
    	)

	def writeLastLine(self):
		'''
		Save a reference to the original standard output.
		'''
		original_stdout = sys.stdout

#-- Change the standard output to the file we created.
		sys.stdout = self.FileOut
		print(self.bundle)

#-- Restore the standard output to its default value
		sys.stdout = original_stdout

	def write_phone_owner(self, phoneOwnerNumber):
		self.phoneOwnerNumber = phoneOwnerNumber
		# data not represented in the XML report
		mobileOperator = ""
		mobileOwnerName = ""
		self.__generateTracePhoneOwner(mobileOperator, mobileOwnerName, phoneOwnerNumber)

	def write_files(self, FILEid, FILEpath, FILEsize, FILEmd5, FILETag,
					FILEtimeCreate, FILEtimeModify, FILEtimeAccess, FILElocalPath,
                    FILEiNodeNumber, FILEiNodeTimeM, FILEownerGID, FILEownerUID,
                    FILEexifLatitudeRef, FILEexifLatitude, FILEexifLongitudeRef,
                    FILEexifLongitude, FILEexifAltitude, FILEexifMake, FILEexifModel):
			self.FILEid = FILEid
			for i, file_id in enumerate(FILEid):
				object_file = self.__generateTraceFile(FILEpath[i], FILEsize[i],
					'MD5', FILEmd5[i],FILETag[i], FILEtimeCreate[i], FILEtimeModify[i],
					FILEtimeAccess[i], FILElocalPath[i], FILEiNodeNumber[i], FILEiNodeTimeM[i],
					FILEownerGID[i], FILEownerUID[i], FILEexifLatitudeRef[i],
					FILEexifLatitude[i], FILEexifLongitudeRef[i], FILEexifLongitude[i],
					FILEexifAltitude[i], FILEexifMake[i], FILEexifModel[i])
				self.FILEuuid[file_id] = object_file
				self.FILEpath[file_id] = FILEpath[i]

	def write_web_bookmark(self, WEB_BOOKMARKid, WEB_BOOKMARKsource, WEB_BOOKMARKtimeStamp,
	    WEB_BOOKMARKpath, WEB_BOOKMARKurl):
		for i, wb_id in enumerate(WEB_BOOKMARKid):
			observable_web_bookmark = self.__generateTraceWebBookmark(wb_id, WEB_BOOKMARKsource[i],
				WEB_BOOKMARKtimeStamp[i], WEB_BOOKMARKpath[i], WEB_BOOKMARKurl[i])

			if observable_web_bookmark:
				pass

	def write_bluetooth(self, BLUETOOTHid, BLUETOOTHstatus, BLUETOOTHvalues):
				
		for i, bt_id in enumerate(BLUETOOTHid):
			observable_bluetooth = self.__generateTraceBluetooth(bt_id,
					BLUETOOTHstatus[i], BLUETOOTHvalues[i])
			
			if observable_bluetooth:
				self.__generateTraceRelation(self.DEVICE_object, observable_bluetooth,
					                     'Connected_To', None, None, None, None)
				self.__generate_chain_of_evidence(bt_id, observable_bluetooth)
			
	def write_calendar(self, CALENDARid, CALENDARstatus, CALENDARcategory, CALENDARsubject,
                    CALENDARdetails, CALENDARstartDate, CALENDARendDate, CALENDARrepeatUntil,
                    CALENDARrepeatDay, CALENDARrepeatInterval):
		for i, calendar_id in enumerate(CALENDARid):
			observable_calendar = self.__generateTraceCalendar(calendar_id,
					CALENDARstatus[i], CALENDARcategory[i], CALENDARsubject[i],
					CALENDARdetails[i], CALENDARstartDate[i], CALENDARendDate[i],
					CALENDARrepeatUntil[i], CALENDARrepeatDay[i], CALENDARrepeatInterval[i])
			
			self.__generate_chain_of_evidence(calendar_id, observable_calendar)

	def write_cell_site(self, CELL_SITEid, CELL_SITEstatus, CELL_SITElongitude,
					CELL_SITElatitude, CELL_SITEtimeStamp, CELL_SITEmcc,
                    CELL_SITEmnc, CELL_SITElac, CELL_SITEcid, CELL_SITEnid,
                    CELL_SITEbid, CELL_SITEsid):
		for i, cell_site_id in enumerate(CELL_SITEid):
			observable_cell_site = self.__generate_trace_cell_site(cell_site_id, CELL_SITEstatus[i],
					CELL_SITElongitude[i], CELL_SITElatitude[i], CELL_SITEtimeStamp[i],
					CELL_SITEmcc[i], CELL_SITEmnc[i], CELL_SITElac[i], CELL_SITEcid[i],
					CELL_SITEnid[i], CELL_SITEbid[i], CELL_SITEsid[i])
			if observable_cell_site is not None:
				self.__generateTraceRelation(self.DEVICE_object, observable_cell_site,
					'Connected_To', '', '', CELL_SITEtimeStamp[i], None)
				self.__generate_chain_of_evidence(cell_site_id, observable_cell_site)

	def write_chat(self, CHATid, CHATstatus, CHATsource, CHATpartyIdentifiers, CHATpartyNames,
                CHATmsgIdentifiersFrom, CHATmsgNamesFrom, CHATmsgBodies, CHATmsgStatuses, CHATmsgOutcomes,
                CHATmsgTimeStamps, CHATmsgAttachmentFilenames, CHATmsgAttachmentUrls):
		for i, chat_id in enumerate(CHATid):
			appSource = CHATsource[i].strip().lower()
			idAppIdentity = self.__check_application_name(appSource)
			CHATid_account_to = []
			CHATid_account_from = ''
#--- If the CHAT doesn't have Participants, it is ignored
			if len(CHATpartyIdentifiers) <= i:
				continue

			if len(CHATpartyIdentifiers[i]) == 0:
				continue

			for j, chat_party_id in enumerate(CHATpartyIdentifiers[i]):
				idChatAccount = self.__checkChatParticipant(chat_party_id,
					CHATpartyNames[i][j], CHATsource[i], idAppIdentity)
#--- in the account_to list, also the CHATmsgIdentifiersFrom is added
				CHATid_account_to.append(idChatAccount)
			CHATthread = []
#--- CHATmsgBodies[i] is the list of the messages of the same thread,
#--- the j index iterates over all the messages within the i-th CHAT
			for j, chat_msg_body in enumerate(CHATmsgBodies[i]):

				CHATmsgFrom = CHATmsgIdentifiersFrom[i][j].strip()
				if len(CHATmsgIdentifiersFrom[i]) > 0:
					CHATid_account_from = self.__checkChatParticipant(CHATmsgFrom,
						CHATmsgNamesFrom[i][j], CHATsource[i], idAppIdentity)
				else:
					CHATid_account_from = self.__checkChatParticipant('MSG_IDENTIFIER_EMPTY',
						'MSG_NAME_EMPTY', CHATsource[i], idAppIdentity)

				chat_observable = self.__generateTraceChat(chat_msg_body, idAppIdentity,
					CHATmsgTimeStamps[i][j], CHATid_account_from, CHATid_account_to,
					CHATmsgStatuses[i][j], CHATmsgOutcomes[i][j],
					'', CHATmsgAttachmentFilenames[i][j],
					CHATmsgAttachmentUrls[i][j])

				CHATthread.append(chat_observable)
				if CHATmsgAttachmentFilenames[i][j].strip() != '':
					CHATattachmentFiles = CHATmsgAttachmentFilenames[i][j].split('###')
					for idx, chat_attachment_file in enumerate(CHATattachmentFiles):
						for key in self.FILEpath:
							if self.FILEpath[key].find(chat_attachment_file) > - 1:
								self.__generateTraceRelation(self.FILEuuid[key],
									chat_observable, 'Attached_To', '', '', None, None);
								break
#--- If there are not messages for this Chat or no ChatAccount has been generated,
#--- the ThreadMessage is skipped and the Chain of evidence is ignored
			if (len(CHATthread) == 0) or (len(CHATid_account_to) == 0):
				pass
			else:
				uuidThread = self.__generate_thread_messages(chat_id, CHATthread,
								CHATid_account_to)
				self.__generate_chain_of_evidence(chat_id, uuidThread)

	def write_cookie(self, COOKIEid, COOKIEstatus, COOKIEsource, COOKIEname,
                    COOKIEvalue, COOKIEdomain, COOKIEcreationTime, COOKIElastAccessTime,
                    COOKIEexpiry):
		for i, cookie_id in enumerate(COOKIEid):
			observable_cookie = self.__generate_trace_cookie(cookie_id, COOKIEstatus[i],
					COOKIEsource[i], COOKIEname[i], COOKIEvalue[i],
					COOKIEdomain[i], COOKIEcreationTime[i], COOKIElastAccessTime[i],
					COOKIEexpiry[i])
			
			self.__generate_chain_of_evidence(cookie_id, observable_cookie)

	def write_installed_app(self, INSTALLED_APPid, INSTALLED_APPstatus,
            INSTALLED_APPname, INSTALLED_APPversion , INSTALLED_APPidentifier, INSTALLED_APPpurchaseDate):

		for i, app_id in enumerate(INSTALLED_APPid):
			observable_app = self.__generateTraceInstalledApp(app_id,
			    INSTALLED_APPstatus[i], INSTALLED_APPname[i],
		        INSTALLED_APPversion[i], INSTALLED_APPidentifier[i], INSTALLED_APPpurchaseDate[i])

			if observable_app:
				self.__generate_chain_of_evidence(app_id, observable_app)

	def write_device_event(self, DEVICE_EVENTid, DEVICE_EVENTstatus,
                    DEVICE_EVENTtimeStamp, DEVICE_EVENTeventType, DEVICE_EVENTvalue):
		for i, device_event_id in enumerate(DEVICE_EVENTid):
			observable_event = self.__generateTraceDeviceEvent(device_event_id,
					DEVICE_EVENTstatus[i], DEVICE_EVENTtimeStamp[i],
					DEVICE_EVENTeventType[i], DEVICE_EVENTvalue[i])
			
			self.__generate_chain_of_evidence(device_event_id, observable_event)

	def write_email(self, EMAILid, EMAILstatus, EMAILsource, EMAILidentifierFROM,
				EMAILidentifiersTO, EMAILidentifiersCC, EMAILidentifiersBCC,
                EMAILbody, EMAILsubject, EMAILtimeStamp, EMAILattachmentsFilename):
		for i, email_id in enumerate(EMAILid):
			self.__generateTraceEmail(email_id, EMAILstatus[i], EMAILsource[i],
				EMAILidentifierFROM[i], EMAILidentifiersTO[i],
				EMAILidentifiersCC[i], EMAILidentifiersBCC[i], EMAILbody[i],
				EMAILsubject[i], EMAILtimeStamp[i], EMAILattachmentsFilename[i])

	def write_instant_message(self, INSTANT_MSGid, INSTANT_MSGstatus, INSTANT_MSGsource,
			INSTANT_MSGtimeStamp, INSTANT_MSGfromIdentifier, INSTANT_MSGfromName,
            INSTANT_MSGtoIdentifier, INSTANT_MSGtoName, INSTANT_MSGsubject, INSTANT_MSGbody,
            INSTANT_MSGfolder, INSTANT_MSGtype, INSTANT_MSGapplication):
		for i, i_msg_id in enumerate(INSTANT_MSGid):
			if INSTANT_MSGsource[i].find('Native') > -1:
				idx = self.appNameList.index("Native")
				observable_app = self.appObjectList[idx]
			else:
				if INSTANT_MSGsource[i].strip() in self.appNameList:
					idx = self.appNameList.index(INSTANT_MSGsource[i].strip())
					observable_app = self.appObjectList[idx]
				else:
					observable_app = self.__generateTraceAppName(INSTANT_MSGsource[i].strip())
					self.appNameList.append(INSTANT_MSGsource[i].strip())
					self.appObjectList.append(observable_app)

			i_msg_from_identifier = INSTANT_MSGfromIdentifier[i].strip()
			
			observable_from = None
			if i_msg_from_identifier != '' :
				if i_msg_from_identifier in self.phone_number_list:
					idx = self.phone_number_list.index(i_msg_from_identifier)
					observable_from = self.phone_uuid_list[idx]
				else:
					self.phone_number_list.append(i_msg_from_identifier)
					self.phoneNameList.append(INSTANT_MSGfromName[i])
					mobileOperator = ""
					observable_from = self.__generate_phone_account_facet(mobileOperator,
							INSTANT_MSGfromName[i], i_msg_from_identifier)
					self.phone_uuid_list.append(observable_from)
			
			list_TO = INSTANT_MSGtoIdentifier[i].split('@@@')
			observables_msg_to = []
			for j, item in enumerate(list_TO):
				if item.strip() != '':
					if item in self.phone_number_list:
						idx = self.phone_number_list.index(item.strip())
						observable_to = self.phone_uuid_list[idx]
					else:
						self.phone_number_list.append(item.strip())
						self.phoneNameList.append(INSTANT_MSGtoName[i])
						mobileOperator = ""
						observable_to = self.__generate_phone_account_facet(mobileOperator,
						INSTANT_MSGtoName[i], item.strip())
						self.phone_uuid_list.append(observable_to)
					observables_msg_to.append(observable_to)
						
			observable_message = self.__generate_trace_message(INSTANT_MSGbody[i],
				observable_app, observable_from, observables_msg_to, INSTANT_MSGtimeStamp[i],
				INSTANT_MSGstatus[i], 'Instant Message')
			if observable_message is not None:
				self.__generate_chain_of_evidence(i_msg_id, observable_message)

	def write_location_device(self, LOCATIONid, LOCATIONstatus, LOCATIONlongitude,
					LOCATIONlatitude, LOCATIONaltitude, LOCATIONtimeStamp,
					LOCATIONcategory):
		    
		for i, location_id in enumerate(LOCATIONid):
			observable_location= self.__generateTraceLocationDevice(location_id, LOCATIONstatus[i],
					LOCATIONlongitude[i], LOCATIONlatitude[i], LOCATIONaltitude[i],
					LOCATIONtimeStamp[i], LOCATIONcategory[i], i)
			
			if observable_location is not None:
				self.__generateTraceRelation(self.DEVICE_object, observable_location,
					'Mapped_By', '', '', LOCATIONtimeStamp[i], None)
				self.__generate_chain_of_evidence(location_id, observable_location)

	def write_social_media_activity(self, SOCIAL_MEDIAid, SOCIAL_MEDIAstatus,
            SOCIAL_MEDIAsource, SOCIAL_MEDIAtimeStamp,
            SOCIAL_MEDIAbody, SOCIAL_MEDIAtitle, SOCIAL_MEDIAurl, SOCIAL_MEDIAidentifier,
            SOCIAL_MEDIAname, SOCIAL_MEDIAreactionsCount, SOCIAL_MEDIAsharesCount,
            SOCIAL_MEDIAactivityType, SOCIAL_MEDIAcommentCount,
            SOCIAL_MEDIAaccount):
		for i, social_media_item_id in enumerate(SOCIAL_MEDIAid):
			observable_social= self.__generateTraceSocialMedia_Item(social_media_item_id,
				SOCIAL_MEDIAstatus[i], SOCIAL_MEDIAsource[i], SOCIAL_MEDIAtimeStamp[i],
				SOCIAL_MEDIAbody[i], SOCIAL_MEDIAtitle[i], SOCIAL_MEDIAurl[i],
				SOCIAL_MEDIAidentifier[i], SOCIAL_MEDIAname[i],
				SOCIAL_MEDIAreactionsCount[i], SOCIAL_MEDIAsharesCount[i],
				SOCIAL_MEDIAactivityType[i], SOCIAL_MEDIAcommentCount[i],
				SOCIAL_MEDIAaccount[i])
			if observable_social is not None:
				self.__generate_chain_of_evidence(social_media_item_id, observable_social)

	def write_searched_item(self, SEARCHED_ITEMid, SEARCHED_ITEMstatus, SEARCHED_ITEMsource,
					SEARCHED_ITEMtimeStamp, SEARCHED_ITEMvalue, SEARCHED_ITEMsearchResult):
		for i, search_item_id in enumerate(SEARCHED_ITEMid):
			
			if SEARCHED_ITEMvalue[i].strip():
				if not self.__checkSearchedItems(SEARCHED_ITEMvalue[i].strip()):	
					history_entries = []
					#print(f"WEB_PAGElastVisited = {WEB_PAGElastVisited[i]}")
					#print(f"type WEB_PAGElastVisited = {type(WEB_PAGElastVisited[i])}")
					# if WEB_PAGElastVisited[i]:
					history_entry = {
					    "uco-observable:keywordSearchTerm": SEARCHED_ITEMvalue[i],
					}
					url_history_entry_object = uco.observable.ObservableObject()
					history_entries.append(history_entry)
					url_history_facet = uco.observable.UrlHistoryFacet(
		    			history_entries=history_entries
					)
					url_history_entry_object.append_facets(url_history_facet)
					self.bundle.append_to_uco_object(url_history_entry_object)
					self.__generate_chain_of_evidence(search_item_id, url_history_entry_object)

	def write_web_pages(self, WEB_PAGEid, WEB_PAGEstatus, WEB_PAGEsource, WEB_PAGEurl,
				WEB_PAGEtitle, WEB_PAGEvisitCount, WEB_PAGlastVisited):
		self.__generateTraceWebPages(WEB_PAGEid, WEB_PAGEstatus, WEB_PAGEsource, WEB_PAGEurl,
				WEB_PAGEtitle, WEB_PAGEvisitCount, WEB_PAGlastVisited)

	def write_wireless_net(self, WIRELESS_NETid, WIRELESS_NETstatus, WIRELESS_NETlongitude,
					WIRELESS_NETlatitude, WIRELESS_NETtimeStamp, WIRELESS_NETlastConnection,
                    WIRELESS_NETbssid, WIRELESS_NETssid):
		
		for i, wireless_net_id in enumerate(WIRELESS_NETid):
			observable_wnet= self.__generateTraceWireless_Net(wireless_net_id,
				WIRELESS_NETstatus[i], WIRELESS_NETbssid[i], WIRELESS_NETssid[i])
			
			if observable_wnet is not None:
				wnet_timeStamp = self.cleanDate(WIRELESS_NETtimeStamp[i])
				wnet_last_connection = self.cleanDate(WIRELESS_NETlastConnection[i])
				self.__generateTraceRelation(self.DEVICE_object, observable_wnet, 'Connected_To',
					'', '', wnet_timeStamp, wnet_last_connection)
				observable_location = self.__checkGeoCoordinates(WIRELESS_NETlatitude[i],
					WIRELESS_NETlongitude[i], '', 'Wireless Network')
				if observable_location:
					self.__generateTraceRelation(observable_wnet, observable_location,
						'Mapped_To', '', '', None, None)
				self.__generate_chain_of_evidence(wireless_net_id, observable_wnet)

	def write_SMS(self, SMSid, SMSstatus, SMStimeStamp, SMSpartyRoles,
					SMSpartyIdentifiers, SMSsmsc, SMSpartyNames, SMSfolder, SMSbody, SMSsource):
		self.__generateTraceSms(SMSid, SMSstatus, SMStimeStamp, SMSpartyRoles,
					SMSpartyIdentifiers, SMSsmsc, SMSpartyNames, SMSfolder, SMSbody, SMSsource)

	def write_context_ufed(self, ufedVersionText, deviceReportCreateTime,
		deviceExtractionStartTime, deviceExtractionEndTime, examinerNameText,
		imagePath, imageSize, imageMetadataHashSHA, imageMetadataHashMD5):

		self.__generateContextUfed(ufedVersionText, deviceReportCreateTime,
			deviceExtractionStartTime, deviceExtractionEndTime, examinerNameText,
			imagePath, imageSize, imageMetadataHashSHA, imageMetadataHashMD5)
