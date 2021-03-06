#!/usr/bin/env python3
'''
Factorio Mod Updater, by Toesoe (https://get.rekt.info/blog)

Quick 'n' dirty Python3 script to update mods on (headless) Factorio server
Uses your username and auth token stored in the server-settings.json file in the Data directory
so make sure you filled those out
No exception handling so don't blame me if your system craps out
Please run it as the user that owns the Factorio folder to prevent any rights issues and shit

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

TL DR: IDGAF what you do with this file, it took me only about an hour to write
'''

from __future__ import print_function
import requests, json, sys
from os import listdir, remove
import re, glob

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
        lastentry = len(r.json()['releases'])
        download_url_list[r.json()['releases'][lastentry-1]['file_name']] = r.json()['releases'][lastentry-1]['download_url']

    print(download_url_list)
    return download_url_list


def download_mod(user, token, mod_dlpath, filename):
    mod_out = open(basePath + "/mods/" + filename, "wb")

    r = requests.get("https://mods.factorio.com" + str(mod_dlpath), params={'username': user, 'token': token})

    mod_out.write(bytes(r.content))


def main():
    global basePath

    credentials = get_token()

    download_dict = get_downloadpaths()
    local_files = get_localfiles()

    s = set(local_files)

    diff = [x for x in download_dict if x not in s]  # all files which do not exist on disk yet

    for value in diff:
        print("Removing old version of " + re.sub('_([0-9]).*.zip', '', value))

        oldfiles = glob.glob(basePath + "/mods/" + re.sub('_([0-9]).*.zip', '', value) + "*")

        for file in oldfiles:
            remove(file)  # delete the old file, we don't want collisions

        print("Downloading " + value)
        download_mod(credentials[0], credentials[1], download_dict[value], value)


if __name__ == '__main__':
    sys.exit(main())
