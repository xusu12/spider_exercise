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
    // stringify: function (e) {
    //     try {
    //         return decodeURIComponent(escape(f_u_stringify(e)))
    //     } catch (e) {
    //         throw new Error("Malformed UTF-8 data")
    //     }
    // },
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

var f_decryptBlock = function(e, t) {
                var n = e[t + 1];
                e[t + 1] = e[t + 3],
                e[t + 3] = n,
                f_doCryptBlock(e, t, this._invKeySchedule, l, f, d, p, i),
                n = e[t + 1],
                e[t + 1] = e[t + 3],
                e[t + 3] = n
            };

var f_processBlock = function(e, n) {
                var o = 4
                  , i = e.slice(n, n + o);
                f_decryptBlock(e, n),
                t.call(this, e, n, o),
                this._prevBlock = i
            };

var f_process = function(data, t) {
                var n = data
                  , r = n.words
                  , o = n.sigBytes
                  , i = 4
                  , c = o / (4 * i)
                  , s = (c = t ? Math.ceil(c) : Math.max((0 | c) - 1, 0)) * i
                  , u = Math.min(4 * s, o);
                if (s) {
                    for (var l = 0; l < s; l += i)
                        f_processBlock(r, l);
                    var f = r.splice(0, s);
                    n.sigBytes -= u
                }
                return new f_a_init(f, u)
            };


function main(e, t, n) {
    "use strict";
    var s = "w28Cz694s63kBYk4"
      , u = f_Utf8.parse(s);
    console.log(u);
      // , l = {
      //       iv: f_Utf8.parse("4kYBk36s496zC82w"),
      //       // mode: f_CBC,
      //       padding: f_Pkcs7
      //   };
    var data1 = f_base64_stringify(f_Hex.parse(e));
    var data2 = f_parse(data1);

    var t = true;
    var res =  f_process(data2, t);

    // console.log(data1);
    // console.log(data2);
    console.log(res)
}

data = 'D4DB6D83FCCA89E3152182CE2CD197DEE81FA68C0074BD235B4BF60278BC73E98A33119D9127E2CDBC8B7DD24C3EE304091C5C58FE2A1E86FD26EF0553E27C03540E181E9A7222978CE2CF494A28921CE0E8DDD32E5E4906DD9FB4FDB43111D0F03C628A1CCF3A883CCA94F2E121DB0EC2ECEC8B008FDE6E8B6FF0E9D345F89E4B3EA305D831E10B6CFF078273DE1A36A53A96D07B0A2DDBF2C9DE51BD693662FD4BE1398764D8FCE1D6F9785E8E8D33919C466706A775F21F46F4ED30F7E1F4A2524BE3DD869684D57004183829E2ABBD266C74267C013F4679ED8F74DB2F2D5F989B392BC834501A6183E60805F480FBE0CA659EF4EBF94A35E3E87C8796B34A6C4607E6EFE2F5907547B93FEEC175869923D66005E0C40D0A34BCF72F9451928F83F5ED3319CD6ADB57C073D43B95E44A74083DDA5BC54CD483C2A600213DE21531CCEA1CE9617A4704E04E7AC34A818770587698E53E75844188C22D88E3AA4CFDF843A51897E9C651B295B632F5F0282C1FBE030F6856187820244F25341964BF0C861898C1389DACD0E98839EEBCAB0C3211760337816661102137332D1AB74B94AD3DD405D5801A21F13F9DFE93C8C904C94CBD70A2674A73CC888CAE2A1870321250CB8DE35C7F228CB1C8F670521C5744F20C634E58821F7E91D51D90918962254F939D9FE8587F304F2137E0FA9DAF7B1092FE87D2B16A1333EAED74A78949EE73057A143E03C07A5EF04971D690D9FB11F889003B15F9199AD9B1768C9832D11A8E6BE0CAF098567D6A09';
main(data, '', '');