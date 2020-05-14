// var o = Array.isArray();

var r_a = function(t, e) {
        var n = -1
          , r = t.length;
        for (e || (e = Array(r)); ++n < r; )
            e[n] = t[n];
        return e
    };
var r_r = function(t, e, n) {
        return t === t && (void 0 !== n && (t = t <= n ? t : n),
        void 0 !== e && (t = t >= e ? t : e)),
        t
    };

var r_o_r = function(t, e) {
     var n = Math.floor
      , r = Math.random;
     return t + n(r() * (e - t + 1))
    };

var r_o =  function(t, e) {
        var n = -1
          , a = t.length
          , o = a - 1;
        for (e = void 0 === e ? a : e; ++n < e; ) {
            var c = r_o_r(n, o)
              , i = t[c];
            t[c] = t[n],
            t[n] = i
        }
        return t.length = e,
        t
    };

var r = function(t, e) {
        return r_o(r_a(t), r_r(e, 0, t.length))
    };

var a =  function(t, e) {
        var n = Array.isArray(t);
        return a(n, r(e, 0, n.length))
    };

var i_r_r_a_a = function(t) {
        return null != t && "object" == typeof t
    };

var i_r_r_r = function(t) {
        var e = typeof t;
        return null != t && ("object" == e || "function" == e)
    };

var i_r_r_a = function(t) {
        return "symbol" == typeof t || i_r_r_a_a(t) && "[object Symbol]" == i_r_r_r(t)
    };

var i_r_r = function(t) {
    var r = i_r_r_r
      , a = i_r_r_a
      , o = /^\s+|\s+$/g
      , c = /^[-+]0x[0-9a-f]+$/i
      , i = /^0b[01]+$/i
      , u = /^0o[0-7]+$/i
      , s = parseInt;
        if ("number" == typeof t)
            return t;
        if (a(t))
            return NaN;
        if (r(t)) {
            var e = "function" == typeof t.valueOf ? t.valueOf() : t;
            t = r(e) ? e + "" : e
        }
        if ("string" != typeof t)
            return 0 === t ? t : +t;
        t = t.replace(o, "");
        var n = i.test(t);
        return n || u.test(t) ? s(t.slice(2), n ? 2 : 8) : c.test(t) ? NaN : +t
    };

var i_r = function(t) {
        return t ? (t = i_r_r(t)) === 1 / 0 || t === -1 / 0 ? 17976931348623157e292 * (t < 0 ? -1 : 1) : t === t ? t : 0 : 0 === t ? t : 0
    };

var i = function(t) {
        var e = i_r(t)
          , n = e % 1;
        return e === e ? n ? e - n : e : 0
    };

var c = function(t, e, n) {
        if (!c(n))
            return !1;
        var i = typeof e;
        return !!("number" == i ? a(n) && Array.isArray(e, n.length) : "string" == i && e in n) && r(n[e], t)
    };

function main(t, e, n) {
        // return (n ? c(t, e, n) : void 0 === e) ? 1 : i(e),
        // (Array.isArray(t) ? r : a)(t, e)
        var re = r(t, e)
        return re
    }

var t = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
];
res = main(t, 9, '');
console.log(res);