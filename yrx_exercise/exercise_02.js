var btoa = require('btoa');
// var md5 = require('./md5.js');

var hexcase = 0;  /* hex output format. 0 - lowercase; 1 - uppercase        */
var b64pad  = ""; /* base-64 pad character. "=" for strict RFC compliance   */
var chrsz   = 8;  /* bits per input character. 8 - ASCII; 16 - Unicode      */

/*
 * These are the functions you'll usually want to call
 * They take string arguments and return either hex or base-64 encoded strings
 */
function hex_md5(s){ return binl2hex(core_md5(str2binl(s), s.length * chrsz));}
function b64_md5(s){ return binl2b64(core_md5(str2binl(s), s.length * chrsz));}
function str_md5(s){ return binl2str(core_md5(str2binl(s), s.length * chrsz));}
function hex_hmac_md5(key, data) { return binl2hex(core_hmac_md5(key, data)); }
function b64_hmac_md5(key, data) { return binl2b64(core_hmac_md5(key, data)); }
function str_hmac_md5(key, data) { return binl2str(core_hmac_md5(key, data)); }

/*
 * Perform a simple self-test to see if the VM is working
 */
function md5_vm_test()
{
  return hex_md5("abc") == "900150983cd24fb0d6963f7d28e17f72";
}

/*
 * Calculate the MD5 of an array of little-endian words, and a bit length
 */
function core_md5(x, len)
{
  /* append padding */
  x[len >> 5] |= 0x80 << ((len) % 32);
  x[(((len + 64) >>> 9) << 4) + 14] = len;

  var a =  1732584193;
  var b = -271733879;
  var c = -1732584194;
  var d =  271733878;

  for(var i = 0; i < x.length; i += 16)
  {
    var olda = a;
    var oldb = b;
    var oldc = c;
    var oldd = d;

    a = md5_ff(a, b, c, d, x[i+ 0], 7 , -680876936);
    d = md5_ff(d, a, b, c, x[i+ 1], 12, -389564586);
    c = md5_ff(c, d, a, b, x[i+ 2], 17,  606105819);
    b = md5_ff(b, c, d, a, x[i+ 3], 22, -1044525330);
    a = md5_ff(a, b, c, d, x[i+ 4], 7 , -176418897);
    d = md5_ff(d, a, b, c, x[i+ 5], 12,  1200080426);
    c = md5_ff(c, d, a, b, x[i+ 6], 17, -1473231341);
    b = md5_ff(b, c, d, a, x[i+ 7], 22, -45705983);
    a = md5_ff(a, b, c, d, x[i+ 8], 7 ,  1770035416);
    d = md5_ff(d, a, b, c, x[i+ 9], 12, -1958414417);
    c = md5_ff(c, d, a, b, x[i+10], 17, -42063);
    b = md5_ff(b, c, d, a, x[i+11], 22, -1990404162);
    a = md5_ff(a, b, c, d, x[i+12], 7 ,  1804603682);
    d = md5_ff(d, a, b, c, x[i+13], 12, -40341101);
    c = md5_ff(c, d, a, b, x[i+14], 17, -1502002290);
    b = md5_ff(b, c, d, a, x[i+15], 22,  1236535329);

    a = md5_gg(a, b, c, d, x[i+ 1], 5 , -165796510);
    d = md5_gg(d, a, b, c, x[i+ 6], 9 , -1069501632);
    c = md5_gg(c, d, a, b, x[i+11], 14,  643717713);
    b = md5_gg(b, c, d, a, x[i+ 0], 20, -373897302);
    a = md5_gg(a, b, c, d, x[i+ 5], 5 , -701558691);
    d = md5_gg(d, a, b, c, x[i+10], 9 ,  38016083);
    c = md5_gg(c, d, a, b, x[i+15], 14, -660478335);
    b = md5_gg(b, c, d, a, x[i+ 4], 20, -405537848);
    a = md5_gg(a, b, c, d, x[i+ 9], 5 ,  568446438);
    d = md5_gg(d, a, b, c, x[i+14], 9 , -1019803690);
    c = md5_gg(c, d, a, b, x[i+ 3], 14, -187363961);
    b = md5_gg(b, c, d, a, x[i+ 8], 20,  1163531501);
    a = md5_gg(a, b, c, d, x[i+13], 5 , -1444681467);
    d = md5_gg(d, a, b, c, x[i+ 2], 9 , -51403784);
    c = md5_gg(c, d, a, b, x[i+ 7], 14,  1735328473);
    b = md5_gg(b, c, d, a, x[i+12], 20, -1926607734);

    a = md5_hh(a, b, c, d, x[i+ 5], 4 , -378558);
    d = md5_hh(d, a, b, c, x[i+ 8], 11, -2022574463);
    c = md5_hh(c, d, a, b, x[i+11], 16,  1839030562);
    b = md5_hh(b, c, d, a, x[i+14], 23, -35309556);
    a = md5_hh(a, b, c, d, x[i+ 1], 4 , -1530992060);
    d = md5_hh(d, a, b, c, x[i+ 4], 11,  1272893353);
    c = md5_hh(c, d, a, b, x[i+ 7], 16, -155497632);
    b = md5_hh(b, c, d, a, x[i+10], 23, -1094730640);
    a = md5_hh(a, b, c, d, x[i+13], 4 ,  681279174);
    d = md5_hh(d, a, b, c, x[i+ 0], 11, -358537222);
    c = md5_hh(c, d, a, b, x[i+ 3], 16, -722521979);
    b = md5_hh(b, c, d, a, x[i+ 6], 23,  76029189);
    a = md5_hh(a, b, c, d, x[i+ 9], 4 , -640364487);
    d = md5_hh(d, a, b, c, x[i+12], 11, -421815835);
    c = md5_hh(c, d, a, b, x[i+15], 16,  530742520);
    b = md5_hh(b, c, d, a, x[i+ 2], 23, -995338651);

    a = md5_ii(a, b, c, d, x[i+ 0], 6 , -198630844);
    d = md5_ii(d, a, b, c, x[i+ 7], 10,  1126891415);
    c = md5_ii(c, d, a, b, x[i+14], 15, -1416354905);
    b = md5_ii(b, c, d, a, x[i+ 5], 21, -57434055);
    a = md5_ii(a, b, c, d, x[i+12], 6 ,  1700485571);
    d = md5_ii(d, a, b, c, x[i+ 3], 10, -1894986606);
    c = md5_ii(c, d, a, b, x[i+10], 15, -1051523);
    b = md5_ii(b, c, d, a, x[i+ 1], 21, -2054922799);
    a = md5_ii(a, b, c, d, x[i+ 8], 6 ,  1873313359);
    d = md5_ii(d, a, b, c, x[i+15], 10, -30611744);
    c = md5_ii(c, d, a, b, x[i+ 6], 15, -1560198380);
    b = md5_ii(b, c, d, a, x[i+13], 21,  1309151649);
    a = md5_ii(a, b, c, d, x[i+ 4], 6 , -145523070);
    d = md5_ii(d, a, b, c, x[i+11], 10, -1120210379);
    c = md5_ii(c, d, a, b, x[i+ 2], 15,  718787259);
    b = md5_ii(b, c, d, a, x[i+ 9], 21, -343485551);

    a = safe_add(a, olda);
    b = safe_add(b, oldb);
    c = safe_add(c, oldc);
    d = safe_add(d, oldd);
  }
  return Array(a, b, c, d);

}

/*
 * These functions implement the four basic operations the algorithm uses.
 */
function md5_cmn(q, a, b, x, s, t)
{
  return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s),b);
}
function md5_ff(a, b, c, d, x, s, t)
{
  return md5_cmn((b & c) | ((~b) & d), a, b, x, s, t);
}
function md5_gg(a, b, c, d, x, s, t)
{
  return md5_cmn((b & d) | (c & (~d)), a, b, x, s, t);
}
function md5_hh(a, b, c, d, x, s, t)
{
  return md5_cmn(b ^ c ^ d, a, b, x, s, t);
}
function md5_ii(a, b, c, d, x, s, t)
{
  return md5_cmn(c ^ (b | (~d)), a, b, x, s, t);
}

/*
 * Calculate the HMAC-MD5, of a key and some data
 */
function core_hmac_md5(key, data)
{
  var bkey = str2binl(key);
  if(bkey.length > 16) bkey = core_md5(bkey, key.length * chrsz);

  var ipad = Array(16), opad = Array(16);
  for(var i = 0; i < 16; i++)
  {
    ipad[i] = bkey[i] ^ 0x36363636;
    opad[i] = bkey[i] ^ 0x5C5C5C5C;
  }

  var hash = core_md5(ipad.concat(str2binl(data)), 512 + data.length * chrsz);
  return core_md5(opad.concat(hash), 512 + 128);
}

/*
 * Add integers, wrapping at 2^32. This uses 16-bit operations internally
 * to work around bugs in some JS interpreters.
 */
function safe_add(x, y)
{
  var lsw = (x & 0xFFFF) + (y & 0xFFFF);
  var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
  return (msw << 16) | (lsw & 0xFFFF);
}

/*
 * Bitwise rotate a 32-bit number to the left.
 */
function bit_rol(num, cnt)
{
  return (num << cnt) | (num >>> (32 - cnt));
}

/*
 * Convert a string to an array of little-endian words
 * If chrsz is ASCII, characters >255 have their hi-byte silently ignored.
 */
function str2binl(str)
{
  var bin = Array();
  var mask = (1 << chrsz) - 1;
  for(var i = 0; i < str.length * chrsz; i += chrsz)
    bin[i>>5] |= (str.charCodeAt(i / chrsz) & mask) << (i%32);
  return bin;
}

/*
 * Convert an array of little-endian words to a string
 */
function binl2str(bin)
{
  var str = "";
  var mask = (1 << chrsz) - 1;
  for(var i = 0; i < bin.length * 32; i += chrsz)
    str += String.fromCharCode((bin[i>>5] >>> (i % 32)) & mask);
  return str;
}

/*
 * Convert an array of little-endian words to a hex string.
 */
function binl2hex(binarray)
{
  var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
  var str = "";
  for(var i = 0; i < binarray.length * 4; i++)
  {
    str += hex_tab.charAt((binarray[i>>2] >> ((i%4)*8+4)) & 0xF) +
           hex_tab.charAt((binarray[i>>2] >> ((i%4)*8  )) & 0xF);
  }
  return str;
}

/*
 * Convert an array of little-endian words to a base-64 string
 */
function binl2b64(binarray)
{
  var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  var str = "";
  for(var i = 0; i < binarray.length * 4; i += 3)
  {
    var triplet = (((binarray[i   >> 2] >> 8 * ( i   %4)) & 0xFF) << 16)
                | (((binarray[i+1 >> 2] >> 8 * ((i+1)%4)) & 0xFF) << 8 )
                |  ((binarray[i+2 >> 2] >> 8 * ((i+2)%4)) & 0xFF);
    for(var j = 0; j < 4; j++)
    {
      if(i * 8 + j * 6 > binarray.length * 32) str += b64pad;
      else str += tab.charAt((triplet >> 6*(3-j)) & 0x3F);
    }
  }
  return str;
}

var _$oa = ['Q2xsdW8=', 'RG51cWo=', 'bG9n', 'Y2FsbA==', 'RUNkdFk=', 'bWlPWmY=', 'ZENmcms=', 'QnJLR0s=', 'U2phVmU=', 'anlnQ3M=', 'TXhtVVA=', 'Y29va2ll', 'YUZXQ0U=', 'UUNLeFY=', 'eVZwclI=', 'UmN1TkI=', 'c3ZiZ0k=', 'aWV6aXE=', 'eURBS0k=', 'U0JmV1o=', 'ZVRqY3g=', 'TmFXUUU=', 'ZEJBVG8=', 'eGhSblM=', 'b0ttQlc=', 'Y2hhaW4=', 'Y291bnRlcg==', 'aW5wdXQ=', 'eUpQUVc=', 'Z2VPQUw=', 'bGVuZ3Ro', 'cWxKU1c=', 'YnRvYQ==', 'd3lNbXE=', 'dVF6ZEE=', 'c3RhdGVPYmplY3Q=', 'cm91bmQ=', 'dmduYlM=', 'cWNMUHI=', 'd2hpbGUgKHRydWUpIHt9', 'dGlyQVM=', 'WkZrbVk=', 'RUtvdks=', 'dmFsdWVPZg==', 'ZXRTSU0=', 'bHF2Zmo=', 'OyBwYXRoPS8=', 'Y3hudUY=', 'UXBLZ2s=', 'aHpaSW8=', 'RnNTVUQ=', 'ZG9Pd0g=', 'aXhwY3I=', 'QXpqSFI=', 'VWNZdWQ=', 'cm95bmM=', 'RnJGTWM=', 'bmdMWUw=', 'TGplekU=', 'Q1pscVc=', 'YWN0aW9u', 'UmFyRFU=', 'T2hYR0Y=', 'c3RyaW5n', 'YXBwbHk=', 'bnpmalo=', 'cVBkc0s=', 'Z01Dc0o=', 'V05vVlc=', 'YWlkaW5nX3dpbg==', 'alpoR2I=', 'alh6WHI=', 'T1RhQVQ=', 'eXVIWWo=', 'TnFTVmE=', 'TW1yWmo=', 'd0h3eU8=', '5q2k572R6aG15Y+X44CQ54ix6ZSt5LqR55u+IFYxLjAg5Yqo5oCB54mI44CR5L+d5oqk', 'ZnVuY3Rpb24gKlwoICpcKQ==', 'c2lnbj0=', 'bmx4emc=', 'c3BZdHI=', 'SFJKR3M=', 'XCtcKyAqKD86W2EtekEtWl8kXVswLTlhLXpBLVpfJF0qKQ==', 'b3BhRG4=', 'Z2dlcg==', 'dWV2TlU=', 'clVRQUE=', 'eWJxdWU=', 'Qk9CZmE=', 'U3FKWVY=', 'Y093eEk=', 'bVVOZGo=', 'VUlnZXc=', 'ZGVidQ==', 'aW5pdA==', 'Y29uc3RydWN0b3I=', 'bGRISHg=', 'SGNBY3g=', 'd2lZYUM=', 'WHNXR1A=', 'cmVsb2Fk'];
(function(a, b) {
    var c = function(f) {
        while (--f) {
            a['push'](a['shift']());
        }
    };
    c(++b);
}(_$oa, 0x1bf));
var _$ob = function(a, b) {
    a = a - 0x0;
    var c = _$oa[a];
    if (_$ob['WJNHgi'] === undefined) {
        (function() {
            var e = function() {
                var h;
                try {
                    h = Function('return\x20(function()\x20' + '{}.constructor(\x22return\x20this\x22)(\x20)' + ');')();
                } catch (i) {
                    h = window;
                }
                return h;
            };
            var f = e();
            var g = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
            f['atob'] || (f['atob'] = function(h) {
                var i = String(h)['replace'](/=+$/, '');
                var j = '';
                for (var k = 0x0, l, m, n = 0x0; m = i['charAt'](n++); ~m && (l = k % 0x4 ? l * 0x40 + m : m,
                k++ % 0x4) ? j += String['fromCharCode'](0xff & l >> (-0x2 * k & 0x6)) : 0x0) {
                    m = g['indexOf'](m);
                }
                return j;
            }
            );
        }());
        _$ob['XAgEGh'] = function(e) {
            var f = atob(e);
            var g = [];
            for (var h = 0x0, j = f['length']; h < j; h++) {
                g += '%' + ('00' + f['charCodeAt'](h)['toString'](0x10))['slice'](-0x2);
            }
            return decodeURIComponent(g);
        }
        ;
        _$ob['gsMMlZ'] = {};
        _$ob['WJNHgi'] = !![];
    }
    var d = _$ob['gsMMlZ'][a];
    if (d === undefined) {
        c = _$ob['XAgEGh'](c);
        _$ob['gsMMlZ'][a] = c;
    } else {
        c = d;
    }
    return c;
};
(function() {
    var a = {
        'FrFMc': function(d, e) {
            return d + e;
        },
        'DZkkX': _$ob('0x37'),
        'AJWYH': _$ob('0x2e'),
        'wHwyO': _$ob('0x15'),
        'gMCsJ': function(d, e) {
            return d !== e;
        },
        'dgtKS': _$ob('0x4d'),
        'dCfrk': _$ob('0x27'),
        'SBfWZ': _$ob('0x2c'),
        'SqJYV': function(d, e) {
            return d(e);
        },
        'abCjO': _$ob('0x38'),
        'SjaVe': function(d, e) {
            return d + e;
        },
        'CBZFm': _$ob('0x58'),
        'yxYcN': function(d, e) {
            return d + e;
        },
        'geOAL': _$ob('0x5a'),
        'jZhGb': function(d) {
            return d();
        },
        'NqSVa': function(d, e) {
            return d === e;
        },
        'HRJGs': _$ob('0xb'),
        'nlxzg': function(d, e, f) {
            return d(e, f);
        },
        'HcAcx': _$ob('0x26'),
        'QHQEf': function(d, e) {
            return d + e;
        },
        'uevNU': _$ob('0x1e'),
        'JaFHp': function(d, e) {
            return d(e);
        },
        'ngLYL': function(d, e) {
            return d + e;
        },
        'lqvfj': function(d, e) {
            return d(e);
        },
        'uQzdA': function(d, e) {
            return d / e;
        },
        'miOZf': function(d, e) {
            return d + e;
        },
        'NaWQE': function(d, e) {
            return d + e;
        },
        'gOLOK': function(d, e) {
            return d + e;
        },
        'tirAS': _$ob('0x28'),
        'RarDU': _$ob('0x7')
    };
    var b = function() {
        var d = {
            'nzfjZ': function(f, g) {
                return a[_$ob('0x11')](f, g);
            },
            'QCKxV': a['DZkkX'],
            'spYtr': a['AJWYH'],
            'ZFkmY': a[_$ob('0x25')],
            'wiYaC': function(f, g) {
                return a[_$ob('0x1c')](f, g);
            },
            'AhFVN': a['dgtKS']
        };
        var e = !![];
        return function(f, g) {
            var h = {
                'rdSgL': function(j, k) {
                    return d[_$ob('0x1a')](j, k);
                },
                'eTjcx': d[_$ob('0x4c')],
                'ivZmj': d[_$ob('0x2a')],
                'QpKgk': d[_$ob('0x2')],
                'UIgew': function(j, k) {
                    return d[_$ob('0x3c')](j, k);
                },
                'OTaAT': d['AhFVN']
            };
            var i = e ? function() {
                var j = {
                    'ldHHx': function(l, m) {
                        return h['rdSgL'](l, m);
                    },
                    'WNoVW': h[_$ob('0x53')],
                    'wyMmq': h['ivZmj'],
                    'mPatM': h[_$ob('0x9')]
                };
                if (g) {
                    if (h[_$ob('0x36')](h[_$ob('0x21')], h[_$ob('0x21')])) {
                        (function() {
                            return !![];
                        }
                        ['constructor'](pJTHdX[_$ob('0x3a')](pJTHdX[_$ob('0x1d')], pJTHdX[_$ob('0x60')]))[_$ob('0x42')](pJTHdX['mPatM']));
                    } else {
                        var k = g['apply'](f, arguments);
                        g = null;
                        return k;
                    }
                }
            }
            : function() {}
            ;
            e = ![];
            return i;
        }
        ;
    }();
    (function() {
        var d = {
            'OhXGF': a[_$ob('0x45')],
            'svbgI': a[_$ob('0x52')],
            'XsWGP': function(e, f) {
                return a[_$ob('0x33')](e, f);
            },
            'vgnbS': a['abCjO'],
            'UkULt': function(e, f) {
                return a[_$ob('0x47')](e, f);
            },
            'aFWCE': a['CBZFm'],
            'ECdtY': function(e, f) {
                return a['yxYcN'](e, f);
            },
            'OnwpW': a[_$ob('0x5c')],
            'etSIM': function(e, f) {
                return a[_$ob('0x33')](e, f);
            },
            'rUQAA': function(e) {
                return a[_$ob('0x1f')](e);
            }
        };
        if (a[_$ob('0x23')](a[_$ob('0x2b')], a[_$ob('0x2b')])) {
            a[_$ob('0x29')](b, this, function() {
                var e = new RegExp(d[_$ob('0x17')]);
                var f = new RegExp(d[_$ob('0x4f')],'i');
                var g = d[_$ob('0x3d')](_$oc, d[_$ob('0x64')]);
                if (!e['test'](d['UkULt'](g, d[_$ob('0x4b')])) || !f['test'](d[_$ob('0x43')](g, d['OnwpW']))) {
                    d[_$ob('0x5')](g, '0');
                } else {
                    d[_$ob('0x30')](_$oc);
                }
            })();
        } else {
            if (fn) {
                var f = fn[_$ob('0x19')](context, arguments);
                fn = null;
                return f;
            }
        }
    }());
    console[_$ob('0x41')](a[_$ob('0x3b')]);
    var c = new Date()[_$ob('0x4')]();
    token = btoa(a['QHQEf'](a[_$ob('0x2f')], a['SqJYV'](String, c)));
    md = a['JaFHp'](hex_md5, btoa(a[_$ob('0x12')](a[_$ob('0x2f')], a[_$ob('0x6')](String, Math[_$ob('0x63')](a[_$ob('0x61')](c, 0x3e8))))));
    var sign = a[_$ob('0x44')](a[_$ob('0x44')](a[_$ob('0x54')](a[_$ob('0x54')](a['NaWQE'](a['gOLOK'](a[_$ob('0x1')], Math['round'](a[_$ob('0x61')](c, 0x3e8))), '~'), token), '|'), md), a[_$ob('0x16')]);
    // location[_$ob('0x3e')]();

    console.log(sign)
}());
function _$oc(a) {
    var b = {
        'CZlqW': function(d, e) {
            return d(e);
        },
        'xhRnS': function(d, e) {
            return d === e;
        },
        'QZWnT': _$ob('0x18'),
        'MmrZj': function(d, e) {
            return d !== e;
        },
        'iaNQH': 'xJwnU',
        'lWWyR': _$ob('0x0'),
        'Clluo': _$ob('0x59'),
        'ybque': function(d, e) {
            return d + e;
        },
        'opaDn': function(d, e) {
            return d / e;
        },
        'roync': _$ob('0x5d'),
        'jXzXr': function(d, e) {
            return d === e;
        },
        'LQpNR': function(d, e) {
            return d % e;
        },
        'AzjHR': _$ob('0x13'),
        'jygCs': _$ob('0x3'),
        'UcYud': _$ob('0x37'),
        'yDAKI': 'gger',
        'MTRfu': _$ob('0x15'),
        'qPdsK': _$ob('0x22'),
        'ZJjSr': _$ob('0x5e'),
        'BrKGK': function(d, e) {
            return d + e;
        },
        'RcuNB': _$ob('0x62'),
        'qcLPr': function(d) {
            return d();
        },
        'cOwxI': function(d, e) {
            return d(e);
        },
        'BOBfa': function(d, e) {
            return d !== e;
        },
        'yJPQW': _$ob('0xd'),
        'LBUqm': _$ob('0x57'),
        'cxnuF': _$ob('0xa'),
        'doOwH': _$ob('0x49'),
        'ieziq': _$ob('0x40'),
        'dBATo': function(d, e) {
            return d(e);
        }
    };
    function c(d) {
        var e = {
            'mUNdj': function(f, g) {
                return b[_$ob('0x14')](f, g);
            }
        };
        if (b[_$ob('0x56')](typeof d, b['QZWnT'])) {
            if (b[_$ob('0x24')](b['iaNQH'], b['iaNQH'])) {
                if (a) {
                    return c;
                } else {
                    e[_$ob('0x35')](c, 0x0);
                }
            } else {
                return function(g) {}
                [_$ob('0x39')](b['lWWyR'])[_$ob('0x19')](b[_$ob('0x3f')]);
            }
        } else {
            if (b[_$ob('0x24')](b[_$ob('0x31')]('', b[_$ob('0x2d')](d, d))[b[_$ob('0x10')]], 0x1) || b[_$ob('0x20')](b['LQpNR'](d, 0x14), 0x0)) {
                if (b[_$ob('0x20')](b[_$ob('0xe')], b[_$ob('0x48')])) {
                    return !![];
                } else {
                    (function() {
                        return !![];
                    }
                    [_$ob('0x39')](b['ybque'](b[_$ob('0xf')], b[_$ob('0x51')]))[_$ob('0x42')](b['MTRfu']));
                }
            } else {
                if (b[_$ob('0x24')](b[_$ob('0x1b')], b['ZJjSr'])) {
                    (function() {
                        return ![];
                    }
                    ['constructor'](b[_$ob('0x46')](b['UcYud'], b[_$ob('0x51')]))[_$ob('0x19')](b[_$ob('0x4e')]));
                } else {
                    return c;
                }
            }
        }
        b['CZlqW'](c, ++d);
    }
    try {
        if (b[_$ob('0x32')](b[_$ob('0x5b')], b['LBUqm'])) {
            if (a) {
                if (b['jXzXr'](b[_$ob('0x8')], b[_$ob('0x8')])) {
                    return c;
                } else {
                    b[_$ob('0x65')](_$oc);
                }
            } else {
                if (b[_$ob('0x32')](b[_$ob('0xc')], b[_$ob('0x50')])) {
                    b[_$ob('0x55')](c, 0x0);
                } else {
                    b[_$ob('0x14')](c, 0x0);
                }
            }
        } else {
            b[_$ob('0x34')](result, '0');
        }
    } catch (g) {}
}

