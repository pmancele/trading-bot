from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import bitfinex.client
import csv
import time

keys = open('keys.txt', 'r')
mykey = keys.readline().replace('\n', '')
mysecret = keys.readline().replace('\n', '')
public_client = bitfinex.client.Public()
trading_client = bitfinex.client.Trading(key=mykey, secret=mysecret)
balances_dict = {}

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
        symbol = words[1]
        ticker = public_client.ticker(symbol)
        print("Current price is {}. Bid is {}".format(ticker['last_price'], ticker['bid']))
        balance = balances_dict['usd']
        print("Current USD balance is {}".format(balance))
        buy_price = (2*float(ticker['ask']) + float(ticker['bid']))/3
        print("Putting BUY order of {} USD on {} at price {}".format(min(50.0, float(balance)), symbol, buy_price))
        amount = min(50.0, float(balance))/buy_price
        print(trading_client.new_order(amount=amount, price=buy_price, side='buy', symbol=symbol))
        with open("logs.csv", 'a') as csv_output:
            field_names = ['Timestamp', 'symbol', 'side', 'amount', 'price']
            writer = csv.DictWriter(csv_output, fieldnames=field_names, delimiter=',')
            #writer.writeheader()
            writer.writerow({'Timestamp':int(time.time()), 'symbol':symbol, 'side':'buy', 'amount':amount, 'price':buy_price})
        print()
        return 0

    if 'SELL' in messageSnippet:
        words = messageSnippet.split(" ")
        print("SELLING {}".format(words[6]))
        symbol = words[1]
        ticker = public_client.ticker(symbol)
        print(ticker)
        print("Current price is {}. Ask is {}".format(ticker['last_price'], ticker['ask']))
        balance = balances_dict[words[6].lower()]
        print("Current {} balance is {}".format(words[6], balance))
        sell_price = (2*float(ticker['bid']) + float(ticker['ask']))/3
        print("Putting SELL order of {} USD on {} at price {}".format(balance, symbol, sell_price))
        print(trading_client.new_order(balance, sell_price, 'sell', symbol=symbol))
        with open("logs.csv", 'a') as csv_output:
            field_names = ['Timestamp', 'symbol', 'side', 'amount', 'price']
            writer = csv.DictWriter(csv_output, fieldnames=field_names, delimiter=',')
            #writer.writeheader()
            writer.writerow({'Timestamp':int(time.time()), 'symbol':symbol, 'side':'sell', 'amount':balance, 'price':sell_price})        
        print()
        return 0
    else:
        return -1

if __name__ == '__main__':
    # Setup the Gmail API
    SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    #executeOrder("Your IOTUSD alert was triggered: SELL IOT ‌")
    #executeOrder("Your BTCUSD alert was triggered: SELL BTC")

    #TODO create a dictionnary currency:balance
    #for element in balance_request:

    # process mails if they are new and not already processed

    while True:
        print("Alive !")
        #Bitfinex balance
        balance_request = trading_client.balances()
        for element in balance_request:
            balances_dict[element['currency']] = element['available']
        print("USD balance : {}".format(balances_dict['usd']))
        
        # Get last messages (1 day)
        query = service.users().messages().list(userId='me', q='from:noreply@tradingview.com + newer_than:1d').execute()
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
        time.sleep(60)