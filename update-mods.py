#!/usr/bin/env python3
'''
Quick 'n' dirty Python3 script to update mods on (headless) Factorio server
Uses your username and auth token stored in the server-settings.json file in the Data directory
so make sure you filled those out
No exception handling so don't blame me if your system craps out
Please run it as the user that owns the Factorio folder to prevent any rights issues and shit

Copyright (c) 2018 Toesoe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

TL DR: IDGAF what you do with this file, it took me only 30 minutes to write
'''

from __future__ import print_function
import requests, json, sys
from os import listdir, remove

glob = {'verbose': False}

basePath = "/opt/factorio"  # change this to your Factorio base path, duh


def get_token():
    global basePath

    settings_file = open(basePath + "/data/server-settings.json").read()
    json_settings = json.loads(settings_file)

    user = json_settings['username']
    token = json_settings['token']

    if user == '' or token == '':
        print("mate, did you forget to set your username and token in the server-settings.json file?")
        print("please fill 'em out then run this script again")
        exit(0)

    return user, token


def get_localfiles():
    files = listdir(basePath + "/mods")
    files.remove("mod-list.json")
    print(files)

    return files


def get_downloadpaths():
    global basePath

    name_list = ['']
    download_url_list = {}  # filename:url

    list_file = open(basePath + "/mods/mod-list.json").read()
    json_mods = json.loads(list_file)

    for index, item in enumerate(json_mods['mods']):
        name_list.append(item['name'])

    name_list = name_list[2:]

    for name in name_list:
        r = requests.get('https://mods.factorio.com/api/mods/' + name)
        download_url_list[r.json()['releases'][0]['file_name']] = r.json()['releases'][0]['download_url']

    return download_url_list


def download_mod(user, token, mod_dlPath, filename):
    mod_out = open(basePath + "/mods/" + filename, "wb")

    r = requests.get("https://mods.factorio.com" + str(mod_dlPath), params={'username': user, 'token': token})

    mod_out.write(bytes(r.content))


def main():
    global basePath
    i = 0  # uber ghetto hacks, i cba to do it the right way

    credentials = get_token()

    download_dict = get_downloadpaths()
    local_files = get_localfiles()

    for key, value in download_dict.items():
        if local_files[i] != key:  # let's check if we already have the most recent version, saves some 'net bytes
            print("Downloading " + value)
            download_mod(credentials[0], credentials[1], value, key)
            remove(basePath + "/mods/" + local_files[i])  # delete the old file, we don't want collisions
        else:
            print(key + " is already up to date")
        i += 1


if __name__ == '__main__':
    sys.exit(main())
