# !/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import frida
import os
import warnings

warnings.filterwarnings("ignore")


hook_test = '''
rpc.exports = {
    getsig: function(){
        var search_id = "" 
        Java.perform(
            function(){
                send('Hook Start douyin ...')
                var alioth = Java.use('com.xingin.alioth.d.b');
                var result = alioth.b();
                search_id = result;
                console.log("alioth.b search_id : ", search_id);
            }
        )
        return search_id;
    }
}

'''


# os.system("adb forward tcp:27042 tcp:27042")
# os.system("adb forward tcp:27043 tcp:27043")


def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)


def stub_hook_prepare():
    process = frida.get_remote_device().attach('com.xingin.xhs')
    script = process.create_script(hook_test)
    script.on('message', on_message)
    script.load()
    return script.exports

if __name__ == '__main__':
    script = stub_hook_prepare()
    print(script.getsig())
