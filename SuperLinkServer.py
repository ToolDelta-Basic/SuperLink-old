import socket, threading, json, os, time, datetime, platform
import traceback, re
try:
    from core.probihited_word import Probihited_words
    from core.base import typeServer, loggings, LoginError
    from core.link import SuperLink, config, __version__
except ModuleNotFoundError:
    print("not core")
    time.sleep(3)
    from SuperLinkBase.probihited_word import Probihited_words
    from SuperLinkBase.base import typeServer, loggings, LoginError
    from SuperLinkBase.link import SuperLink, config, __version__
    # cd /www/OMEGA/users/SuperLinkServer;python3.10 SuperLinkServer.py
channelClients: dict[str, dict[socket.AddressFamily, typeServer]] = {} # {频道: {地址: 套接字}}
serverList: dict[socket.AddressFamily, list] = {}                          # {频道: {地址, }}
msgConsole = loggings.msgConsole

if "Windows" in platform.platform():
    platform_ver = 1
else:
    platform_ver = 0
#
         
def consoleCmd():
    while 1:
        try:
            cmd = input()
            if cmd:
                cmd = cmd.split()
            else:
                continue
            if cmd[0] == "help":
                msgConsole("[#FFFF00]查看指令帮助")
                msgConsole("[#FFFF00] exit:   广播一条互通服务端将关闭的消息， 并关闭此服务端")
                msgConsole("[#FFFF00] upd:   广播一条互通服务端将进行更新的消息， 并关闭服务端")
                msgConsole("[#FFFF00] list:   列出所有已连接的服务器与所有频道的列表")
                msgConsole("[#FFFF00] kick IP <ip(不需要填端口)>:   根据输入的IP踢出对应的租赁服")
                msgConsole("[#FFFF00] kick name <服务器名>:   根据输入的服务器名踢除对应的租赁服")
                msgConsole("[#FFFF00] announce <信息>:   广播一条信息")
                continue

            elif cmd[0] == "exit":
                SuperLink.broadcast({"data_type": "msg", "data": "§c互通即将进行关闭/重启", "serverName": f"{config.terminalName}§f>>"})
                time.sleep(0.5)
                os._exit(0)

            elif cmd[0] == "upd":
                SuperLink.broadcast({"data_type": "msg", "data": "§c服服互通将进行常规更新， 请重启", "serverName": f"{config.terminalName}§f>>"})
                time.sleep(0.5)
                os._exit(0)

            elif cmd[0] == "list":
                msgConsole("[#00FFFF]当前已连接并登录的服务器 & 频道列表:")
                if not channelClients:
                    msgConsole("[#FF7700]没有租赁服在线.")
                for s_channel in channelClients:
                    for s_addr in channelClients[s_channel]:
                        server = channelClients[s_channel][s_addr]
                        msgConsole(f" - 频道: {server.channel} 服务器名: {server.serverName}")
                continue

            elif cmd[0] == "kick":
                assert len(cmd) == 3
                kick_mode, kick_tar = cmd[1:4]
                isSuccess = False
                for ch in channelClients:
                    for ip in channelClients[ch]:
                        if (ip[0] == kick_tar and kick_mode.capitalize() == "ip") or (kick_tar in channelClients[ch][ip].serverName and kick_mode.lower() == "name"):
                            msgConsole(f"[#FF7777]客户端租赁服 {channelClients[ch][ip].serverName} 已被踢出.")
                            SuperLink.kickClient(channelClients[ch][ip])
                            isSuccess = True
                            break
                msgConsole(f"[#FF7777]未找到符合条件的客户端租赁服，输入 list 可查看列表") if not isSuccess else None
                continue

            elif cmd[0] == "announce":
                annMsg = cmd[1]
                SuperLink.broadcast({"data_type": "msg", "data": annMsg, "serverName": f"{config.terminalName}§f>>"})
                msgConsole(f"[#007700]转发成功， 已将消息转发到 {SuperLink.sumServers()} 个租赁服")
                continue

            msgConsole("[#FF7777]命令不存在, 输入 help 可查看命令列表")

        except (IndexError, AssertionError) as err:
            msgConsole("[#FF7777]输入格式有误: 缺少参数.")
        except BaseException as err:
            traceback.print_exc()
            msgConsole(f"[#FF0000]ERROR: [#FF7700]执行指令出现问题: {err}")


def log_data():
    while 1:
        if loggings.logs:
            with open(f"SuperLink/logs/{datetime.datetime.now().strftime('%Y-%m-%d')}.log", "a", encoding='utf-8') as log_file:
                log_file.write("\n".join(loggings.logs))
            loggings.logs = [""]
        time.sleep(10)

def get_local_ip():
    l = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    l.connect(("8.8.8.8", 80))
    return l.getsockname()[0]

if not os.path.isdir("SuperLink"):
    os.mkdir("SuperLink")
if not os.path.isdir("SuperLink/account"):
    os.mkdir("SuperLink/account")
if not os.path.isdir("SuperLink/logs"):
    os.mkdir("SuperLink/logs")
if not os.path.isdir("SuperLink/scbs"):
    os.mkdir("SuperLink/scbs")
        
[msgConsole(ico, block=True) for ico in [
    "Dbbbbbbbb",
    "Dbbbbbbbb",
    "DbbWbDbbWbDbb",
    "DbWbRbWbDbRbWbDb",
    "WbbRbWbbRbWbb",
    "Wbbbbbbbb",
    "Wbbb____bbb",
    "WbbbbbRbGbb",
]
]
os.system("title SuperLink-服服互通 - 服务端 [请不要直接关闭该窗口，而是输入upd后回车]") if platform_ver else msgConsole("[#FF7700]如果您要关闭服务端，请输入 upd 并回车")
msgConsole("[#00FFFF]SuperLink - The first chatroom for Netease RentalServers")

config.initcfg()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", config.usePort))
server.listen(64)

msgConsole(f"启动服务端成功, 已开放端口{config.usePort}")
msgConsole(f"运行在本机(局域网)地址： {get_local_ip()}:{config.usePort}")
msgConsole(f"[#FFFF00]输入 help 获取命令帮助")
threading.Thread(target = consoleCmd).start()
threading.Thread(target = log_data).start()
        
while 1:
    conn, addr = server.accept()
    msgConsole(f"[#00FF00]客户端 [#00FFFF]IP:{addr[0]} 连接了服务端, 等待登录")
    threading.Thread(target = SuperLink.connectOK, args = (server, conn, addr)).start()