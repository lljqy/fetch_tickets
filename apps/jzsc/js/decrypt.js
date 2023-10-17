var crypto = require('crypto-js')

function extract(t) {
    var f = {"words": [1785673834, 964118391, 624314466, 2019968622], "sigBytes": 16}
    var h = {"words": [808530483, 875902519, 943276354, 1128547654], "sigBytes": 16}
    var e = crypto.enc.Hex.parse(t)
        , n = crypto.enc.Base64.stringify(e)
        , a = crypto.AES.decrypt(n, f, {
        iv: h,
        mode: crypto.mode.CBC,
        padding: crypto.pad.Pkcs7
    })
        , r = a.toString(crypto.enc.Utf8);
    return JSON.parse(r.toString())
}