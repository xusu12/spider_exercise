function showStacks(){
    var stack = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new());
    // var stack = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Throwable").$new());
    console.log(stack);
}

var bytesToString = function (arr) {  
    var str = '';
    arr = new Uint8Array(arr);
    for(var i in arr){
        str += String.fromCharCode(arr[i]);
    }
    return str;
}

function java_hook01(){
    Java.perform(function(){
    
        var retrofit2_mime_b = Java.use('com.bytedance.retrofit2.mime.b');
        retrofit2_mime_b.a.overload('java.lang.String', 'boolean', 'java.lang.String', 'boolean').implementation = function(ars1, ars2, ars3, ars4){
            showStacks();
            console.log('retrofit2_mime_b.a ars1 : ', ars1);
            console.log('retrofit2_mime_b.a ars2 : ', ars2);
            console.log('retrofit2_mime_b.a ars3 : ', ars3);
            console.log('retrofit2_mime_b.a ars4 : ', ars4);
            var result = this.a(ars1, ars2, ars3, ars4);
            console.log('retrofit2_mime_b.a result : ', result);
            return result
        }


        // var retrofit2_mime_b = Java.use('com.bytedance.retrofit2.mime.b');
        // retrofit2_mime_b.md5Stub.implementation = function(){
        //     var result = this.md5Stub();
        //     console.log('retrofit2_mime_b.md5Stub result : ', result);
        //     return result
        // }


        // var retrofit2_mime_a = Java.use('com.bytedance.retrofit2.mime.a');
        // retrofit2_mime_a.a.overload('[B').implementation = function(ars1){
            
        //     console.log('retrofit2_mime_a.a ars1 : ', bytesToString(ars1));
        //     var result = this.a(ars1);
        //     console.log('retrofit2_mime_a.a result : ', result);
        //     return result

        // }

        console.log('Success！');
    
    });
    
}


// function java_hook02(){
//     Java.perform(function(){

//         // 分析 a2  String b2 = tt.d(str);

//         // var tt = Java.use('com.ss.sys.ces.gg.tt');

//         // tt.a.implementation = function(ars1, ars2){
            
//         //     console.log('tt.d ars1 : ', ars1);
//         //     console.log('tt.d ars2 : ', ars2);
//         //     var result = this.a(ars1, ars2);
//         //     console.log('tt.d result : ', result);
//         //     return result
//         // }

//         // tt.d.overload('java.lang.String').implementation = function(ars1){
            
//         //     console.log('tt.d ars1 : ', ars1);
//         //     var result = this.d(ars1);
//         //     console.log('tt.d result : ', result);
//         //     return result
//         // }

//         // var b_a = Java.use('com.ss.a.b.a');
//         // b_a.a.overload('[B').implementation = function(ars1){
            
//         //     console.log('b_a.a ars1 : ', ars1);
//         //     var result = this.a(ars1);
//         //     console.log('b_a.a result : ', result);
//         //     return result
//         // }

//         // 分析 a2  b.a(b2)

//         // var b_b = Java.use('com.ss.a.b.b');
//         // b_b.a.overload('java.lang.String').implementation = function(ars1){
            
//         //     console.log('b_b.a ars1 : ', ars1);
//         //     var result = this.a(ars1);
//         //     console.log('b_b.a result : ', result);
//         //     return result
//         // }

//         // // 22850d0fb2bd29c9e6b334565140394c 9EE1EC96C81888414B276C55E98A743E 5bed170ffe25ef692562b98540db8ba3 9a4dff2c540b903dacccdc1ac46f86e0
//         // var b_a = Java.use('com.ss.a.b.a');
//         // b_a.a.overload('java.lang.String').implementation = function(ars1){
            
//         //     console.log('b_a.a ars1 : ', ars1);
//         //     var result = this.a(ars1);
//         //     console.log('b_a.a result : ', result);
//         //     return result
//         // }

//         // var ces_a = Java.use('com.ss.sys.ces.a');
//         // ces_a.leviathan.implementation = function(ars1, ars2, ars3){
            
//         //     console.log('ces_a.a ars1 : ', ars1);
//         //     console.log('ces_a.a ars2 : ', ars2);
//         //     console.log('ces_a.a ars3 : ', ars3);
//         //     var result = this.leviathan(ars1, ars2, ars3);
//         //     console.log('ces_a.a result : ', result);
//         //     return result
//         // }

//         // var h_c = Java.use('com.bytedance.h.c');
//         // h_c.a.implementation = function(ars1){
            
//         //     console.log('ces_a.a ars1 : ', ars1);

//         //     this.a(ars1);
//         //     // console.log('ces_a.a result : ', result);
//         //     // return result
//         // }

//         console.log('Success！');
    
//     });
    
// }



// function call_java(){
//     Java.perform(function(){

//     //     var b_a = Java.use('com.ss.a.b.a');
//     //     var ces_a = Java.use('com.ss.sys.ces.a');
//     //     var str = "0a88e56c98d55e71a494966e45122f59E90BD85E80E226FBC144629181D2C8FB5bed170ffe25ef692562b98540db8ba39a4dff2c540b903dacccdc1ac46f86e0";
//     //     var X_Gorgon = b_a.a(ces_a.leviathan(-1, 1603536782, b_a.a(str)));
//     //     console.log('X_Gorgon : ', X_Gorgon);
    
//     //     console.log('Success！');
    
//     // });

// }



// 抖音风控
// function java_hook02(){
//     Java.perform(function(){

//         var deviceregister = Java.use('com.ss.android.deviceregister.b.c$a');
//         deviceregister.a.overload('java.lang.String').implementation = function(ars1){
            
//             console.log('ttEncrypt ars1 : ', ars1);
//             // console.log('ttEncrypt ars1 bytesToString : ', bytesToString(ars1));
//             // console.log('ttEncrypt ars2 : ', ars2);

//             var result = this.a(ars1);
//             // console.log('ttEncrypt result bytesToString : ', bytesToString(result));
//             console.log('ttEncrypt result : ', result);
//             return result
//         }
//         // var currentApplication = Java.use('android.app.ActivityThread').currentApplication();
//         // var context = currentApplication.getApplicationContext();

//         var NetUtil = Java.use('com.ss.android.common.applog.NetUtil');
//         NetUtil.sendEncryptLog.overload('java.lang.String', '[B', 'android.content.Context', 'boolean').implementation = function(ars1, ars2, ars3, ars4){
            
//             console.log('sendEncryptLog ars1 : ', ars1);
            
//             console.log('sendEncryptLog ars2 : ', ars2);
//             console.log('sendEncryptLog ars2 bytesToString : ', bytesToString(ars2));
//             console.log('sendEncryptLog ars3 : ', ars3);
//             console.log('sendEncryptLog ars4 : ', ars4);

//             var result = this.sendEncryptLog(ars1, ars2, ars3, ars4);
//             // console.log('ttEncrypt result bytesToString : ', bytesToString(result));
//             console.log('sendEncryptLog result : ', result);
//             return result
//         }

//         var NetworkClient = Java.use('com.bytedance.common.utility.NetworkClient');
//         NetworkClient.post.overload('java.lang.String', '[B', 'boolean', 'java.lang.String', 'boolean').implementation = function(ars1, ars2, ars3, ars4, ars5){
            
//             console.log('post ars1 : ', ars1);
            
//             console.log('post ars2 : ', ars2);
//             console.log('post ars2 bytesToString : ', bytesToString(ars2));
//             console.log('post ars3 : ', ars3);
//             console.log('post ars4 : ', ars4);
//             console.log('post ars5 : ', ars5);

//             var result = this.post(ars1, ars2, ars3, ars4, ars5);
//             // console.log('ttEncrypt result bytesToString : ', bytesToString(result));
//             console.log('post result : ', result);
//             return result
//         }


//         var EncryptorUtil = Java.use('com.bytedance.frameworks.encryptor.EncryptorUtil');
//         EncryptorUtil.ttEncrypt.implementation = function(ars1, ars2){
            
//             // console.log('ttEncrypt ars1 : ', ars1);
//             // console.log('ttEncrypt ars1 bytesToString : ', bytesToString(ars1));
//             // console.log('ttEncrypt ars2 : ', ars2);

//             var result = this.ttEncrypt(ars1, ars2);
//             console.log('ttEncrypt result bytesToString : ', bytesToString(result));
//             console.log('ttEncrypt result : ', result);
//             return result
//         }

//         console.log('Success！');
    
//     });
    
// }



// java_hook02();
// Java.perform(function(){
//     var PatchProxy = Java.use('com.meituan.robust.PatchProxy');
//     var PatchProxyResult = Java.use('com.meituan.robust.PatchProxyResult');
    
//     PatchProxy.proxy.implementation = function(ars1, ars2, ars3, ars4, ars5){
//         var PatchProxyResult1 = PatchProxyResult.$new();
//         PatchProxyResult1.isSupported.value = false;
//         PatchProxyResult1.result.value = '';
//         // var result = this.proxy(ars1, ars2, ars3, ars4, ars5);

//         console.log('PatchProxyResult1.isSupported : ', PatchProxyResult1.isSupported);
//         return PatchProxyResult1;
//     }

//     console.log('Success！');

// });

// java_hook02();







