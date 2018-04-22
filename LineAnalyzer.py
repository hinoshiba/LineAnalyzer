#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, codecs
import sqlite3
import json
import datetime
import os.path

DEBUG = True
DEFAULT_BACKUP = "~/Library/Application Support/MobileSync/Backup/"
FILE_MANIFEST = "/Manifest.db"
def echoLog(_logtext,_default_echo=True):
    if _default_echo:
        print("[MSG]"+str(_logtext))
    else :
        if DEBUG : print("[DEBUG]"+str(_logtext))


def getSqlfileName(_manifestpath):
    _filename = None
    _conn = sqlite3.connect(_manifestpath)
    _c = _conn.cursor()
    for _row in _c.execute("SELECT fileID FROM Files WHERE relativePath like '%Line.sqlite%'"):
        _filename = _row
    if _filename is None :
        echoLog("filename not found",False)
        return None
    return "/" + (_filename[0])[0:2] + "/" + _filename[0]
def testExit():
    echoLog("testExit",False)
    exit()
#### format
_file_linedb = None
_username = {}
_talk = {}
_filename_map = {}

#### main
echoLog("StartScript")
path = os.path.expanduser(DEFAULT_BACKUP)
echoLog(os.listdir(path))


while True :
    echoLog("into while",False)
    echoLog("======= Choose Backup file =======")
    for row in os.listdir(path):
        echoLog("filename:"+row)
    _target_file = raw_input('which do you want >> ')
    if _target_file in os.listdir(path) :
        echoLog("Find Input File",False)
        _file_linedb =  path + _target_file + "/" + getSqlfileName(path + _target_file + "/" + FILE_MANIFEST)
        if not _file_linedb is None :
            break
        else :
            echoLog("Cant find Line Database File")
    else:
        echoLog("choose failed")
echoLog("Target file is "+  _file_linedb)

echoLog("Check a Dir",False)
if os.path.isdir(str(_target_file)):
    echoLog("Directory already",False)
    echoLog("The directory already exists. Can,t make a new one.")
    echoLog("Please move,delete or give up execution.")
    exit()
echoLog("Make a Dir",False)
os.mkdir(str(_target_file))
echoLog("Make a Dir .... done",False)

echoLog("Will Get Sql_Users")
_conn = sqlite3.connect(_file_linedb)
_c = _conn.cursor()
for _userid,_name,_customname in _c.execute("SELECT Z_PK,ZNAME,ZCUSTOMNAME FROM ZUSER"):
        # ZUSER is tablename
        # Z_PK is autoincrement integer id
        # ZNAME is default username . maybe saved line.corp database
        # ZCUSTOMNAME is customizename
        _username[_userid] = {"name":_name,"custom":_customname}
echoLog("Will Get Sql_Users....Done")

echoLog("Will Get Sql_Messages")
for _zchat,_userid,_message,_timestamp in _c.execute("SELECT ZCHAT,ZSENDER,ZTEXT,ZTIMESTAMP FROM ZMESSAGE ORDER BY Z_PK "):
    # ZMESSAGE is tablesname
    # Z_PK is autoincrement integer id
    # ZCHAT is talk room id
    # ZSENDER is talk send user id. Can find Z_PK in a ZUSER
    # ZTEXT is user sending message
    # ZTIMESTAMP is message sending unixtime
    ## set default strings
    _talkuser = "ME"
    _talkuser_custom = "ME"
    _talkmessage = "stamp or call"
    _talkdate = 00000000000
    ## set strings
    if not _userid is None :
        _talkuser = _username[_userid]["name"]
        _talkuser_custom = _username[_userid]["custom"]
    if not _message is None :
        _talkmessage = _message
    if not _timestamp is None :
        _talkdate = datetime.datetime.fromtimestamp(int(str(_timestamp)[0:10]))
    # export json
    ## _talk[_zchat] = {"user":_talkuser,"customname":_talkuser_custom ,"msg":_talkmessage , "date":_talkdate}
    _f = open(str(_target_file)+"/zchat.csv",'a')
    _f = codecs.lookup('utf_8')[-1](_f)
    _f.write(str(_zchat)+"\n")
    _f.close()
    _f = open(str(_target_file)+"/"+str("{0:05d}".format(_zchat))+".csv",'a')
    _f = codecs.lookup('utf_8')[-1](_f)
    _f.write(((str(_talkdate) + "," +_talkuser + "," + _talkmessage).replace('\n',''))+"\n")
    _f.close()
echoLog("Will Get Sql_Messages....Done")
echoLog("EndScript")
