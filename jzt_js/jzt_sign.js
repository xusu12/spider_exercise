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

var t = {
    sigBytes: 20,
    words: [-1852769082, -737475379, 1008862044, -1661795697, 812380903]
}
res = f_stringify(t)
console.log(res)
