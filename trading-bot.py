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
trading_client = bitfinex.client.Trading(key='xxx', secret='xxx')

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
        ticker = public_client.ticker(symbol)
        print("Current price is {}. Bid is {}".format(ticker['last_price'], ticker['bid']))
        buy_price = float(ticker['bid']) + 0.001*float(ticker['bid'])
        print("Putting BUY order of 50 USD on {} at price {}".format(symbol, buy_price))
        print()
        return 0

    if 'SELL' in messageSnippet:
        words = messageSnippet.split(" ")
        print("SELLING {}".format(words[6]))
        symbol = words[6] + 'USD'
        print("Current price is {}".format(public_client.ticker(symbol)['last_price']))
        print()
        return 0
    else:
        return -1

if __name__ == '__main__':
    # Get last messages (1 day)
    query = service.users().messages().list(userId='me', q='from:noreply@tradingview.com + newer_than:1d').execute()

    # process mails if they are new and not already processed
    messages = query.get('messages')
    for message in messages:
        content = service.users().messages().get(userId='me', id=message['id']).execute()
        if 'INBOX' in content['labelIds']:
            print("Alert found: {}".format(content['snippet']))
            print("Placing order ...")
            if (executeOrder(content['snippet']) == 0):
                service.users().messages().modify(userId='me', id=content['id'], body=CreateMsgLabels()).execute()
                print("Order executed")

        if 'Label_3666501887904461799' in content['labelIds']:
            print("Found alert already processed: {}".format(content['snippet']))