from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import json
import logging
import os
import requests
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
'''這是Line Bot上線後第二版 依照老闆意願改輸出格式'''
line_bot_api = LineBotApi(os.getenv('ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('SECRET'))

def get_price(reqMes):  
    requestURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?'
    reqSymbol = 'symbol='
    reqID = 'id='
    reqConvert = '&convert='
    cryConv = 'USD'
    searchKey = reqMes.split()
    keyword = str(searchKey[0]).upper()
    if keyword == 'PP' or keyword == 'P':
        cryPtoc = str(searchKey[1]).upper()
        if len(searchKey) == 3:
            cryConv = str(searchKey[2]).upper()
    

    request = requests.get(requestURL+reqSymbol+cryPtoc+reqConvert+cryConv,headers={'X-CMC_PRO_API_KEY': os.getenv('X_CMC_PRO_API_KEY')})
    data = request.json()
    if data['status']['error_code'] == 0:
        coin = data['data'][cryPtoc]
        #print(json.dumps(coin, indent=4, sort_keys=True))

        name = coin['name'] #Name
        symbol = coin['symbol'] #Symbol
        mxsup = coin['max_supply'] #Maximum supply
        ttsup = coin['total_supply'] #Total supply
        ccsup = coin['circulating_supply'] #Circulating supply
        cmcrank = coin['cmc_rank'] #CMC Rank

        priceAll = coin['quote'][cryConv]
        mkcap = priceAll['market_cap']
        pc1h = priceAll['percent_change_1h']
        pc24h = priceAll['percent_change_24h']
        pc7d = priceAll['percent_change_7d']
        price = priceAll['price']
        vol24 = priceAll['volume_24h']
        
        if keyword == 'PP':
            rep_Mes = '｜{}({})｜#{}\n\n'.format(name,symbol,cmcrank)+\
            '【時價】\n{:,.6f} {}'.format(price,cryConv)+'\n\n'+\
            '【漲跌幅】\n'+\
            '(1小) {:.3%}'.format(pc1h/100)+'\n'+\
            '(1日) {:.3%}'.format(pc24h/100)+'\n'+\
            '(7日) {:.3%}'.format(pc7d/100)+'\n\n'+\
            '【市值】\n{:,.6f} {}'.format(mkcap,cryConv)+'\n\n'+\
            '【市流通量】\n{:,} {}'.format(ccsup,symbol)+'\n\n'+\
            '【總供應量】\n{:,} {}'.format(ttsup,symbol)+'\n\n'+\
            '【24hr 交易量】\n{:,.6f} {}'.format(vol24,cryConv)

        elif keyword == 'P':
            rep_Mes = '｜{}({})｜#{}\n\n'.format(name,symbol,cmcrank)+\
            '【時價】\n{:,.6f} {}'.format(price,cryConv)+'\n\n'+\
            '【漲跌幅】\n'+\
            '(1小) {:.3%}'.format(pc1h/100)+'\n'+\
            '(1日) {:.3%}'.format(pc24h/100)
        
        return rep_Mes

        

def lambda_handler(event, context):
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=get_price(event.message.text)))
    try:
        # get X-Line-Signature header value
        signature = event['headers']['X-Line-Signature']
        # get event body
        body = event['body']
        # handle webhook body
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {'statusCode': 400, 'body': 'InvalidSignature'}
    except Exception as e:
        return {'statusCode': 400, 'body': json.dump(e)}
    return {'statusCode': 200, 'body': 'OK'}
