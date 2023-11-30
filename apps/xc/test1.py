import requests
import json


headers = {
    "authority": "m.ctrip.com",
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://hotels.ctrip.com",
    "p": "31925527702",
    "pragma": "no-cache",
    "referer": "https://hotels.ctrip.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
cookies = {
    "Union": "OUID=index&AllianceID=4897&SID=155952&SourceID=&createtime=1696934370&Expires=1697539170430",
    "MKT_OrderClick": "ASID=4897155952&AID=4897&CSID=155952&OUID=index&CT=1696934370430&CURL=https%3A%2F%2Fwww.ctrip.com%2F%3Fsid%3D155952%26allianceid%3D4897%26ouid%3Dindex&VAL={}",
    "MKT_CKID": "1696934370793.ll2sh.a1ki",
    "MKT_CKID_LMT": "1696934370794",
    "GUID": "09031074214937747423",
    "_RF1": "124.240.84.155",
    "_RSG": "zvK0lH9vEtC0SULvRD.yd9",
    "_RDG": "28a28e51419bc4245809801861e0b22927",
    "_RGUID": "cdcee494-6f01-4e7d-99fc-f8d6f955e700",
    "MKT_Pagesource": "PC",
    "_bfaStatusPVSend": "1",
    "_ubtstatus": "%7B%22vid%22%3A%221696934370623.34tyyy%22%2C%22sid%22%3A1%2C%22pvid%22%3A2%2C%22pid%22%3A102001%7D",
    "_bfi": "p1%3D102001%26p2%3D102001%26v1%3D2%26v2%3D1",
    "_bfaStatus": "success",
    "manualclose": "1",
    "ibulanguage": "CN",
    "ibulocale": "zh_cn",
    "cookiePricesDisplayed": "CNY",
    "_jzqco": "%7C%7C%7C%7C1696934370990%7C1.982593758.1696934370791.1696934449791.1696934528319.1696934449791.1696934528319.0.0.0.3.3",
    "librauuid": "",
    "UBT_VID": "1696934370623.34tyyy",
    "_bfa": "1.1696934370623.34tyyy.1.1696934449460.1696934998235.1.3.102002"
}
url = "https://m.ctrip.com/restapi/soa2/21881/json/HotelSearch"
params = {
    "testab": "bc8ae7b8bd05c8170a147586fadcc218a797cfc8ca27e81ba8532d82288f070e"
}
data = {
    "meta": {
        "fgt": "",
        "hotelId": "",
        "priceToleranceData": "",
        "priceToleranceDataValidationCode": "",
        "mpRoom": [],
        "hotelUniqueKey": "",
        "shoppingid": "",
        "minPrice": "",
        "minCurr": ""
    },
    "seqid": "",
    "deduplication": [],
    "filterCondition": {
        "star": [],
        "rate": "",
        "rateCount": [],
        "priceRange": {
            "lowPrice": 0,
            "highPrice": -1
        },
        "priceType": "",
        "breakfast": [
            3
        ],
        "payType": [],
        "bedType": [],
        "bookPolicy": [],
        "bookable": [],
        "discount": [],
        "hotPoi": [],
        "zone": [],
        "landmark": [],
        "metro": [],
        "airportTrainstation": [],
        "location": [],
        "cityId": [],
        "amenty": [],
        "promotion": [],
        "category": [],
        "feature": [],
        "brand": [],
        "popularFilters": [],
        "hotArea": [],
        "ctripService": [],
        "priceQuickFilters": [],
        "applicablePeople": [],
        "covid": []
    },
    "searchCondition": {
        "sortType": "1",
        "adult": 1,
        "child": 0,
        "age": "",
        "pageNo": 1,
        "optionType": "City",
        "optionId": "2",
        "lat": 0,
        "destination": "",
        "keyword": "",
        "cityName": "上海",
        "lng": 0,
        "cityId": 2,
        "checkIn": "2023-10-10",
        "checkOut": "2023-10-11",
        "roomNum": 1,
        "mapType": "gd",
        "travelPurpose": 0,
        "countryId": 1,
        "url": "https://hotels.ctrip.com/hotels/list?countryId=1&city=2&checkin=2023/10/10&checkout=2023/10/11&optionId=2&optionType=City&directSearch=0&display=%E4%B8%8A%E6%B5%B7&crn=1&adult=1&children=0&searchBoxArg=t&travelPurpose=0&ctm_ref=ix_sb_dl&domestic=1&&highPrice=-1&barCurr=CNY&breakfast=3&sort=1",
        "pageSize": 10,
        "timeOffset": 28800,
        "radius": 0,
        "directSearch": 0,
        "signInHotelId": 0,
        "signInType": 0,
        "hotelIdList": []
    },
    "queryTag": "NORMAL",
    "genk": True,
    "genKeyParam": {
        "a": 0,
        "b": "2023-10-10",
        "c": "2023-10-11",
        "d": "zh-cn",
        "e": 2
    },
    "pageTraceId": "2c9ee4af-4664-4fb5-ab51-aef59db078a6",
    "tsid": "prd-2023_10_10_1-e86988a7-79ca-47e0-9f32-ab11434b5071-hotel_online_list-3.6.2-DOM-online",
    "webpSupport": True,
    "platform": "online",
    "pageID": "102002",
    "head": {
        "Version": "",
        "userRegion": "CN",
        "Locale": "zh-CN",
        "LocaleController": "zh-CN",
        "TimeZone": "8",
        "Currency": "CNY",
        "PageId": "102002",
        "webpSupport": True,
        "userIP": "",
        "P": 31925527702,
        "ticket": "",
        "clientID": "09031074214937747423",
        "group": "ctrip",
        "Frontend": {
            "vid": "1696934370623.34tyyy",
            "sessionID": 1,
            "pvid": 3
        },
        "Union": {
            "AllianceID": "",
            "SID": "",
            "Ouid": ""
        },
        "HotelExtension": {
            "group": "CTRIP",
            "hasAidInUrl": False,
            "Qid": "148254718448",
            "WebpSupport": True,
            "hotelUuidKey": "OpNWUpYDpw6PJ7ceOge8QYd8WgbxXNRhXYhY97RZfrUUx6bYX1EzBvZGjZEgYozJ6pISpJ7nepgE5qj0tWNcr3QrAbvbY5mIpkr9UrTtjptwf7vAOj6Jf7j6oRqZvhDjaJpSjZHwTOvA9jFJPUvg1vF8YZswkfjDHeULiG6YSNJajQ0i1YGcy5dKnyBTyH8jPOvOUEL1vtoW1HjZ6wTmYQMKmYtFK44xS1wMTY1oiZ0wzfR3NEXnWpgE6wpdY5YXmetoeFMrsUetNw9HR5Y3oxBQKfTwnsysNwFtjzYM4IXHeH8JlnvmaYOQyS5jZqvGNeXDYsTj3gygJbcvT5Y5MypFjtAva3eZQYDfj8hyhJd6YXZvSTWMAWAHeNsImj6Ys6RoPET5RsqvBDegfY0Him9YBzK3hvH6wsYGcR1mRPwM9y0wPBIaYltw67vUETAynfv3sY6mwp5jTfemoiLXYcHw06iDbJg6jAfwDBeXqY6FxkkKsAWgaeHMYHYXJDgvboRQoYHUi9kiTOiP9j6OIs3RoTyoYDHezcrsprU9EQAyDNYfQwHXJ9Fyf7YbzwzUiLOiNnyNYg9iXXxsDvTpRh9wLcv5Owhgv76i31EXcv0ovbzYQ1RPfj1URUQrOavtXyGYqLi44x6JqMilOigkR8Y7LR5Or5Eg3RlSwXZvTzw0Qvskit4EN5iHfyBPWFNw8cYfSi0SjQfwllKlY5Ljddx1LYkfjdLwa8vNFjs9JddxbDK3Yasr1Bxf7wmBYkMJz4wp8WsHe4dRhaE30EUzW7TINZwBDYpYc3IGOE7vU5Yk0JfhwGUWSaeM9RhoEZUWfPWzaJ53eF7RFY9Mxp1Ytcr7zRoMw5pvP0wZAvcUiSLEZ7JmgYoFjM9vTmiofWTOW3hxavzYh0jMARN9eQdEkSjhZWb6WogWLAY0bYS8Y38RXAYAPW6ZYq9YQNYD0jdAefLE0pWT9eSBw7qeLOjApY6DypZEMFjbFEltrqTj9Qw1qy3FwpzxgNILYbsR5LWXnW7SWsAW06Y0YpgJohWBSxm6vhBE8BWldyhQjdJlTv07EtLWPkyUsjobeSSxaPraYpNIhQJsHKMnEgSEtLEadR1DEf8R8zx7hK0YbZR4ajP6JTzE1mEBlEM0YzcYcUYAzYp3RsgeGs"
        }
    }
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)

print(response.text)
print(response)