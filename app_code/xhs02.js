function showStacks(){
    var stack = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new());
    // var stack = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Throwable").$new());
    console.log(stack);
}



/*
    com.xingin.alioth.d.b


    public static String b() {
        StringBuilder sb = new StringBuilder();
        sb.append(String.valueOf(System.currentTimeMillis()) + "");
        String format = String.format("%064d", Arrays.copyOf(new Object[]{Long.valueOf((long) (Math.random() * 9.223372036854776E18d))}, 1));
        m.a((Object) format, "java.lang.String.format(format, *args)");
        sb.append(format);
        String b2 = v.b(sb.toString());
        m.a((Object) b2, "MD5Util.md5(timeStr + St….format(\"%064d\", random))");
        return b2;
    }


    com.xingin.utils.core.v

    public static String b(String str) {
        return a(str.getBytes(StandardCharsets.UTF_8));
    }

    public static String a(byte[] bArr) {
        try {
            MessageDigest instance = MessageDigest.getInstance("MD5");
            instance.update(bArr);
            return am.a(instance.digest());
        } catch (NoSuchAlgorithmException e2) {
            e2.printStackTrace();
            return "";
        }
    }

    com.xingin.utils.core.am

    private static final char[] f67022c = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};

    public static String a(byte[] bArr) {
        if (bArr == null || bArr.length == 0) {
            return "";
        }
        int length = bArr.length;
        char[] cArr = new char[(length * 2)];
        for (int i = 0; i < length; i++) {
            byte b2 = bArr[i];
            int i2 = i * 2;
            char[] cArr2 = f67022c;
            cArr[i2] = cArr2[(b2 >>> 4) & 15];
            cArr[i2 + 1] = cArr2[b2 & 15];
        }
        return new String(cArr);
    }


*/

Java.perform(function(){
    console.log('Hook Start ！');


    var alioth = Java.use('com.xingin.alioth.d.b');

    alioth.b.implementation = function(){
        var result = this.b();
        console.log("alioth.b result : ", result);
        return result;
    };

    // var core = Java.use('com.xingin.utils.core.v');

    // core.b.implementation = function(arg1){
    //     console.log("core.b arg1 : ", arg1);
    //     var result = this.b(arg1);
    //     console.log("core.b result : ", result);
    //     return result;
    // };


})


