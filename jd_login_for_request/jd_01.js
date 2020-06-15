function f_st(d) {
    var c = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-~".split("")
      , b = c.length
          , e = +d
          , a = [];
        do {
            mod = e % b;
            e = (e - mod) / b;
            a.unshift(c[mod])
        } while (e);return a.join("")
};

function f_pi(a, b) {
        return (Array(b).join(0) + a).slice(-b)
    };

function g_pm(d, c, b) {
    var f = this;
        var e = f_st(Math.abs(d));
        var a = "";
        if (!b) {
            a += (d > 0 ? "1" : "0")
        }
        a += f_pi(e, c);
        return a
};

function gc(c) {
        var g = this;
        var b = new Array();
        for (var e = 0; e < c.length; e++) {
            if (e == 0) {
                b.push(g_pm(c[e][0] < 262143 ? c[e][0] : 262143, 3, true));
                b.push(g_pm(c[e][1] < 16777215 ? c[e][1] : 16777215, 4, true));
                b.push(g_pm(c[e][2] < 4398046511103 ? c[e][2] : 4398046511103, 7, true))
            } else {
                var a = c[e][0] - c[e - 1][0];
                var f = c[e][1] - c[e - 1][1];
                var d = c[e][2] - c[e - 1][2];
                b.push(g_pm(a < 4095 ? a : 4095, 2, false));
                b.push(g_pm(f < 4095 ? f : 4095, 2, false));
                b.push(g_pm(d < 16777215 ? d : 16777215, 4, true))
            }
        }
        return b.join("")
    }

var lis = [["897", "178", 1592041222173],
["926", "204", 1592041222173],
["926", "204", 1592041222462],
["926", "204", 1592041222466],
["927", "204", 1592041222474],
["927", "204", 1592041222482],
["927", "204", 1592041222488],
["928", "204", 1592041222500],
["928", "204", 1592041222505],
["928", "204", 1592041222514],
["928", "204", 1592041222521],
["929", "204", 1592041222529],
["929", "204", 1592041222538],
["929", "204", 1592041222545],
["929", "204", 1592041222553],
["930", "204", 1592041222562],
["930", "204", 1592041222568],
["931", "204", 1592041222577],
["931", "204", 1592041222586],
["931", "204", 1592041222596],
["932", "204", 1592041222601],
["932", "203", 1592041222608],
["932", "203", 1592041222615],
["932", "203", 1592041222625],
["933", "203", 1592041222633],
["933", "203", 1592041222641],
["933", "203", 1592041222648],
["933", "203", 1592041222657],
["934", "203", 1592041222665],
["934", "203", 1592041222671],
["934", "203", 1592041222688],
["934", "203", 1592041222704],
["934", "203", 1592041222769],
["934", "203", 1592041222816]];

// var res = gc(lis);
// console.log(res);