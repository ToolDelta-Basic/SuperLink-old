import datetime
import socket, re
import os, json
from rich.console import Console as _console
console = _console()

class LoginError(Exception):...

class _client_server:
    MSG = "msg"
    CONN = "connected"
    DISCONN = "disconnected"
    PLAYERJOIN = "player.join"
    PLAYERLEFT = "player.left"
    EXIT = "exit"
    CHECK = "check"
    API_DATA = "api.data"
    # This will not achieve for a long time :( now can
    UPLOAD_SCB = "upload.scb"
    ALLOW_TYPES = [MSG, CONN, DISCONN, PLAYERJOIN, PLAYERLEFT, EXIT, CHECK, UPLOAD_SCB, API_DATA]

    def __init__(self, __sock: socket.socket, name: str, addr: socket.AddressFamily, channel: str = "默认大区", robotMode: str = "Omega"):
        self.sock = __sock
        self.addr = addr
        self.serverName = name
        self.channel = channel
        self.robotmode = robotMode

class _loggings:
    logs = [""]
    def msgConsole(this, msg: str, block: bool = False):
        this.logs.append(datetime.datetime.now().strftime("[%H:%M:%S]") +  " " + str(msg))
        dt = datetime.datetime.now().strftime("[[#00FF00]%H [#FFFFFF]: [#00FF00]%M[#FFFFFF]]")
        msg = str(msg).replace("§1", "[#000077]").replace("§1", "[#000077]").replace("§2", "[#007700]").replace("§3", "[#007777]").replace("§4", "[#FF0000]")\
            .replace("§5", "[#770077]").replace("§6", "[#FF7700]").replace("§7", "[#777777]").replace("§8", "[#777777]").replace("§9", "[#000077]")\
            .replace("§a", "[#00FF00]").replace("§b", "[#00FFFF]").replace("§c", "[#FF7777]").replace("§d", "[#FF00FF]").replace("§e", "[#FFFF00]")\
            .replace("§f", "[#FFFFFF]").replace("§g", "[#FFFF00]").replace("§l", "[#FFFFFF]").replace("§r", "[#FFFFFF]") if not block else \
        msg.replace("R", "[#000000 on #00FFFF]").replace("W", "[#000000 on white]").replace("b", "  ").replace("D", "[#000000 on #0000FF]").replace("G", "[#000000 on #777777]")
        console.print(f"{dt} {msg}")

class _config:
    # class ConfigError(BaseException):...
    # class ArgumentError(ConfigError):...
    default_config = {
        "使用端口": 24013,
        "是否开启token登录(False则为不需要登录)": False,
        "转发服务器进入互通提示": True,
        "转发玩家进出提示": True,
        "允许信息内彩字": True,
        "警告次数上限": 10,
        "警告清空周期(每发x条信息就清空一次警告)": 20,
        "重复信息发送间隔检测秒数(小于此时长将进行一次警告)": 3,
        "两条信息间隔最小时长秒数(小于此时长将进行一次警告)": 1,
        "终端显示名称": "§b蔚蓝科技",
        "登录成功时欢迎语": f"§7您已成功连接到 §f「[当前频道名称]」§7频道\n[终端名称]§f>> §7当前有§f[总频道数]§7个频道， 共§f[在线服务器数]§7个服务器在线"
    }

    def initcfg(self):
        if not os.path.isfile("SuperLink/config.json"):
            json.dump(self.default_config, open("SuperLink/config.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)
            self.useConfig = self.default_config
            self.update()
            loggings.msgConsole("[#FF7700]还没有生成配置文件， 已自动生成(SuperLink/config.json)")
        else:
            try:
                self.useConfig = json.load(open("SuperLink/config.json", "r", encoding='utf-8'))
                self.update()
                loggings.msgConsole("[#00FF00]配置文件读取完成")
            except json.JSONDecodeError:
                loggings.msgConsole("[#FF7777]配置文件似乎被您改错了..你需要修改配置文件并重启")
                loggings.msgConsole("[#FF7777]您也可以直接删掉现有配置文件以解决问题")
                loggings.msgConsole("[#FF7777]回车键以退出")
                input()
                os._exit(0)
            except KeyError:
                loggings.msgConsole("[#FF7777]配置文件缺少项， 有可能是服务端版本更新导致的")
                loggings.msgConsole("[#FF7777]你需要删除配置文件并重启服务端以等待其自动生成")
                loggings.msgConsole("[#FF7777]回车键以退出")
                input()
                os._exit(0)

    def update(self):
        self.usePort = self.useConfig["使用端口"]
        self.isUseToken = self.useConfig["是否开启token登录(False则为不需要登录)"]
        self.isSendoutConn = self.useConfig["转发服务器进入互通提示"]
        self.isSendoutPlayerConn = self.useConfig["转发玩家进出提示"]
        self.allowColorMsg = self.useConfig["允许信息内彩字"]
        self.maxWarnings = self.useConfig["警告次数上限"]
        self.warningsClearPrd = self.useConfig["警告次数上限"]
        self.DuplicMsgSendDelay = self.useConfig["重复信息发送间隔检测秒数(小于此时长将进行一次警告)"]
        self.msgSendDelay = self.useConfig["两条信息间隔最小时长秒数(小于此时长将进行一次警告)"]
        self.terminalName = self.useConfig["终端显示名称"]
        self.loginOKMsg = self.useConfig["登录成功时欢迎语"]

typeServer = _client_server
loggings = _loggings()
config = _config()