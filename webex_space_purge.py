# webex-space-purge

# Copyright (c) 2022 Cisco and/or its affiliates.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import sqlite3
import import_data
from datetime import datetime
import zoneinfo
from webexteamssdk import WebexTeamsAPI, ApiError

# Edit .env file to specify optional configuration
import os
from dotenv import load_dotenv
load_dotenv(override=True)

database = 'space_purge.db'
conn = sqlite3.connect(database)
conn.row_factory = sqlite3.Row

accessToken = os.getenv('WEBEX_ACCESS_TOKEN')

if accessToken == '':
    print('Invalid configuration in .env: WEBEX_ACCESS_TOKEN missing')
    sys.exit(1)
api = WebexTeamsAPI(access_token=accessToken)

cutOffDate = os.getenv('CUT_OFF_DATE')
try:
    datetime.strptime(cutOffDate, '%Y-%m-%d')
except:
    print('Invalid configuration in .env: CUT_OFF_DATE malformed - format: YYY-MM-DD: ')
    sys.exit(1)

print(f'\nPurge users with no messages since: {cutOffDate}')

roomId=os.getenv('ROOM_ID')
if roomId=='':
    print('Invalid configuration in .env: ROOM_ID missing')
    sys.exit(1)
try:
    roomName=api.rooms.get(roomId).title
except ApiError as e:
    print(f'Error getting space details: {e}')

print(f'Target space: {roomName}')

if not os.getenv('skipDownload') == 'True':
    import_data.importData(api, conn, accessToken, roomId, cutOffDate)

cursor = conn.cursor()

cutOffDate = datetime.strptime( cutOffDate, '%Y-%m-%d' ).astimezone(zoneinfo.ZoneInfo('UTC'))
cutOffDate = cutOffDate.strftime( '%Y-%m-%dT%H:%M:%S.%f%z' )

query = f'''
    SELECT DISTINCT memberships.id, memberships.personEmail
    FROM memberships LEFT JOIN messages
    ON memberships.personId=messages.personId
    WHERE messages.personId is null
    '''

rows = cursor.execute(query).fetchall()

if len(rows) < 1:
    print('\nNo memberships were found to purge!')
    sys.exit(0)

print('\nWriting records to file: ', end = '' )

with open( 'purge_list.csv', 'w', encoding = 'utf-8' ) as outfile:
    count=0
    for row in rows:
        count+=1
        print(f'\rWriting records to file: {count}', end='')
        outfile.write(f'{row["personEmail"]}\n')

print('\n\nComplete\n')

if not input(f'Removing {count} users from space.  Enter "CONFIRM" to proceed: ') == 'CONFIRM':
    sys.exit(0)

count=0

print('\nDeleting memberships: ', end='')

for row in rows:
    count+=1
    print(f'\rDeleting memberships: {count}', end='')
    # api.memberships.delete(row['id']) //enable this line to actually purge users

print('\nDone!')    