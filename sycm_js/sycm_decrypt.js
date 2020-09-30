/*
    完全使用js代码实现生意参谋市场数据data解密
*/

var f_a_init = function(e, t) {
                    e = this.words = e || [],
                    this.sigBytes = null != t ? t : 4 * e.length
                };

var f_u_stringify = function(e) {
                for (var t = e.words, n = e.sigBytes, r = [], o = 0; o < n; o++) {
                    var i = t[o >>> 2] >>> 24 - o % 4 * 8 & 255;
                    r.push(String.fromCharCode(i))
                }
                return r.join("")
            };

var f_u_parse = function(e) {
                for (var t = e.length, n = [], r = 0; r < t; r++)
                    n[r >>> 2] |= (255 & e.charCodeAt(r)) << 24 - r % 4 * 8;
                return new f_a_init(n,t)
            };

var f_Utf8 = {
    stringify: function (e) {
        try {
            return decodeURIComponent(escape(f_u_stringify(e)))
        } catch (e) {
            throw new Error("Malformed UTF-8 data")
        }
    },
    parse: function (e) {
        return f_u_parse(unescape(encodeURIComponent(e)))
    }
};

var f_Hex = {
    stringify: function(e) {
        for (var t = e.words, n = e.sigBytes, r = [], o = 0; o < n; o++) {
            var i = t[o >>> 2] >>> 24 - o % 4 * 8 & 255;
            r.push((i >>> 4).toString(16)),
            r.push((15 & i).toString(16))
        }
        return r.join("")
    },
    parse: function(e) {
        for (var t = e.length, n = [], r = 0; r < t; r += 2)
            n[r >>> 3] |= parseInt(e.substr(r, 2), 16) << 24 - r % 8 * 4;
        return new f_a_init(n,t / 2)
    }
};

var f_base64_stringify = function(e) {
    var t = e.words
      , n = e.sigBytes
      , r = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
    // e.clamp();
    for (var o = [], i = 0; i < n; i += 3)
        for (var a = (t[i >>> 2] >>> 24 - i % 4 * 8 & 255) << 16 | (t[i + 1 >>> 2] >>> 24 - (i + 1) % 4 * 8 & 255) << 8 | t[i + 2 >>> 2] >>> 24 - (i + 2) % 4 * 8 & 255, c = 0; c < 4 && i + .75 * c < n; c++)
            o.push(r.charAt(a >>> 6 * (3 - c) & 63));
    var s = r.charAt(64);
    if (s)
        for (; o.length % 4; )
            o.push(s);
    return o.join("")
};

var f_Pkcs7 = {
    pad: function(e, t) {
        for (var n = 4 * t, r = n - e.sigBytes % n, o = r << 24 | r << 16 | r << 8 | r, i = [], a = 0; a < r; a += 4)
            i.push(o);
        var s = c.create(i, r);
        e.concat(s)
    },
    unpad: function(e) {
        var t = 255 & e.words[e.sigBytes - 1 >>> 2];
        e.sigBytes -= t
    }
};

var f_create = function() {
                var e = this.extend();
                return e.init.apply(e, arguments),
                e
            };

var f_invKeySchedule = function (u, lfdpi) {
    var o = lfdpi['o'];
    var l = lfdpi['l'];
    var f = lfdpi['f'];
    var d = lfdpi['d'];
    var p = lfdpi['p'];
    var h = [0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54]
    for (var e = u, t = e.words, n = e.sigBytes / 4, r = 4 * ((n + 6) + 1), i = [], a = 0; a < r; a++)
        if (a < n)
            i[a] = t[a];
        else {
            var c = i[a - 1];
            a % n ? n > 6 && a % n == 4 && (c = o[c >>> 24] << 24 | o[c >>> 16 & 255] << 16 | o[c >>> 8 & 255] << 8 | o[255 & c]) : (c = o[(c = c << 8 | c >>> 24) >>> 24] << 24 | o[c >>> 16 & 255] << 16 | o[c >>> 8 & 255] << 8 | o[255 & c],
                c ^= h[a / n | 0] << 24),
                i[a] = i[a - n] ^ c
        }
    for (var s = [], u = 0; u < r; u++)
        a = r - u,
            c = u % 4 ? i[a] : i[a - 4],
            s[u] = u < 4 || a <= 4 ? c : l[o[c >>> 24]] ^ f[o[c >>> 16 & 255]] ^ d[o[c >>> 8 & 255]] ^ p[o[255 & c]]
    return s
};

var f_get_lfdpi = function() {
    var e = r
        , o = []
        , i = []
        , a = []
        , c = []
        , s = []
        , u = []
        , l = []
        , f = []
        , d = []
        , p = [];
    for (var e = [], t = 0; t < 256; t++)
        e[t] = t < 128 ? t << 1 : t << 1 ^ 283;
    var n = 0
        , r = 0;
    for (t = 0; t < 256; t++) {
        var h = r ^ r << 1 ^ r << 2 ^ r << 3 ^ r << 4;
        h = h >>> 8 ^ 255 & h ^ 99,
            o[n] = h,
            i[h] = n;
        var m = e[n]
            , b = e[m]
            , y = e[b]
            , g = 257 * e[h] ^ 16843008 * h;
        a[n] = g << 24 | g >>> 8,
            c[n] = g << 16 | g >>> 16,
            s[n] = g << 8 | g >>> 24,
            u[n] = g,
            g = 16843009 * y ^ 65537 * b ^ 257 * m ^ 16843008 * n,
            l[h] = g << 24 | g >>> 8,
            f[h] = g << 16 | g >>> 16,
            d[h] = g << 8 | g >>> 24,
            p[h] = g,
            n ? (n = m ^ e[e[e[y ^ m]]],
                r ^= e[e[r]]) : n = r = 1
    }

    return {
        'l': l,
        'f': f,
        'd': d,
        'p': p,
        'i': i,
        'o': o,
    }
};

var f_parse = function(e) {
            var t = e.length
              , n = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
              , r = [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, 62, null, null, null, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, null, null, null, 64, null, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, null, null, null, null, null, null, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51];
            if (!r) {
                r = [];
                for (var i = 0; i < n.length; i++)
                    r[n.charCodeAt(i)] = i
            }
            var a = n.charAt(64);
            if (a) {
                var c = e.indexOf(a);
                -1 !== c && (t = c)
            }
            return function(e, t, n) {
                for (var r = [], i = 0, a = 0; a < t; a++)
                    if (a % 4) {
                        var c = n[e.charCodeAt(a - 1)] << a % 4 * 2
                          , s = n[e.charCodeAt(a)] >>> 6 - a % 4 * 2;
                        r[i >>> 2] |= (c | s) << 24 - i % 4 * 8,
                        i++
                    }
                // return o.create(r, i)
                return  {
                        'words': r,
                        'sigBytes': i
                        }
            }(e, t, r)
        };

var f_doCryptBlock = function(e, t, n, r, o, i, a, c) {
    for (var s = 10, u = e[t] ^ n[0], l = e[t + 1] ^ n[1], f = e[t + 2] ^ n[2], d = e[t + 3] ^ n[3], p = 4, h = 1; h < s; h++) {
        var b = r[u >>> 24] ^ o[l >>> 16 & 255] ^ i[f >>> 8 & 255] ^ a[255 & d] ^ n[p++]
          , m = r[l >>> 24] ^ o[f >>> 16 & 255] ^ i[d >>> 8 & 255] ^ a[255 & u] ^ n[p++]
          , g = r[f >>> 24] ^ o[d >>> 16 & 255] ^ i[u >>> 8 & 255] ^ a[255 & l] ^ n[p++]
          , y = r[d >>> 24] ^ o[u >>> 16 & 255] ^ i[l >>> 8 & 255] ^ a[255 & f] ^ n[p++];
        u = b,
        l = m,
        f = g,
        d = y
    }
    b = (c[u >>> 24] << 24 | c[l >>> 16 & 255] << 16 | c[f >>> 8 & 255] << 8 | c[255 & d]) ^ n[p++],
    m = (c[l >>> 24] << 24 | c[f >>> 16 & 255] << 16 | c[d >>> 8 & 255] << 8 | c[255 & u]) ^ n[p++],
    g = (c[f >>> 24] << 24 | c[d >>> 16 & 255] << 16 | c[u >>> 8 & 255] << 8 | c[255 & l]) ^ n[p++],
    y = (c[d >>> 24] << 24 | c[u >>> 16 & 255] << 16 | c[l >>> 8 & 255] << 8 | c[255 & f]) ^ n[p++],
    e[t] = b,
    e[t + 1] = m,
    e[t + 2] = g,
    e[t + 3] = y
};

var f_decryptBlock = function(e, t, lfdpi, _invKeySchedule) {
                var n = e[t + 1];
                e[t + 1] = e[t + 3],
                e[t + 3] = n,
                f_doCryptBlock(e, t, _invKeySchedule, lfdpi['l'], lfdpi['f'], lfdpi['d'], lfdpi['p'], lfdpi['i']),
                n = e[t + 1],
                e[t + 1] = e[t + 3],
                e[t + 3] = n;
                return e
            };

var f_call = function (t, n, r, iv) {
    var o = iv;
    for (var i = 0; i < r; i++)
       t[n + i] ^= o[i]
    return t
};

var f_processBlock = function(e, n, iv, lfdpi, _invKeySchedule) {
                var o = 4
                  , i = e.slice(n, n + o);
                var r = f_decryptBlock(e, n, lfdpi, _invKeySchedule),

                r = f_call(r, n, o, iv),
                iv = i;
                return {
                    'r': r,
                    'iv': iv
                }

            };

var f_process = function(data, t, iv, lfdpi, _invKeySchedule) {
                var n = data
                  , r = n.words
                  , o = n.sigBytes
                  , i = 4
                  , c = o / (4 * i)
                  , s = (c = t ? Math.ceil(c) : Math.max((0 | c) - 1, 0)) * i
                  , u = Math.min(4 * s, o);
                if (s) {
                    for (var l = 0; l < s; l += i){
                        var res = f_processBlock(r, l, iv, lfdpi, _invKeySchedule);
                        r = res["r"];
                        iv = res["iv"]
                    }

                    var f = r.splice(0, s);
                    n.sigBytes -= u
                }
                return new f_a_init(f, u)
            };


function main(e, t, n) {
    "use strict";
    var s = "w28Cz694s63kBYk4"
      , u = f_Utf8.parse(s)
      , iv = f_Utf8.parse(s.split("").reverse().join("")).words;

    var lfdpi = f_get_lfdpi();
    var _invKeySchedule = f_invKeySchedule(u, lfdpi);
    // var data1 = f_base64_stringify(f_Hex.parse(e));
    // var data2 = f_parse(data1);
    var data2 = f_Hex.parse(e);

    var t = true;
    var res =  f_process(data2, t, iv, lfdpi, _invKeySchedule);
    var res_data = f_Utf8.stringify(res);
    return res_data
}

data = '';
res_data = main(data, '', '');

console.log(res_data);