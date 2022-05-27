# webex-messaging-activity-report-sample

# Copyright (c) 2019 Cisco and/or its affiliates.
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
from datetime import datetime
from webexteamssdk import ApiError

def importData(api, conn, teamsAccessToken, roomId, cutOffDate):

    cursor = conn.cursor()
    try:
        resp = cursor.execute('DROP TABLE messages')
    except:
        pass
    conn.commit
    resp = cursor.execute(
        '''
        CREATE TABLE messages (
            id text,
            created text, 
            roomId text, 
            text text, 
            personId text, 
            personEmail text
            )
        '''
    )
    conn.commit

    try:
        resp = cursor.execute('DROP TABLE memberships')
    except:
        pass
    conn.commit

    resp = cursor.execute(
        '''
        CREATE TABLE memberships (
            id text,
            personId text, 
            personEmail text
            )
        '''
    )
    conn.commit

    print('\nImporting messages: ', end = '')

    cutOffDate = datetime.strptime(cutOffDate, '%Y-%m-%d').astimezone()

    try:
        messages = api.messages.list(roomId=roomId)
    except ApiError as e:
        print(f'Error listing messages: {e}')
        sys.exit(1)

    count = 0
    data = []

    for message in messages:
        count += 1
        print(f'\rImporting messages: {count}', end='')
        if message.created < cutOffDate:
            break
        messageCreated = message.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

        data.append((
            message.id,
            messageCreated,
            message.roomId,
            message.text,
            message.personId,
            message.personEmail,
        ))

    if count < 1:
        print('\nNo messages found newer than cutoff date')
        return

    cursor.executemany(
        'REPLACE INTO messages VALUES (?,?,?,?,?,?)', data)
    conn.commit()

    print('\nImporting memberships: ', end = '')

    count = 0

    try:
        memberships = api.memberships.list(roomId=roomId)
    except ApiError as e:
        print(f'Error listing memberships: {e}')
        sys.exit(1)

    data = []
    for membership in memberships:
        count += 1
        print(f'\rImporting memberships: {count}', end='')
        
        data.append((
            membership.id,
            membership.personId,
            membership.personEmail,
        ))

    cursor.executemany('INSERT INTO memberships VALUES (?,?,?)', data)
    conn.commit()    
    print()
