var timestamp;

//---------生成sign使用的方法----------//
function clamp(t) {
    var e = t.words
        , i = t.sigBytes;
    e[i >>> 2] &= 4294967295 << 32 - i % 4 * 8,
        e.length = Math.ceil(i / 4)
}

function f_stringify(t) {
    var e = t.words
        , i = t.sigBytes
        , r = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
    clamp(t);
    for (var n = [], o = 0; o < i; o += 3)
        for (var s = (e[o >>> 2] >>> 24 - o % 4 * 8 & 255) << 16 | (e[o + 1 >>> 2] >>> 24 - (o + 1) % 4 * 8 & 255) << 8 | e[o + 2 >>> 2] >>> 24 - (o + 2) % 4 * 8 & 255, a = 0; a < 4 && o + .75 * a < i; a++)
            n.push(r.charAt(s >>> 6 * (3 - a) & 63));
    var h = r.charAt(64);
    if (h)
        for (; n.length % 4; )
            n.push(h);
    return n.join("")
}
//----------------------------------//

//--------生成words使用的方法---------//
function f_clamp() {
    var e = this.words
        , i = this.sigBytes;
    e[i >>> 2] &= 4294967295 << 32 - i % 4 * 8,
        e.length = Math.ceil(i / 4)
}

function f_concat(t) {
    var e = this.words
      , i = t.words
      , r = this.sigBytes
      , n = t.sigBytes;
    if (f_clamp(),
    r % 4)
        for (var o = 0; o < n; o++) {
            var s = i[o >>> 2] >>> 24 - o % 4 * 8 & 255;
            e[r + o >>> 2] |= s << 24 - (r + o) % 4 * 8
        }
    else
        for (o = 0; o < n; o += 4)
            e[r + o >>> 2] = i[o >>> 2];
    return this.sigBytes += n,
    this
}

function f_init(t, e) {
    t = this.words = t || [],
    this.sigBytes = null != e ? e : 4 * t.length
}

function p_parse(t) {

    for (var e = t.length, i = [], r = 0; r < e; r++)
        i[r >>> 2] |= (255 & t.charCodeAt(r)) << 24 - r % 4 * 8;
    return new f_init(i,e)
}

function append(t) {
    f_init()
    this._nDataBytes=0
    "string" == typeof t && (t = p_parse(t))
    f_concat(t),
    this._nDataBytes += t.sigBytes,
    this._data = t
}

function f_doProcessBlock (t, e) {
    var h = [];
    this._hash = new f_init([1732584193, 4023233417, 2562383102, 271733878, 3285377520]);
    for (var i = this._hash.words, r = i[0], n = i[1], o = i[2], s = i[3], a = i[4], u = 0; u < 80; u++) {
        if (u < 16)
            h[u] = 0 | t[e + u];
        else {
            var f = h[u - 3] ^ h[u - 8] ^ h[u - 14] ^ h[u - 16];
            h[u] = f << 1 | f >>> 31
        }
        var l = (r << 5 | r >>> 27) + a + h[u];
        l += u < 20 ? 1518500249 + (n & o | ~n & s) : u < 40 ? 1859775393 + (n ^ o ^ s) : u < 60 ? (n & o | n & s | o & s) - 1894007588 : (n ^ o ^ s) - 899497514,
            a = s,
            s = o,
            o = n << 30 | n >>> 2,
            n = r,
            r = l
    }
    i[0] = i[0] + r | 0,
    i[1] = i[1] + n | 0,
    i[2] = i[2] + o | 0,
    i[3] = i[3] + s | 0,
    i[4] = i[4] + a | 0
}

function f_doFinalize() {
    var t = this._data
        , e = t.words
        , i = 8 * this._nDataBytes
        , r = 8 * t.sigBytes;
    return e[r >>> 5] |= 128 << 24 - r % 32,
        e[14 + (r + 64 >>> 9 << 4)] = Math.floor(i / 4294967296),
        e[15 + (r + 64 >>> 9 << 4)] = i,
        t.sigBytes = 4 * e.length,
        // this._process(),
        f_doProcessBlock(t.words, 0)
        this._hash
}

function ce(t) {
    return t && append(t),
    f_doFinalize()
}
//------------------------------//

function we(t) {
    return (we = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(t) {
        return typeof t
    }
    : function(t) {
        return t && "function" == typeof Symbol && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t
    }
    )(t)
}

function ve(t) {
    var e = {}.toString.call(t);
    return /^\[object (\w+)\]$/.exec(e)[1]
}

function encryptSignApi(t, e, i) {
    if (!t || !e)
        return console.error("请给出正确的url或params"),
        {};
    var r = {}
      , n = !i || !i.hasOwnProperty("useSignApi") || i.useSignApi;
    var mi = ["/kuaiche/keyword/list", "/kuaiche/dmp/search/list", "/kuaiche/ad/list", "/kuaiche/adgroup/list", "/common/keyword/price/batch/update", "/common/sku/info", "/kuaiche/adgroup/add", "/common/keyword/sku/recommend", "/common/keyword/insert", "/featured/dmp/recommend/list", "/touchpoint/dmp/list", "/api/download/common/asyn/download/reportInfo/ids"];
    return (mi.indexOf(t) > -1 || !n) && (r = function(t, e) {
        if ("Object" === ve(t)) {
            var i = Object.assign({}, t || {})
              , r = e && e.publicKey || "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCK0GF/A3P7a1PNPh9ZNcprFnFUi/2w2C97vCFxyCgggtcT3BpCV8Yc32HWYR3a2Gtk1LF456ZB4kI9EbxJMl3bnK9esD/cQ1TD1YoPmey5S6UaVgO1IKGDx2OomvLUfbRMmTOUtttCogD9ps3knL15DvfhXiaAjMML8Ck8bDPXZQIDAQAB\n-----END PUBLIC KEY-----"
              , n = e && e.uniqueKey || (new Date).getTime()
              , o = "";
            i.key = n,
            Object.keys(i).filter((function(t) {
                return ["number", "string"].includes(we(i[t]))
            }
            )).sort().forEach((function(t, e) {
                o += (0 === e ? "" : "&") + t + "=" + i[t]
            }
            ));
            var s = ce(o)
              , sign = f_stringify(this._hash);
            timestamp = n;
            return sign
        }
    }(e, i) || {}),
    r
}
let e = {
    ids: [5644221],
    requestFrom: 0,
    deliverySystemType: 0
};
let t = "/api/download/common/asyn/download/reportInfo/ids";
sign = encryptSignApi(t, e);

// 通过rsa算法对timestamp加密, 配合sign一起 (sign的生成也是和这个timestamp相关)
console.log(timestamp, sign);