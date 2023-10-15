#!/usr/bin/python3
#
#--------------------------------------
#
# RaspController notifications
# v.2
#
# Author   : Ettore Gallina
# Date     : 06/10/2023
# Copyright: Egal Net di Ettore Gallina
#
# https://www.egalnetsoftwares.com/
#
#--------------------------------------


import ctypes
import subprocess
import os


architecture = subprocess.check_output(["uname", "-m"]).decode("utf-8").strip()
openssl_version = subprocess.check_output(["openssl", "version"]).decode("utf-8").strip()
if architecture == "aarch64" or architecture == "armv8":
	if openssl_version.startswith("OpenSSL 1.1.1"):
		lib_so = "raspc_notif_lib2_arm64_ssl1.1.1.so"
	elif openssl_version.startswith("OpenSSL 3.0."):
		lib_so = "raspc_notif_lib2_arm64_ssl3.0.2.so"
	else:
		raise Exception("OpenSSL not found. Please install it!")
else:
	if openssl_version.startswith("OpenSSL 1.1.1"):
		lib_so = "raspc_notif_lib2_armhf_ssl1.1.1.so"
	elif openssl_version.startswith("OpenSSL 3.0."):
		lib_so = "raspc_notif_lib2_armhf_ssl3.0.2.so"
	else:
		raise Exception("OpenSSL not found. Please install it!")
_notif_lib = ctypes.cdll.LoadLibrary(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + lib_so)	

		
     
class _CResult(ctypes.Structure):
	_fields_ = [("status", ctypes.c_int),
                ("message", ctypes.c_char_p)] 
		

class Result:
	
	SUCCESS = ctypes.c_int.in_dll(_notif_lib, "SUCCESS").value
	SOCKET_ERROR = ctypes.c_int.in_dll(_notif_lib, "SOCKET_ERROR").value
	TOO_MANY_REQUESTS = ctypes.c_int.in_dll(_notif_lib, "TOO_MANY_REQUESTS").value
	SERVER_ERROR = ctypes.c_int.in_dll(_notif_lib, "SERVER_ERROR").value
	INVALID_APIKEY = ctypes.c_int.in_dll(_notif_lib, "INVALID_APIKEY").value
	INVALID_PARAMETER = ctypes.c_int.in_dll(_notif_lib, "INVALID_PARAMETER").value
	NO_TOKEN_FOUND = ctypes.c_int.in_dll(_notif_lib, "NO_TOKEN_FOUND").value
		
		
	def __init__(self, status, message):
		self.status = status
		self.message = message
		
		
		
class Notification:
	def __init__(self, title, message, high_priority = False):
		self.title = title
		self.message = message
		self.high_priority = high_priority
		
	def has_valid_title(self):
		return self.title == None or isinstance(self.title, str)


	def has_valid_message(self):
		return isinstance(self.message, str) and self.message.strip()
		
		

class Sender:
	
	def __init__(self, apikey):
		self.apikey = apikey


	def send_notification(self, notification):
		if not isinstance(notification, Notification):
			return Result(Result.INVALID_PARAMETER, "Invalid notification")
		
		if not notification.has_valid_title():
			return Result(Result.INVALID_PARAMETER, "Invalid title")

		if not notification.has_valid_message():
			return Result(Result.INVALID_PARAMETER, "Invalid message")
		
		title_to_send = notification.title[0:200].encode()
		message_to_send = notification.message[0:1000].encode()
		cresult = ctypes.POINTER(_CResult)
		_notif_lib.send_notifications.restype = ctypes.POINTER(_CResult)
		cresult = _notif_lib.send_notifications(self.apikey.encode(), title_to_send, message_to_send, notification.high_priority)
		result = Result(cresult.contents.status, cresult.contents.message.decode("utf-8"))
		_notif_lib.free_result(cresult)
		return result


	

		
		
		

  
