# !/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import frida
import os
import warnings

warnings.filterwarnings("ignore")

hook_code = '''
rpc.exports = {
    getsig: function(currentTimeMillis, str_res){
        var gorgon = "" 
        Java.perform(
            function(){
                send('Hook Start douyin ...')

                var b_a = Java.use('com.ss.a.b.a');
                var ces_a = Java.use('com.ss.sys.ces.a');
                // var str = "0a88e56c98d55e71a494966e45122f59E90BD85E80E226FBC144629181D2C8FB5bed170ffe25ef692562b98540db8ba39a4dff2c540b903dacccdc1ac46f86e0";
                var X_Gorgon = b_a.a(ces_a.leviathan(-1, currentTimeMillis, b_a.a(str_res)));
                gorgon = X_Gorgon;
            }
        )
        return gorgon;
    }
}

'''


os.system("adb forward tcp:27042 tcp:27042")
# os.system("adb forward tcp:27043 tcp:27043")

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)


def gorgon_hook_prepare():

    # host = '127.0.0.1:27042'
    # process_name = "com.ss.android.ugc.aweme"
    # manager = frida.get_device_manager()
    # remote_device = manager.add_remote_device(host)
    # process = remote_device.attach(process_name)

    process = frida.get_remote_device().attach('com.ss.android.ugc.aweme')
    script = process.create_script(hook_code)
    script.on('message', on_message)
    script.load()
    return script.exports


if __name__ == '__main__':
    ghp = gorgon_hook_prepare()
    gorgon = ghp.getsig(1603536770, "0a88e56c98d55e71a494966e45122f59E90BD85E80E226FBC144629181D2C8FB5bed170ffe25ef692562b98540db8ba39a4dff2c540b903dacccdc1ac46f86e0")
    print("gorgon : ", gorgon)