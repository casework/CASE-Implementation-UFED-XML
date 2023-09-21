#!/usr/bin/env python3

#---
#	CASE_generate.py:    
#		generate the JSON file pieces (Observables) that compose the final JSON-LD CASE file
#

import json
from datetime import datetime
from uuid import uuid4
from datetime import datetime

class ObjectCore(dict):

    def __init__(self):
        super().__init__()  

    def _set_properties_str(self, **kwargs):
        for key, var in kwargs.items():
            if isinstance(var, str):
                self[key] = var
            else:
                self.__handle_var_type_errors(key, var, 'str')    

    def _set_properties_float(self, **kwargs):
        for key, var in kwargs.items():
            if isinstance(var, float):
                self[key] = {"@type": "xsd:decimal", "@value": str(var)}
            else:
                self.__handle_var_type_errors(key, var, 'float')

    def _set_properties_int(self, **kwargs):
        for key, var in kwargs.items():
            if isinstance(var, int):
                self[key] = {"@type": "xsd:integer", "@value": str(var)}
            else:
                self.__handle_var_type_errors(key, var, 'int')

    def _set_properties_bool(self, **kwargs):
        for key, var in kwargs.items():
            if isinstance(var, bool):
                self[key] = {"@type": "xsd:boolean", "@value": var}
            else:
                self.__handle_var_type_errors(key, var, 'bool') 

    def _set_properties_date_time(self, **kwargs):
        for key, var in kwargs.items():
            if isinstance(var, datetime):
                tz_info = var.strftime("%z")
                iso_format = var.isoformat() if tz_info else var.isoformat() + '+00:00'
                self[key] = {"@type": "xsd:dateTime", "@value": iso_format}
            else:
                self.__handle_var_type_errors(key, var, 'date time') 

    def _set_properties_id_reference(self, **kwargs):
        for key, var in kwargs.items():
            if var is not None:
                self[key] = {'@id': var.get_id()} 

    def _set_properties_list_id_reference(self, **kwargs):
        for key, var in kwargs.items():
            if var is not None:
                self[key] = [{'@id': item.get_id()} for item in var]

    def _set_properties_list_id_reference_array(self, **kwargs):
        for key, var in kwargs.items():
            if var is not None:
                # print(f"key={key}")
                # print(f"var={var}")
                self[key] = [{'@id': var.get_id()}]

    def __str__(self):
        return json.dumps(self, indent=4)

    def __handle_var_type_errors(self, var_name, var_val, expected_type):
        if var_val is None:
            pass
        else:
            print(f"Value provided for {var_name} is not of type {expected_type}: value provided: {var_val}")
            raise TypeError

    def _add_reference_list_vars(self, **kwargs):
        pass 


    def get_id(self):
        return self["@id"]

    def append_to_uco_object(self, *args):
        for item in args:
            #self[self.root].append(item)
            self["uco-core:object"].append(item)            

class Bundle(ObjectCore):
		
        def __init__(self, uco_core_name=None, spec_version=None, description=None, 
            root="uco-core:object"):
            """
            The header of the JSON and the CASE Object container (root) of Observables.
            """
            super().__init__()
            #self.build = [] # ???
            case_identifier = 'bundle-' + str(uuid4())
            self["@context"] = {
                "@vocabulary":"http://example.org/kb/",
                "kb": "http://example.org/kb/",
                "drafting":"http://example.org/ontology/drafting/",
                "co": "http://purl.org/co/",                
                "case-investigation":"https://ontology.caseontology.org/case/investigation/",
                "uco-action":"https://ontology.unifiedcyberontology.org/uco/action/",
                "uco-core":"https://ontology.unifiedcyberontology.org/uco/core/",
                "uco-identity":"https://ontology.unifiedcyberontology.org/uco/identity/",
                "uco-role":"https://ontology.unifiedcyberontology.org/uco/role/",
                "uco-location":"https://ontology.unifiedcyberontology.org/uco/location/",
                "uco-observable":"https://ontology.unifiedcyberontology.org/uco/observable/",
                "uco-tool":"https://ontology.unifiedcyberontology.org/uco/tool/",
                "uco-types":"https://ontology.unifiedcyberontology.org/uco/types/",
                "uco-vocabulary":"https://ontology.unifiedcyberontology.org/uco/vocabulary/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",            
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            }

            self["@type"] = "uco-core:Bundle"
            # self._set_properties_str(**{"uco-core:account_name": uco_core_name,
            #     'uco-core:specVersion': spec_version,
            #     'uco-core:description': description,
            #     '@id': case_identifier})
            self._set_properties_str(**{'@id': case_identifier})
            self.root = root
            self[self.root] = list()

            #def append_object_to_root(self, *args):
             #for items in args:
               #self["uco-core:object"].append(item)

class ObjectFacet(ObjectCore):
    def __init__(self):
        super().__init__()
        # each Facet/@type require to have IRIs (`@id`s)
        self["@id"] = "kb:" + str(uuid4())


class ObjectObservable(ObjectCore):

    def __init__(self, object_class="uco-observable:ObservableObject"):
        """
        An observable object contains Facet, a group of unique features that characterises a 
        Cyber item / Digital vestige.
        :param facets: the dictionary representing the Cyber item
        """
        super().__init__()   
        self["@id"] = "kb:" + str(uuid4())           
        self["@type"] = object_class
        self["uco-core:hasFacet"] = list()

    def append_facets(self, *facets):
        for facet in facets:
            self["uco-core:hasFacet"].append(facet)


class ObjectSpecial(ObjectCore):
    def __init__(self):
        super().__init__()
        self["@id"] = "kb:" + str(uuid4())

class Relationship(ObjectSpecial):	  
    def __init__(self, source=None, target=None, kind_of_relationship=None, start_time=None, end_time=None, 
        directional=None):
        super().__init__()
        self["@type"] = "uco-observable:ObservableRelationship"
        self._set_properties_str(**{"uco-core:kindOfRelationship": kind_of_relationship})
        self._set_properties_bool(**{"uco-core:isDirectional": directional})
        self._set_properties_date_time(**{"uco-observable:startTime": start_time,
            "uco-observable:endTime": end_time,
            })
        self._set_properties_id_reference(**{"uco-core:source": source,
            "uco-core:target": target})

class ProvenanceRecord(ObjectSpecial):
    def __init__(self, exhibit_number=None, uco_core_objects=None):
        super().__init__()
        self['@type'] = 'case-investigation:ProvenanceRecord'
        self._set_properties_str(**{"case-investigation:exhibitNumber": exhibit_number})
        self._set_properties_list_id_reference(**{"uco-core:object": uco_core_objects})

class ObjectInfo(ObjectCore):

    def __init__(self, name="", version="", description=""):
        """
        An observable object contains Facet, a group of unique features that characterises a 
        Cyber item / Digital vestige. This is for storing info about name,
        description and version o fthe bundle        
        """
        super().__init__()   
        self["@id"] = "kb:" + str(uuid4())           
        self["@type"] = "uco-observable:ObservableObject" 
        self["uco-core:name"] = name 
        self["uco-core:description"] = description
        self["rdfs:comment"]  = "version: " + version        

class Account(ObjectFacet):

    def __init__(self, identifier=None, is_active=True, issuer_id=None):
        """
        Used to represent user accounts
        :param is_active: Active unless specified otherwise (False)
        :param identifier: The idenitifier of the account (like a Skype username)
        :param issuer_id: The id of issuing body for application
                          (e.g., kb:organization-skypeapp-cc44c2ae-bdd3-4df8-9ca3-1f58d682d62b)
        """
        super().__init__()
        self._set_properties_str(**{"@type": "uco-observable:AccountFacet",
			"uco-observable:accountIdentifier": identifier})
        self._set_properties_id_reference(**{"uco-observable:accountIssuer": issuer_id})

        self._set_properties_bool(**{"uco-observable:isActive": is_active})


class ContentData(ObjectFacet):

    def __init__(self, byte_order=None, magic_number=None, mime_type=None, size_bytes=None, data_payload=None,
                 entropy=None, is_encrypted=None, hash_method=None, hash_value=None):
        """
        The characteristics of a block of digital data.
        :param byte_order: Byte order of data. Example - "BigEndian"
        :param magic_number: The magic phone_number of a file
        :param mime_type: The mime type of a file. Example - "image/jpg"
        :param size_bytes: A phone_number representing the size of the content
        :param data_payload: A base64 representation of the data
        :param entropy: The entropy value for the data
        :param is_encrypted: A boolean True/False, if encrypted or not.
        :param hash_method: The algorithm used to calculate the hash value
        :param hash_value: The cryptographic hash of this content
        """
        super().__init__()
        self["@type"] = "uco-observable:ContentDataFacet"
        self._set_properties_str(**{"uco-observable:byteOrder": byte_order,
                          "uco-observable:magicNumber": magic_number,
                          "uco-observable:mimeType": mime_type,
                          "uco-observable:dataPayload": data_payload,
                          "uco-observable:entropy": entropy,
                          "uco-observable:sizeInBytes": size_bytes,
                          "uco-observable:isEncrypted": is_encrypted})

        if hash_method is not None or hash_value is not None or hash_value != "-":
            data = {"@type": "uco-types:Hash", "@id": "kb:" + str(uuid4())}
            if hash_method is not None:
                data["uco-types:hashMethod"] = {"@type": "uco-vocabulary:HashNameVocab", 
                "@value": hash_method}
            if hash_value is not None:
                data["uco-types:hashValue"] = {"@type": "xsd:hexBinary", "@value": hash_value}
            self["uco-observable:hash"] = [data]


class Application(ObjectFacet):

    def __init__(self, app_name=None, app_identifier=None, installed_version_history=None, num_launches=None, os=None, version=None):
        """
        A simple application
        :param app_name: Name of application (e.g. Native, Facebook, WhatsApp, etc.)
        """
        super().__init__()
        self["@type"] = "uco-observable:ApplicationFacet"
        self._set_properties_str(**{"uco-core:name": app_name,
            "uco-observable:applicationIdentifier": app_identifier,
            "uco-observable:version": version,
            "uco-observable:operatingSystem": os})
        self._set_properties_int(**{"uco-observable:numberOfLaunches": num_launches})
        self._set_properties_id_reference(**{"uco-observable:installedVersionHistory": installed_version_history})                                    

class ApplicationVersion(ObjectFacet):
    """
    A simple application version to manage the installed application
    :param install_date: The date when the application was installed/purchased on the device
    """
    def __init__(self, install_date):
        """
        A simple application
        :param install_date: installation date of an application
        """
        super().__init__()
        self["@type"] = "uco-observable:ApplicationVersion"
        self._set_properties_date_time(**{"uco-observable:installDate": install_date})    
    
class DataRange(ObjectFacet):

    def __init__(self, range_offset=None, range_size=None):
        """
        A data range facet is a grouping of characteristics unique to a particular contiguous scope
        within a block of digital data
        :param range_offset: location in data at which the contiguous data starts
        :param range_size: the length of the data starting at the offset point
        """
        super().__init__()
        self["@type"] = "uco-observable:DataRangeFacet"
        self._set_properties_str(**{"uco-observable:rangeOffset": range_offset,
                          "uco-observable:rangeSize": range_size})


class Device(ObjectFacet):

    def __init__(self, device_type=None, manufacturer=None, model=None, serial=None):
        """
        Characteristics of a piece of electronic equipment.
        :param device_type: The type of device (e.g., "camera")
        :param manufacturer: The producer of the device (e.g., "Canon")
        :param model: The model of the device (e.g., "Powershot SX540")
        :param serial: The serial phone_number of the device (e.g., "1296-3219-8792-CL918")
        """
        super().__init__()
        self["@type"] = "uco-observable:DeviceFacet"
        self._set_properties_str(**{"uco-observable:deviceType": device_type,
                          "uco-observable:manufacturer": manufacturer,
                          "uco-observable:model": model,
                          "uco-observable:serialNumber": serial})


class WifiAddress(ObjectFacet):

    def __init__(self, wifi_mac_address=None):
        """
        :param wifi_mac_address: The wifi mac address of a device (EG: 11:54:00:bc:c8:ba)
        """
        super().__init__()
        self["@type"] = "uco-observable:WifiAddressFacet"
        self._set_properties_str(**{"uco-observable:addressValue": wifi_mac_address})


class BrowserBookmark(ObjectFacet):
    def __init__(self, bookmark_source=None, url=None, bookmark_path=None, bookmark_accessed_time=None):
        """
        :param source:
        :param url:
        :param path:
        :param manually_entered_count:
        :param accessed_time: An observable object with a URLFacet
        """
        super().__init__()
        
        self['@type'] = 'uco-observable:BrowserBookmarkFacet'

        self._set_properties_str(**{'uco-observable:bookmarkPath': bookmark_path})                                
        self._set_properties_date_time(**{'uco-observable:observableCreatedTime': bookmark_accessed_time})                                      
        self._set_properties_id_reference(**{'uco-observable:application':bookmark_source, 'uco-observable:urlTargeted': url})
        
class BluetoothAddress(ObjectFacet):

    def __init__(self, name=None, address=None):
        """
        :param name:
        :param address: The Bluetooth address value (e.g. "D4:A3:3D:B5:F4:6C")
        """
        super().__init__()
        self["@type"] = "uco-observable:BluetoothAddressFacet"
        self._set_properties_str(**{'uco-core:name': name,
                          'uco-observable:addressValue': address})


class UrlHistory(ObjectFacet):

    def __init__(self, browser=None, history_entries=None):
        """
        :param browser_info: An observable object containing a URLHistoryFacet
        :param history_entries: A list of URLHistoryEntry types
        """

        super().__init__()
        self["@type"] = "uco-observable:URLHistoryFacet"
        self._set_properties_id_reference(**{'uco-observable:browserInformation': browser})        
        #self.append_history_entries(history_entries)

    #def append_history_entries(self, entries):
        #"""
        #Used to add history entries to this URL History facet
        #:param args: A single/tuple of URLHistoryEntry class types
        #"""
        ##for entry in entries:
        #self["uco-core:hasFacet"].append(history_entries)        


class UrlHistoryEntry(ObjectFacet):

    def __init__(self, first_visit=None, last_visit=None, expiration_time=None, manually_entered_count=None, url=None,
                 user_profile=None, page_title=None, referrer_url=None, visit_count=None, keyword_search_term=None,
                 allocation_status=None, browser=None):
        """
        :param first_visit:
        :param last_visit:
        :param expiration_time:
        :param manually_entered_count:
        :param url: An observable object with a URLFacet
        :param user_profile:
        :param page_title:
        :param referrer_url:
        :param visit_count:
        :param keyword_search_term:
        :param allocation_status:
        """

        super().__init__()
        
        self['@type'] = 'uco-observable:URLHistoryFacet'
        
        #self._set_properties_id_reference(**{'uco-observable:browserInformation': browser}) 
        self['uco-observable:browserInformation'] = {'@id': browser.get_id()}         

        # self._set_properties_str(**{'uco-observable:userProfile': user_profile,  # todo: referral?
        #         'uco-observable:pageTitle': page_title,
        #         'uco-observable:referrerUrl': referrer_url,
        #         'uco-observable:keywordSearchTerm': keyword_search_term,
        #         'uco-observable:allocationStatus': allocation_status})        
        # self._set_properties_int(**{'uco-observable:visitCount': visit_count,
        #          'uco-observable:manuallyEnteredCount': manually_entered_count})
        # self._set_properties_date_time(**{'uco-observable:firstVisit': first_visit,
        #                        'uco-observable:lastVisit': last_visit,
        #                        'uco-observable:expirationTime': expiration_time})
        # self._set_properties_id_reference(**{'uco-observable:url': url})
        
        
        if first_visit:
            tz_info = first_visit.strftime("%z")
            first_iso_format = first_visit.isoformat() if tz_info else first_visit.isoformat() + '+00:00'
        else:
            first_iso_format = '1900-01-01T08:00:00+00:00'

        if last_visit:
            tz_info = last_visit.strftime("%z")
            last_iso_format = last_visit.isoformat() if tz_info else last_visit.isoformat() + '+00:00'
        else:
            last_iso_format = '1900-01-01T08:00:00+00:00'

        self['uco-observable:urlHistoryEntry'] = []
        self['uco-observable:urlHistoryEntry'].append(
            {'@id': "kb:" + str(uuid4()),
            '@type': 'uco-observable:URLHistoryEntry',
            'uco-observable:firstVisit': {"@type": "xsd:dateTime", "@value": first_iso_format},
            'uco-observable:lastVisit': {"@type": "xsd:dateTime", "@value": last_iso_format},
            'uco-observable:pageTitle': page_title,  
            'uco-observable:url': {'@id': url.get_id()}, 
            'uco-observable:visitCount': {"@type": "xsd:integer", "@value": visit_count},
            'uco-observable:allocationStatus': allocation_status,
            'uco-observable:keywordSearchTerm': keyword_search_term})


class Url(ObjectFacet):

    def __init__(self, url_address=None, url_port=None, url_host=None, url_fragment=None, url_password=None,
                 url_path=None, url_query=None, url_scheme=None, url_username=None):
        """
        :param url_address: an address of a url (i.e. google.ie)
        :param url_port: a tcp or udp port of a url for example 3000
        :param url_host: the Ip address of a host that was requested (e.g.192.168.1.1 could be your home router)
        :param url_fragment: A fragment of a url pointing to a specific resource (i.e  subdomain=api)
        :param url_password: A password that may be used in authentication scheme for accessing restricted resources
        :param url_path: the location that may have resources available e.g. /chatapp
        :param url_query: a query that may be used with a resource such as an api e.g. ?health
        :param url_scheme:  Identifies the type of URL. (e.g. ssh://)
        :param url_username: A username that may be required for authentication for a specific resource. (login)
        """
        super().__init__()
        self["@type"] = "uco-observable:URLFacet"
        self._set_properties_str(**{"uco-observable:fullValue": url_address,
                          "uco-observable:host": url_host,
                          "uco-observable:fragment": url_fragment,
                          "uco-observable:password": url_password,
                          "uco-observable:path": url_path,
                          "uco-observable:query": url_query,
                          "uco-observable:scheme": url_scheme,
                          "uco-observable:userName": url_username})
        self._set_properties_int(**{"uco-observable:port": url_port})


class RasterPicture(ObjectFacet):

    def __init__(self, camera_id=None, bits_per_pixel=None, picture_height=None, picture_width=None,
                 image_compression_method=None, picture_type=None):
        """
        This CASEObject represents the contents of a file or device
        :param camera_id: An observable cyberitem
        :param bits_per_pixel: The phone_number (integer) of bits per pixel
        :param picture_height: The height of a picture (integer)
        :param picture_width: The width of a picture (integer)
        :param image_compression_method: The compression method used
        :param picture_type: The type of picture ("jpg", "png" etc.)
        """
        super().__init__()
        self["@type"] = "uco-observable:RasterPictureFacet"
        self._set_properties_str(**{"uco-observable:imageCompressionMethod": image_compression_method,
                          "uco-observable:pictureType": picture_type,
                          "uco-observable:pictureHeight": picture_height,
                          "uco-observable:pictureWidth": picture_width,
                          "uco-observable:bitsPerPixel": bits_per_pixel})
        self._set_properties_id_reference(**{"uco-observable:camera": camera_id})


class PhoneCall(ObjectFacet):

    def __init__(self, call_type=None, start_time=None, application=None, call_from=None,
                 call_to=None, call_duration=None, allocation_status=None):
        """
        :param call_type: incoming outgoing etc
        :param start_time: the time at which the device registered the call as starting
        :param application: ObjectObservable with call-application (e.g. WhatsApp) facet-info
        :param call_from: ObjectObservable with person/caller facet-info
        :param call_to: ObjectObservable with person/caller facet-info
        :param call_duration: how long the call was registedred on the device as lasting in minutes (E.G. 60)
        :param allocation_status: The allocation status of the record of the call i.e intact for records that are
        present on the device
        """
        super().__init__()
        self["@type"] = "uco-observable:PhoneCallFacet"
        self._set_properties_str(**{"uco-observable:callType": call_type,
                          "uco-observable:allocationStatus": allocation_status})
        self._set_properties_int(**{"uco-observable:duration": call_duration})
        self._set_properties_date_time(**{"uco-observable:startTime": start_time})
        self._set_properties_id_reference(**{"uco-observable:application": application,
                                     "uco-observable:from": call_from,
                                     "uco-observable:to": call_to})

class Call(ObjectFacet):

    def __init__(self, call_type=None, start_time=None, application=None, call_from=None,
                 call_to=None, call_duration=None, allocation_status=None):
        """
        :param call_type: incoming outgoing etc
        :param start_time: the time at which the device registered the call as starting
        :param application: ObjectObservable with call-application (e.g. WhatsApp) facet-info
        :param call_from: ObjectObservable with person/caller facet-info
        :param call_to: ObjectObservable with person/caller facet-info
        :param call_duration: how long the call was registedred on the device as lasting in minutes (E.G. 60)
        :param allocation_status: The allocation status of the record of the call i.e intact for records that are
        present on the device
        """
        super().__init__()
        self["@type"] = "uco-observable:CallFacet"
        self._set_properties_str(**{"uco-observable:callType": call_type,
                          "uco-observable:allocationStatus": allocation_status})
        self._set_properties_int(**{"uco-observable:duration": call_duration})
        self._set_properties_date_time(**{"uco-observable:startTime": start_time})
        self._set_properties_id_reference(**{"uco-observable:application": application,
                                     "uco-observable:from": call_from,
                                     "uco-observable:to": call_to})        


class PhoneAccount(ObjectFacet):

    def __init__(self, phone_number=None, account_name=None):
        """

        :param phone_number: The number for this account (e.g., "+16503889249")
        :param account_name: The name of this account/user (e.g., "Bill Bryson")
        """
        super().__init__()
        self["@type"] = "uco-observable:PhoneAccountFacet"
        self._set_properties_str(**{"uco-observable:phoneNumber": phone_number,
                          "uco-observable:displayName": account_name})


class EmailAccount(ObjectFacet):

    def __init__(self, email_address):
        """
        :param email_address: An ObjectObservable (with EmailAdressFacet)
        """
        super().__init__()
        self["@type"] = "uco-observable:EmailAccountFacet"
        self._set_properties_id_reference(**{"uco-observable:emailAddress": email_address})


class EmailAddress(ObjectFacet):

    def __init__(self, email_address_value=None, display_name=None):
        """
        Used to represent the value of an email address.
        :param email_address_value: a single email address (e.g., "bob@example.com")
        """
        super().__init__()
        self["@type"] = "uco-observable:EmailAddressFacet"
        self._set_properties_str(**{"uco-observable:addressValue": email_address_value,
                          "uco-core:displayName": display_name})


class EmailMessage(ObjectFacet):

    def __init__(self, msg_to=None, msg_from=None, cc=None, bcc=None, subject=None, body=None, received_time=None,
                 sent_time=None, modified_time=None, other_headers=None, application=None, body_raw=None,
                 header_raw=None, in_reply_to=None, sender=None, x_originating_ip=None, is_read=None,
                 content_disposition=None, content_type=None, message_id=None, priority=None, x_mailer=None,
                 is_mime_encoded=None, allocation_status=None, is_multipart=None):
        """
        An instance of an email message, corresponding to the internet message format described in RFC 5322 and related.
        :param msg_to: A list of ObjectObservables (with EmailAccountFacet)
        :param msg_from: An ObjectObservable (with EmailAccountFacet)
        :param cc: A list of ObjectObservables (with EmailAccountFacet) in carbon copy
        :param bcc: A list of ObjectObservables (with EmailAccountFacet) in blind carbon copy
        :param subject: The subject of the email.
        :param body: The content of the email.
        :param received_time: The time received, in ISO8601 time format (e.g., "2020-09-29T12:13:01Z")
        :param sent_time: The time sent, in ISO8601 time format (e.g., "2020-09-29T12:13:01Z")
        :param modified_time: The time modified, in ISO8601 time format (e.g., "2020-09-29T12:13:01Z")
        :param other_headers: A dictionary of other headers
        :param application: The application associated with this object.
        :param body_raw:
        :param header_raw:
        :param in_reply_to: One of more unique identifiers for identifying the email(s) this email is a reply to.
        :param sender: ???
        :param x_originating_ip:
        :param is_read: A boolean True/False
        :param content_disposition:
        :param content_type:
        :param message_id: A unique identifier for the message.
        :param priority: The priority of the email.
        :param x_mailer:
        :param is_mime_encoded: A boolean True/False
        :param is_multipart: A boolean True/False
        :param allocation_status:
        """
        super().__init__()
        self["@type"] = "uco-observable:EmailMessageFacet"
        self._set_properties_str(**{"uco-observable:subject": subject,
			"uco-observable:body": body,
			"uco-observable:otherHeaders": other_headers,
			"uco-observable:bodyRaw": body_raw,
            "uco-observable:headerRaw": header_raw,
			"uco-observable:contentDisposition": content_disposition,
            "uco-observable:contentType": content_type,
            "uco-observable:messageID": message_id,
            "uco-observable:priority": priority,
            "uco-observable:xMailer": x_mailer,
            "uco-observable:allocationStatus": allocation_status,
            "uco-observable:receivedTime": received_time,            
            "uco-observable:modifiedTime": modified_time,
            "uco-observable:isRead": is_read,
			"uco-observable:isMimeEncoded": is_mime_encoded,
			"uco-observable:isMultipart": is_multipart})
        self._set_properties_date_time(**{"uco-observable:sentTime": sent_time})
        self._set_properties_list_id_reference(**{"uco-observable:to": msg_to,
                                    "uco-observable:cc": cc,
                                    "uco-observable:bcc": bcc,                                    
                                    "uco-observable:inReplyTo": in_reply_to,
                                    "uco-observable:sender": sender,
                                    "uco-observable:xOriginatingIP": x_originating_ip,
                                    "uco-observable:application": application})
        self._set_properties_id_reference(**{"uco-observable:from": msg_from})


class EXIF(ObjectFacet):

    def __init__(self, **kwargs):
        """
        Specifies exchangeable image file format (Exif) metadata tags for image and sound files recorded by digital cameras.
        :param kwargs: The user provided key/value pairs of exif items (e.g., Make="Canon", etc.).
        """
        super().__init__()
        self["@type"] = "uco-observable:EXIFFacet"

        self["uco-observable:exifData"] = {"@type": "uco-types:ControlledDictionary", "uco-types:entry": []}
        for k, v in kwargs.items():
            if v not in ["", " "]:
                item = {"@type": "uco-types:ControlledDictionaryEntry", "uco-types:key": k, "uco-types:value": v}
                self["uco-observable:exifData"]["uco-types:entry"].append(item)


class ExtInode(ObjectFacet):

    def __init__(self, deletion_time=None, inode_change_time=None, file_type=None, flags=None, hard_link_count=None,
                 inode_id=None, permissions=None, sgid=None, suid=None):
        """
        An instance of an email message, corresponding to the internet message format described in RFC 5322 and related.
        :param deletion_time: Specifies the time at which the file represented by an Inode was 'deleted'.
        :param inode_change_time: The date and time at which the file Inode metadata was last modified.
        :param file_type: Specifies the EXT file type (FIFO, Directory, Regular file, Symbolic link, etc) for the Inode.
        :param flags: Specifies user flags to further protect (limit its use and modification) the file represented by an Inode.
        :param hard_link_count: Specifies a count of how many hard links point to an Inode.
        :param inode_id: Specifies a single Inode identifier.
        :param permissions: Specifies the read/write/execute permissions for the file represented by an EXT Inode.
        :param sgid: Specifies the group ID for the file represented by an Inode.
        :param suid: Specifies the user ID that 'owns' the file represented by an Inode.
        """
        super().__init__()
        self["@type"] = "uco-observable:ExtInodeFacet"
        self._set_properties_str(**{"uco-observable:extFileType": file_type,
            "uco-observable:extFlags": flags,
            "uco-observable:extHardLinkCount": hard_link_count,
            "uco-observable:extPermissions": permissions,            
            })
        self._set_properties_int(**{"uco-observable:extSGID": sgid,
            "uco-observable:extSUID": suid,
            "uco-observable:extInodeID": inode_id})
        self._set_properties_date_time(**{"uco-observable:extDeletionTime": deletion_time,
            "uco-observable:extInodeChangeTime": inode_change_time})


class CalendarEntry(ObjectFacet):

    def __init__(self, group=None, subject=None, details=None, start_time=None, end_time=None, repeat_until=None,
                 repeat_interval=None, status=None, private=None, recurrence=None, remind_time=None,
                 attendants=None):
        super().__init__()
        self["@type"] = "uco-observable:CalendarEntryFacet"
        self._set_properties_str(**{"drafting:group": group,
            "uco:observable:subject": subject,
            "drafting:details": details,
            "drafting:repeatInterval": repeat_interval,  # todo: type?
            'uco-observable:eventStatus': status,
            'uco-observable:recurrence': recurrence,            
            'uco-observable:remindTime': remind_time,
            "drafting:repeatUntil": repeat_until,
            'uco:observable:isPrivate': private})
        self._set_properties_date_time(**{"uco-observable:startTime": start_time,
            "uco-observable:endTime": end_time})
        #self.append_attendants(attendants)

    
    # def append_attendants(self, *args):
    #     self._append_observable_objects("uco-observable:attendant", *args)


class BrowserCookie(ObjectFacet):

    def __init__(self, source=None, name=None, path=None, domain=None, created_time=None,
                 last_access_time=None, expiration_time=None, secure=None):
        super().__init__()
        self["@type"] = "uco-observable:BrowserCookieFacet"
        self._set_properties_str(**{'uco-observable:cookieName': name,
            "uco-observable:cookiePath": path,            
            'uco-observable:isSecure': secure})
        self._set_properties_date_time(**{'uco-observable:observableCreatedTime': created_time,
            "uco-observable:accessedTime": last_access_time,
            'uco-observable:expirationTime': expiration_time})
        self._set_properties_id_reference(**{"drafting:source": source,
                                     'uco-observable:cookieDomain': domain})


class File(ObjectFacet):

    def __init__(self, file_system_type=None, file_name=None, file_path=None, file_local_path=None,
                 file_extension=None,
                 size_bytes=None, accessed_time=None, created_time=None, modified_time=None,
                 metadata_changed_time=None,
                 tag=None):
        """
        The basic properties associated with the storage of a file on a file system.
        :param file_system_type: The specific type of a file system (e.g., "EXT4")
        :param file_name: Specifies the account_name associated with a file in a file system (e.g., "IMG_0123.jpg").
        :param file_path: Specifies the file path for the location of a file within a filesystem. (e.g., "/sdcard/IMG_0123.jpg")
        :param file_extension: The file account_name extension. Not present if the file has no dot in its account_name. (e.g., "jpg").
        :param size_bytes: The size of the data in bytes (e.g., integer like 35125)
        :param accessed_time: The datetime the file was last accessed
        :param created_time: The datetime the file was created
        :param modified_time: The datetime the file was last modified
        :param metadata_changed_time: The last change to metadata of a file but not necessarily the file contents
        :param tag: A generic (string) tag/label, or a list/tuple of (strings) tags/labels.
        """
        super().__init__()
        self["@type"] = "uco-observable:FileFacet"
        self._set_properties_str(**{"uco-observable:fileSystemType": file_system_type,
            "uco-observable:fileName": file_name,
            "uco-observable:filePath": file_path,
            "drafting:fileLocalPath": file_local_path,
            "uco-observable:extension": file_extension, 
            "uco-observable:mimeType": tag,
            "uco-observable:metadataChangeTime": metadata_changed_time})
        #self._set_properties_str(**{'uco-core:tag': tag})
        #self['uco-core:tag'] = tag
        self._set_properties_date_time(**{"uco-observable:accessedTime": accessed_time,
            "uco-observable:observableCreatedTime": created_time,
            "uco-observable:modifiedTime": modified_time})
        self._set_properties_int(**{"uco-observable:sizeInBytes": size_bytes})


class Message(ObjectFacet):

    def __init__(self, msg_to=None, msg_from=None, message_text=None, sent_time=None,
                 application=None, message_type=None, message_id=None, session_id=None):
        """
        Characteristics of an electronic message.
        :param msg_to: A list of ObjectObservables
        :param msg_from: An ObjectObservable
        :param message_text: The content of the email.
        :param sent_time: The time sent, in ISO8601 time format (e.g., "2020-09-29T12:13:01Z")
        :param application: The application associated with this object.
        :param message_type:
        :param message_id: A unique identifier for the message.
        :param session_id: The priority of the email.
        """
        super().__init__()
        self["@type"] = "uco-observable:MessageFacet"
        self._set_properties_str(**{"uco-observable:messageText": message_text,
                          "uco-observable:messageType": message_type,
                          "uco-observable:messageID": message_id,
                          "uco-observable:sessionID": session_id})
        self._set_properties_date_time(**{"uco-observable:sentTime": sent_time})
        self._set_properties_id_reference(**{"uco-observable:from": msg_from,                                     
                                     "uco-observable:application": application})
        self._set_properties_list_id_reference(**{"uco-observable:to": msg_to})        

class SmsMessage(ObjectFacet):

    def __init__(self, msg_to=None, msg_from=None, message_text=None, sent_time=None,
                 application=None, message_id=None, session_id=None):
        """
        Characteristics of an electronic message.
        :param msg_to: A list of ObjectObservables
        :param msg_from: An ObjectObservable
        :param message_text: The content of the email.
        :param sent_time: The time sent, in ISO8601 time format (e.g., "2020-09-29T12:13:01Z")
        :param application: The application associated with this object.
        :param message_type:
        :param message_id: A unique identifier for the message.
        :param session_id: The priority of the email.
        """
        super().__init__()
        self["@type"] = "uco-observable:SMSMessageFacet"
        self._set_properties_str(**{"uco-observable:messageText": message_text,
                          "uco-observable:messageID": message_id,
                          "uco-observable:sessionID": session_id})
        self._set_properties_date_time(**{"uco-observable:sentTime": sent_time})
        self._set_properties_id_reference(**{"uco-observable:from": msg_from,                                     
                                     "uco-observable:application": application})
        self._set_properties_list_id_reference(**{"uco-observable:to": msg_to}) 

class MobileDevice(ObjectFacet):

    def __init__(self, IMSI=None, ICCID=None, IMEI=None, storage_capacity=None, keypad_pin=None):
        """
        The basic properties associated with a phone and phone account of a device or user.
        :param IMSI International mobile subscriber identity
        :param ICCID Integrated Circuit Card Identification Number
        :param IMEI international mobile equipment identity
        :param storage_capacity storage capacity of device in bytes
        """
        super().__init__()
        self["@type"] = "uco-observable:MobileDeviceFacet"
        self._set_properties_str(**{"uco-observable:IMSI": IMSI,
                          "uco-observable:ICCID": ICCID,
                          "uco-observable:IMEI": IMEI})
        self._set_properties_int(**{"uco-observable:storageCapacityInBytes": storage_capacity,
                          "uco-observable:keypadUnlockCode": keypad_pin})


class OperatingSystem(ObjectFacet):

    def __init__(self, os_name=None, os_manufacturer=None, os_version=None, os_install_date=None):
        super().__init__()
        self["@type"] = "uco-observable:OperatingSystemFacet"
        self._set_properties_str(**{"uco-observable:displayName": os_name,        
                          "uco-observable:version": os_version})
        self._set_properties_id_reference(**{"uco-observable:manufacturer": os_manufacturer})
        self._set_properties_date_time(**{"uco-observable:installDate": os_install_date})


class PathRelation(ObjectFacet):

    def __init__(self, path):
        """
        This CASE object specifies the location of one object within another containing object.
        :param path: The full path to the object (e.g, "/sdcard/IMG_0123.jpg")
        """
        super().__init__()
        self["@type"] = "uco-observable:PathRelationFacet"
        self._set_properties_str(**{"uco-observable:path": path})


class Event(ObjectFacet):

    def __init__(self, event_type=None, event_text=None, event_id=None, cyber_action=None, computer_name=None,
                 created_time=None, start_time=None, end_time=None):
        """
         An event facet is a grouping of characteristics unique to something that happens in a digital context
         (e.g., operating system events).
        :param event_type: The type of the event, for example 'information', 'warning' or 'error'.
        :param event_text: The textual representation of the event.
        :param event_id: The identifier of the event.
        :param cyber_action: The action taken in response to the event.
        :param computer_name: A name of the computer on which the log entry was created.
        """
        super().__init__()
        self["@type"] = "uco-observable:EventRecordFacet"
        self._set_properties_str(**{"uco-observable:eventType": event_type,
                          "uco-observable:eventRecordText": event_text,
                          "uco-observable:eventID": event_id,
                          "uco-observable:computerName": computer_name})
        self._set_properties_id_reference(**{'uco-observable:cyberAction': cyber_action})
        self._set_properties_date_time(**{'uco-observable:observableCreatedTime': created_time,
                               'drafting:observableStartTime': start_time,
                               'drafting:observableEndTime': end_time})


# class ObservableRelationship(ObjectSpecial):

#     def __init__(self, source, target, start_time=None, end_time=None, kind_of_relationship=None, directional=None):
#         """
#         This object represents an assertion that one or more objects are related to another object in some way
#         :param source: An observable object
#         :param target: An observable object
#         :param start_time: The time, in ISO8601 time format, the action was started (e.g., "2020-09-29T12:13:01Z")
#         :param end_time: The time, in ISO8601 time format, the action completed (e.g., "2020-09-29T12:13:43Z")
#         :param kind_of_relationship: How these items relate from source to target (e.g., "Contained_Within")
#         :param directional: A boolean representing ???? Usually set to True
#         """
#         super().__init__()
#         self["@type"] = "uco-observable:ObservableRelationship"
#         self._bool_vars(**{"uco-core:isDirectional": directional})
#         self._str_vars(**{"uco-core:kindOfRelationship": kind_of_relationship})
#         self._datetime_vars(**{"uco-observable:startTime": start_time,
#                                "uco-observable:endTime": end_time})
#         self._node_reference_vars(**{"uco-core:source": source,
#                                      "uco-core:target": target})

#     def set_start_accessed_time(self):
#         """Set the time when this action initiated."""
#         self._addtime(_type='start')

#     def set_end_accessed_time(self):
#         """Set the time when this action completed."""
#         self._addtime(_type='end')

#     def _addtime(self, _type):
#         time = datetime.now(timezone('UTC'))
#         self[f"uco-observable:{_type}Time"] = {"@type": "xsd:dateTime", "@value": time.isoformat()}


class ApplicationAccount(ObjectFacet):

    def __init__(self, application=None):
        """
        An application account facet is a grouping of characteristics unique to an account within a particular software
        program designed for end users.
        :param application: An Observable Object (containing an Application Facet)
        """
        super().__init__()
        self["@type"] = "uco-observable:ApplicationAccountFacet"
        self._set_properties_id_reference(**{"uco-observable:application": application})


class DigitalAccount(ObjectFacet):

    def __init__(self, display_name=None, login=None, first_login_time=None, disabled=None, last_login_time=None):
        """
        A digital account facet is a grouping of characteristics unique to an arrangement with an entity to enable and
        control the provision of some capability or service within the digital domain.
        """
        super().__init__()
        self["@type"] = "uco-observable:DigitalAccountFacet"
        self._set_properties_str(**{"uco-observable:displayName": display_name,
                          'uco-observable:accountLogin': login})
        self._set_properties_date_time(**{'uco-observable:firstLoginTime': first_login_time,
                               'uco-observable:lastLoginTime': last_login_time})
        self._set_properties_bool(**{'uco-observable:isDisabled': disabled})


class WirelessNetworkConnection(ObjectFacet):

    def __init__(self, ssid=None, base_station=None):
        """
        A wireless network connection facet is a grouping of characteristics unique to a connection (completed or
        attempted) across an IEEE 802.11 standards-conformant digital network (a group of two or more computer systems
        linked together).
        """
        super().__init__()
        self["@type"] = "uco-observable:WirelessNetworkConnectionFacet"
        self._set_properties_str(**{"uco-observable:ssid": ssid,
                          'uco-observable:baseStation': base_station})

class Messagethread(ObjectFacet):

    def __init__(self, visibility=None, participants=None, display_name=None,
                 messages=None, message_state=None, message_has_changed=None):
        """
        A message thread facet is a grouping of characteristics unique to a running commentary of electronic messages
        pertaining to one topic or question.
        """
        super().__init__()
        self["@type"] = "uco-observable:MessageThreadFacet"
        self._set_properties_str(**{"uco-observable:displayName": display_name})
        self._set_properties_bool(**{'uco-observable:visibility': visibility})
        self._set_properties_list_id_reference(**{'uco-observable:participant': participants})

        self["uco-observable:messageThread"]=dict()
        self["uco-observable:messageThread"]["@id"]= "kb:" + str(uuid4())
        self["uco-observable:messageThread"]["@type"] = "uco-types:Thread"
        self["uco-observable:messageThread"]["co:size"]= dict()
        self["uco-observable:messageThread"]["co:size"]["@type"] = "xsd:nonNegativeInteger"
        self["uco-observable:messageThread"]["co:size"]["@value"] = str(len(messages))
        self["uco-observable:messageThread"]["co:element"]= list()
        for i, m in enumerate(messages):
            self["uco-observable:messageThread"]["co:element"].append({"@id":m.get_id()})

    # def append_messages(self, messages):
    #     self['uco-observable:message'].append_indexed_items(messages)

    # def append_participants(self, participants):
    #     self._append_refs('uco-observable:participant', *participants)


class MessageSMS(ObjectFacet):

    def __init__(self, has_changed=None, state=None, indexed_items=None):
        """
        A message is a discrete unit of electronic communication intended by the source for consumption by some
        recipient or group of recipients. [based on https://en.wikipedia.org/wiki/Message]
        """
        super().__init__()
        self["@type"] = "uco-observable:Message"
        self._set_properties_str(**{'uco-observable:state': state})
        self._set_properties_bool(**{'uco-observable:hasChanged': has_changed})
        #self.append_indexed_items(indexed_items)


class DiskPartition(ObjectFacet):

    def __init__(self, serial_number=None, partition_type=None, total_space=None, space_left=None,
                 space_used=None, offset=None):
        """
        Used to represent Disk Partition
        :param serial_number: disk partition identifier
        :param partition_type: FAT32, NTFS etc.
        :param total_space: free space
        :param space_left: total - used space
        :param space_used: used space
        :param space_used: the offset to the beginning of the disk
        """
        super().__init__()
        self["@type"] = "uco-observable:DiskPartitionFacet"
        self._set_properties_str(**{"uco-observable:serialNumber": serial_number,
                          "uco-observable:diskPartitionType": partition_type})
        self._set_properties_int(**{"uco-observable:totalSpace": total_space,
                          "uco-observable:spaceLeft": space_left,
                          "uco-observable:spaceUsed": space_used,
                          "uco-observable:partitionOffset": offset})


class Disk(ObjectFacet):

    def __init__(self, disk_type=None, size=None, partition=None):
        """
        Used to represent Fixed Disk 
        :param disk_type: Fixed default value
        :param size: disk size
        :param partition: array of @id references to the partitions contained
        """
        super().__init__()
        self["@type"] = "uco-observable:DiskFacet"
        self._set_properties_str(**{"uco-observable:diskType": disk_type})
        self._set_properties_int(**{"uco-observable:diskSize": size})
        self._set_properties_list_id_reference_array(**{"uco-observable:partition": partition})

class CellSite(ObjectFacet):

    def __init__(self, country_code=None, network_code=None, area_code=None, site_id=None):
        super().__init__()
        self['@type'] = "uco-observable:CellSiteFacet"
        self._set_properties_str(**{"uco-observable:cellSiteType": "GSM",
                "uco-observable:cellSiteCountryCode": country_code,
                "uco-observable:cellSiteNetworkCode": network_code,
                "uco-observable:cellSiteLocationAreaCode": area_code,
                "uco-observable:cellSiteIdentifier": site_id})

class SocialMediaActivity(ObjectFacet):

    def __init__(self, application=None, created_time=None, body=None, page_title=None, url=None, author_id=None,
                 author_name=None, reactions_count=None, shares_count=None, activity_type=None, comment_count=None,
                 account_id=None):
        """
        :param application: An observable object
        :param created_time:
        :param body:
        :param page_title:
        :param url: An observable object
        :param author_id:
        :param author_name:
        :param reactions_count:
        :param shares_count:
        :param activity_type:
        :param comment_count:
        :param account_id:
        """
        super().__init__()
        self['@type'] = "drafting:SocialMediaActivityFacet"
        self._set_properties_str(**{"uco-observable:body": body,
                          "uco-observable:pageTitle": page_title,
                          "drafting:authorIdentifier": author_id,
                          "drafting:authorName": author_name,
                          "drafting:reactionsCount": reactions_count,
                          "drafting:sharesCount": shares_count,
                          "drafting:activityType": activity_type,
                          "drafting:commentCount": comment_count,
                          "uco-observable:accountIdentifier": account_id})
        self._set_properties_date_time(
            **{'uco-observable:observableCreatedTime': created_time})
        self._set_properties_id_reference(**{"uco-observable:application": application,
                                     "uco-observable:url": url})

class SearchedItem(ObjectFacet):

    def __init__(self, search_value=None, search_result=None, application=None, search_launch_time=None):
        super().__init__()
        self["@type"] = "drafting:SearchedItemFacet"
        self._set_properties_str(**{"drafting:searchValue": search_value,
                          "drafting:searchResult": search_result})
        self._set_properties_date_time(
            **{'drafting:searchLaunchedTime': search_launch_time})
        self._set_properties_id_reference(
            **{'uco-observable:application': application})

class Location(ObjectFacet):

    def __init__(self, latitude=None, longitude=None, altitude=None):
        super().__init__()
        self["@type"] = "uco-location:LatLongCoordinatesFacet"
        self._set_properties_float(**{"uco-location:latitude": latitude,
                            "uco-location:longitude": longitude,
                            'uco-location:altitude': altitude})
        #self._set_properties_str(**{'drafting:locationType': location_type})

class SimpleName(ObjectFacet):

    def __init__(self, given_name=None, family_name=None):
        """
        :param given_name: Full name of the identity of person
        :param family_name: Family name of identity of person
        """
        super().__init__()
        self["@type"] = "uco-identity:SimpleNameFacet"
        self._set_properties_str(**{"uco-identity:givenName": given_name,
                          "uco-identity:familyName": family_name})

class Role(ObjectSpecial):

    def __init__(self, description=None, _id=None, modified_time=None, name=None, created_time=None, spec_version=None,
                 tag=None, _type=None, created_by=None, objet_marking=None):
        """
        A role is a usual or customary function based on contextual perspective.
        :param description: A description of a particular concept characterization.
        :param _id: A globally unique identifier for a characterization of a concept.
        :param modified_time: Specifies the time that this particular version of the object was modified.
        :param name: The name of a particular concept characterization.
        :param created_time: The time at which a characterization of a concept is created.
        :param spec_version: The version of UCO used to characterize a concept.
        :param tag: A generic tag/label.
        :param _type: The explicitly-defined type of characterization of a concept.
        :param created_by: The identity that created a characterization of a concept.
        :param objet_marking: Marking definitions to be applied to a particular concept characterization in its entirety
        """

        super().__init__()
        self["@type"] = "uco-role:Role"
        self._set_properties_str(**{"uco-core:description": description,
                          "uco-core:name": name,
                          "uco-core:specVersion": spec_version,
                          "uco-core:tag": tag,
                          "uco-core:type": _type})
        self._set_properties_date_time(**{"uco-core:modifiedTime": modified_time,
                               "uco-core:objectCreatedTime": created_time})
        self._set_properties_id_reference(**{"uco-core:id": _id,
                                     "uco-core:createdBy": created_by,
                                     "uco-core:objectMarking": objet_marking})

class SimpleAdress(ObjectFacet):

    def __init__(self, country=None, locality=None, street=None, postal_code=None, region=None, address_type=None):
        super().__init__()
        self["@type"] = "uco-location:SimpleAddressFacet"
        self._set_properties_str(**{"uco-location:adressType": address_type,
                          "uco-location:country": country,
                          'uco-location:locality': locality,
                          'uco-location:postalCode': postal_code,
                          'uco-location:region': region,
                          'uco-location:street': street})

class Tool(ObjectSpecial):

    def __init__(self, tool_name=None, tool_version=None, tool_type=None, tool_creator=None):
        """
        The Uco tool is a way to define the specfifics of a tool used in an investigation
        :param tool_name: The account_name of the tool (e.g., "exiftool")
        :param tool_creator: The developer and or organisation that produces this tool {might need to add a dict here}
        :param tool_type: The type of tool
        :param tool_version: The version of the tool
        """
        super().__init__()
        self["@type"] = "uco-tool:Tool"
        self._set_properties_str(**{"uco-core:name": tool_name,
                          "uco-tool:version": tool_version,
                          "uco-tool:toolType": tool_type})                                
        self._set_properties_id_reference(**{"uco-tool:creator": tool_creator})

class InvestigativeAction(ObjectSpecial):

    def __init__(self, name=None, description=None, start_time=None, end_time=None,
        performer=None, instrument=None, location=None, environment=None, results=None, objects=None):
        """
        An investigative action is a CASE object that represents the who, when, what outcome of an action
        :param name: The account_name of the action (e.g., "annotated")
        :param start_time: The time, in ISO8601 time format, the action was started (e.g., "2020-09-29T12:13:01Z")
        :param end_time: The time, in ISO8601 time format, the action completed (e.g., "2020-09-29T12:13:43Z")
        """
        super().__init__()
        self["@type"] = "case-investigation:InvestigativeAction"
        self._set_properties_str(**{"uco-core:name": name,
                          'uco-core:description': description,
                          "uco-action:environment": environment})
        self._set_properties_date_time(**{"uco-action:startTime": start_time,
                               "uco-action:endTime": end_time})
        self._set_properties_id_reference(**{"uco-action:performer": performer,
                                    "uco-action:instrument": instrument,
                                    "uco-action:location": location})
        self._set_properties_list_id_reference(**{"uco-action:result": results})
        self._set_properties_list_id_reference_array(**{"uco-action:object": objects})


class ActionReferences(ObjectFacet):

    def __init__(self, performer=None, instrument=None, location=None, environment=None, results=None, objects=None):
        """
        An action reference contains the details of an InvestigativeAction.
        It groups the properties characterizing the core elements (who, how, with what, where, etc.) for actions.
        The properties consist of identifier references to separate UCO objects detailing the particular property.
        :param performer: The account_name or id of the person conducting the action
        :param instrument: The tool used to conduct the action
        :param location: The general location where the action took place (Room, Building or Town)
        :param environment: The type of environment (lab, office)
        :param results: A list of resulting output identifiers
        """
        super().__init__()
        self["@type"] = "uco-action:ActionReferencesFacet"
        self._set_properties_str(**{"uco-action:environment": environment})
        self._set_properties_id_reference(**{"uco-action:performer": performer,
                                     "uco-action:instrument": instrument,
                                     "uco-action:location": location})
        self._set_properties_list_id_reference(**{"uco-action:result": results})
        self._set_properties_list_id_reference_array(**{"uco-action:object": objects})

    def append_results(self, *args):
        """
        Add result(s) to the list of outputs from an action
        :param args: A CASE object, or objects, often an observable. (e.g., one or many devices from a search operation)
        """
        self._set_properties_list_id_reference("uco-action:result", *args)

    def append_objects(self, *args):
        """
        Add object(s) to the list of outputs from an action
        :param args: A CASE object, or objects, often an observable. (e.g., one or many devices from a search operation)
        """
        self._set_properties_list_id_reference("uco-action:object", *args)

