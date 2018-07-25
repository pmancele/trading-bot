from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import bitfinex.client

# Setup the Gmail API
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

public_client = bitfinex.client.Public()


def CreateMsgLabels():
  """Create object to update labels.

  Returns:
    A label update object.
  """
  return {'removeLabelIds': ['INBOX'], 'addLabelIds': ['Label_3666501887904461799']}

def executeOrder(messageSnippet):
    if 'BUY' in messageSnippet:
        words = messageSnippet.split(" ")
        print("BUYING {}".format(words[6]))
        symbol = words[6] + 'USD'
        print("Current price is {}".format(public_client.ticker(symbol)['last_price']))
        print()

    elif 'SELL' in messageSnippet:
        words = messageSnippet.split(" ")
        print("SELLING {}".format(words[6]))
        symbol = words[6] + 'USD'
        print("Current price is {}".format(public_client.ticker(symbol)['last_price']))
        print()

if __name__ == '__main__':
    # Get last messages (1 day)
    query = service.users().messages().list(userId='me', q='from:noreply@tradingview.com + newer_than:1d').execute()

    # process mails if they are new and not already processed
    messages = query.get('messages')
    for message in messages:
        message = service.users().messages().get(userId='me', id=message['id']).execute()
        if 'INBOX' in message['labelIds']:
            print("Alert found: {}".format(message['snippet']))
            print("Placing order ...")
            executeOrder(message['snippet'])

        if 'Label_3666501887904461799' in message['labelIds']:
            print("Found alert already processed: {}".format(message['snippet']))