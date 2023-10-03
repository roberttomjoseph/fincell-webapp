import http.client

conn = http.client.HTTPSConnection("apiconnect.angelbroking.com")
payload = {
    "mode": "FULL",
    "exchangeTokens": {
        "NSE": ["3045"]
    }
}
headers = {
  'X-PrivateKey': 'BYZCB0Mu',
  'Accept': 'application/json',
  'X-SourceID': 'WEB',
  'X-ClientLocalIP': 'CLIENT_LOCAL_IP',
  'X-ClientPublicIP': 'CLIENT_PUBLIC_IP',
  'X-MACAddress': 'MAC_ADDRESS',
  'X-UserType': 'USER',
  'Authorization': 'Bearer AUTHORIZATION_TOKEN',
  'Accept': 'application/json',
  'X-SourceID': 'WEB',
  'Content-Type': 'application/json'
}
conn.request("POST", "rest/secure/angelbroking/market/v1/quote/", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))