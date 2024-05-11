import json, socket, time, os, traceback, re
try:
    from core.base import typeServer, loggings, LoginError, loggings, config, typeServer
    from core.probihited_word import Probihited_words
except ModuleNotFoundError:
    from SuperLinkBase.base import typeServer, loggings, LoginError, loggings, config, typeServer
    from SuperLinkBase.probihited_word import Probihited_words
msgConsole = loggings.msgConsole

channelClients: dict[str, dict[socket.AddressFamily, typeServer]] = {}
serverList: dict[socket.AddressFamily, list] = {}
__version__ = 3

class SuperLink:
    def multiJSONHandle(__json: str):
        if "} {" in __json:
            return __json[:__json.find("} {")+1]
        if "}{" in __json:
            return __json[:__json.find("}{")+1]
        return __json

    def sendJSONOut(__dict, urAddr, urChannel = "默认大区"):
        dataAsJson = json.dumps(__dict)
        SuperLink.sendout(bytes(dataAsJson, "utf-8"), urAddr, urChannel)

    def sendJSON(conn: socket.socket, __dict: dict):
        conn.send(bytes(json.dumps(__dict, ensure_ascii=False), 'utf-8'))

    def sendout(data: bytes, Addr, urChannel = "默认大区"):
        socketAddrs = list(channelClients[urChannel].keys())
        for socketAddr in socketAddrs:
            if socketAddr != Addr:
                try:
                    channelClients[urChannel][socketAddr].sock.send(data)
                except BaseException as err:
                    msgConsole(f'[#FF7777]转发 {channelClients[urChannel][socketAddr].serverName} IP={socketAddr[0]} 时遇到问题：{err}')
                    if "主机" in str(err):
                        channelClients[urChannel][socketAddr].sock.close()
                        SuperLink.ToChannel(channelClients[urChannel][socketAddr], "remove")

    def broadcast(__data: dict):
        for __channel in channelClients:
            for socketAddr in channelClients[__channel]:
                try:
                    channelClients[__channel][socketAddr].sock.send(bytes(json.dumps(__data), "utf-8"))
                except:
                    pass

    def getToken(addr: str):
        if os.path.isfile(f"SuperLink/account/{addr}.token"):
            f = open(f"SuperLink/account/{addr}.token", "r", encoding='utf-8')
            _getToken = f.read()
            f.close()
            del f
            return _getToken
        else:
            return None

    def ToChannel(server: typeServer, mode = "add"):
        global channelClients, serverList
        if mode == "add":
            try:
                channelClients[server.channel][server.addr] = server
            except:
                channelClients[server.channel] = {}
                channelClients[server.channel][server.addr] = server
            try:
                serverList[server.channel].append(server)
            except:
                serverList[server.channel] = [server]

        elif mode == "remove":
            try:
                channelClients[server.channel][server.addr].sock.close()
                del channelClients[server.channel][server.addr]
            except: pass
            if not channelClients[server.channel] and server.channel != "默认大区":
                del channelClients[server.channel]
            try: serverList[server.channel].remove(server)
            except: pass
            if not serverList[server.channel] and server.channel != "默认大区":
                del serverList[server.channel]

    def sumServers():
        totalClients = 0
        for channel in channelClients:
            totalClients += len(channelClients[channel])
        return totalClients

    def login(conn: socket.socket, addr: socket.AddressFamily):
        try:
            conn.send(bytes(
                json.dumps({"needToken": config.isUseToken, "version": __version__}, ensure_ascii=False),
                "utf-8"
            ))
            _recv = SuperLink.multiJSONHandle(conn.recv(1024).decode("utf-8"))
            _recvJSON = json.loads(_recv)
        except json.JSONDecodeError:
            raise LoginError("SendData ERROR")
        except:
            raise LoginError("closed recv")
        try:
            if _recvJSON['KeyCode'] != "RentalServerLink made by 2401 & SuperScript":
                SuperLink.sendJSON(conn, {"data_type": "consolemsg", "msgColor": "§cTerminal -> Copyright ERROR", "msgInfo": "§c 错误 "})
                raise LoginError("Copyright ERROR")
            if config.isUseToken:
                _getTokenFromNumber = SuperLink.getToken(addr[0])
                if _getTokenFromNumber == None:
                    SuperLink.sendJSON(conn, {"data_type": "consolemsg", "msgColor": "§cTerminal -> 您还没有获得该服务端的Token", "msgInfo": "§c 错误 "})
                    msgConsole("[#FF7777]中止连接, 因为没有 Token")
                    time.sleep(0.5)
                    raise LoginError("Not Token")
                elif _recvJSON["token"] != _getTokenFromNumber:
                    SuperLink.sendJSON(conn, {"data_type": "consolemsg", "msgColor": "§cTerminal -> Token错误", "msgInfo": "§c 错误 "})
                    msgConsole("[#FF7777]中止连接, 因为 Token 错误")
                    raise LoginError("Invalid Token")
            if len(_recvJSON["serverName"]) > 10:
                SuperLink.sendJSON(conn, {"data_type": "consolemsg", "msgColor": "§cTerminal -> 过长的服务器名字", "msgInfo": "§c 错误 "})
                raise LoginError("Too long a server name")
            if _recvJSON["robotType"] == "flash_chatroom":
                msgConsole("[#FFFF00]此客户端为外部flash聊天室客户端")
            if _recvJSON["robotType"] not in ["Origin_Omega", "DotCS", "dotcs"]:
                raise LoginError("Invalid ConnectType")
            return typeServer(conn, _recvJSON["serverName"], addr, _recvJSON["channel"], _recvJSON["robotType"])
        except:
            print(_recvJSON)
            raise LoginError("Lack of argument in login-data")

    def checkMsg(__msg: dict):
        if __msg["data_type"] not in typeServer.ALLOW_TYPES:
            raise ValueError(__msg)

    def strServerList(urChannel):
        retStr = "§a当前在线租赁服如下: \n"
        for server in channelClients[urChannel]:
            retStr += f" {channelClients[urChannel][server].serverName}\n"
        return retStr

    def kickClient(server: typeServer):
        SuperLink.sendJSON(server.sock, {"data_type": "msg", "data": "§c你已被踢出互通服务端", "serverName": config.terminalName + "§f>>"})
        SuperLink.ToChannel(server, "remove")

    welcomeFmt = lambda server, msg : msg.replace("[服务器名]", server.serverName).replace("[当前频道名称]", server.channel).replace("[在线服务器数]", str(SuperLink.sumServers()))\
        .replace("[总频道数]", str(len(channelClients))).replace("[终端名称]", config.terminalName)

    def writeScbData(ch_name: str, serverName: str, scbName: str, itemName: str, score: int, mode = "add", noNegative = False):
        if not os.path.isfile(f"SuperLink/scbs/{ch_name}.json"):
            with open(f"SuperLink/scbs/{ch_name}.json", "w", encoding = 'utf-8') as jso:
                json.dump({}, jso)
        with open(f"SuperLink/scbs/{ch_name}.json", "r", encoding = 'utf-8') as jso:
            oldScbsData: dict = json.load(jso)
        if mode == "add":
            try:
                oldScbsData[scbName][itemName] += score
                moneyLeft = oldScbsData[scbName][itemName]
                if noNegative and oldScbsData[scbName][itemName] < 0:
                    return {"status": "failed.negative", "success": False, "left": moneyLeft}
            except KeyError:
                if oldScbsData.get(scbName, None) is None:
                    oldScbsData[scbName] = {}
                    mode = "set"
                    # return {"status": "failed.no_such_scoreboard", "success": False}
                else:
                    mode = "set"
        if mode == "set":
            oldScbsData[scbName][itemName] = score
            moneyLeft = score
        with open(f"SuperLink/scbs/{ch_name}.json", "w", encoding = 'utf-8') as jso:
            json.dump(oldScbsData, jso, indent=4, ensure_ascii=False)
        msgConsole(f"[#0000FF]{serverName}: 频道 {ch_name} 计分板分数改动: 计分板={scbName}, 变更={score}, 新分数=[{itemName}:{oldScbsData[scbName][itemName]}]")
        return {"status": "success", "success": True, "left": moneyLeft}

    def getScbData(ch_name: str, itemName: str) -> int:
        with open(f"SuperLink/scbs/{ch_name}.json", "r", encoding = 'utf-8') as jso:
            try:
                return json.load(jso)[itemName]
            except (FileNotFoundError, KeyError):
                return None

    def connectOK(server: socket.socket, conn: socket.socket, addr):
        global channelClients, serverList
        try:
            serverData = SuperLink.login(conn, addr)
            msgConsole(f"[#00FFFF]IP: {serverData.addr[0]}:{serverData.addr[1]} [#00FF00]{serverData.serverName} [#00FF00]已登录")
            SuperLink.ToChannel(serverData)
            SuperLink.sendJSONOut({"data_type": "connected", "serverName": serverData.serverName}, addr, serverData.channel)
            SuperLink.sendJSON(conn, {"data_type": "msg", "data": SuperLink.welcomeFmt(serverData, config.loginOKMsg), "serverName": f"{config.terminalName}§f>>"})
            try:
                lastMsgTime = 0
                lastMsg = ""
                warning_count = 0
                msg_period = 0
                while 1:
                    getRecvData = conn.recv(3072).decode("utf-8")
                    msg_period += 1
                    msgTime = time.time()
                    if msg_period >= config.warningsClearPrd:
                        if warning_count >= config.maxWarnings:
                            raise Exception(f"该服务器: {serverData.serverName} 被警告次数大于4, 自动断开连接")
                        msg_period = 0
                        warning_count = 0
                    #
                    check_bool = msgTime - lastMsgTime > config.msgSendDelay and not (lastMsg == getRecvData and msgTime - lastMsgTime < config.DuplicMsgSendDelay)
                    if not check_bool:
                        warning_count += 1
                        msgConsole(f"[#00FF00]客户端 [#00FFFF]IP:{addr[0]} < {serverData.serverName} [#FF7700]发送消息太快 或发送重复信息太快!")

                    if len(getRecvData) and check_bool:
                        lastMsg = getRecvData
                        lastMsgTime = msgTime
                        getRecvJSON = json.loads(SuperLink.multiJSONHandle(getRecvData))
                        SuperLink.checkMsg(getRecvJSON)
                        match getRecvJSON["data_type"]:
                            case "exit":
                                raise ConnectionResetError()
                            case typeServer.MSG:
                                _getMsg = Probihited_words.checkProbihited(getRecvJSON["data"])
                                if not config.allowColorMsg:
                                    _getMsg = re.compile("§[1-9a-zA-Z]").sub("", _getMsg)
                                if len(_getMsg) < 50:
                                    SuperLink.sendJSONOut({"data_type": "msg", "data": _getMsg, "serverName": serverData.serverName}, addr, serverData.channel)
                                    msgConsole(f"{serverData.channel} {serverData.serverName} [#CCCCCC]>> [#FFFFFF]{_getMsg}")
                                else:
                                    _getMsg = _getMsg[:50]
                                    msgConsole(f"[#FF7777]{serverData.channel}频道的客户端{serverData.serverName}发送过长消息, 仅转发: {_getMsg}..")
                                    SuperLink.sendJSONOut({"data_type": "msg", "data": _getMsg, "serverName": serverData.serverName}, addr, serverData.channel)
                            case typeServer.CONN:
                                SuperLink.sendJSONOut({"data_type": "connected", "data": server, "serverName": serverData.serverName}, addr, serverData.channel)
                                msgConsole(f"{serverData.channel} > {serverData.serverName} 登入互通")
                            case typeServer.DISCONN:
                                SuperLink.sendJSONOut({"data_type": "disconnected", "data": server, "serverName": serverData.serverName}, addr, serverData.channel)
                                msgConsole(f"{serverData.channel} > {serverData.serverName} 退出互通")
                            case typeServer.PLAYERJOIN:
                                SuperLink.sendJSONOut({"data_type": "player.join", "data": getRecvJSON['data'], "serverName": serverData.serverName}, addr, serverData.channel)
                                msgConsole(f"{serverData.channel} > {serverData.serverName} [#FFFF00]{getRecvJSON['data']} 加入了游戏")
                            case typeServer.PLAYERLEFT:
                                SuperLink.sendJSONOut({"data_type": "player.left", "data": getRecvJSON['data'], "serverName": serverData.serverName}, addr, serverData.channel)
                                msgConsole(f"{serverData.channel} > {serverData.serverName} [#FFFF00]{getRecvJSON['data']} 退出了游戏")
                            case typeServer.CHECK:
                                msgConsole(f"{serverData.channel} <-> {serverData.serverName} is checking {getRecvJSON['data']}")
                                match getRecvJSON["data"]:
                                    case "server_list":
                                        try:
                                            msgConsole(f"{serverData.serverName}")
                                            SuperLink.sendJSON(conn, {"data_type": "msg", "data": SuperLink.strServerList(serverData.channel), "serverName": f"{config.terminalName}§f>§r"})
                                        except Exception as err:
                                            SuperLink.sendJSON(conn, {"data_type": "msg", "data": "§c获取列表出现问题: "+str(err), "serverName": f"{config.terminalName}§f>§r"})

                            case typeServer.UPLOAD_SCB:
                                score = int(getRecvJSON['data'])
                                scbItemName = getRecvJSON['ExtraData2']
                                scbName = getRecvJSON['ExtraData1']
                                noNegative = getRecvJSON['ExtraData3']
                                protocolUID = getRecvJSON["UID"]
                                result = SuperLink.writeScbData(serverData.channel, serverData.serverName, scbName, scbItemName, score, noNegative=noNegative)
                                SuperLink.sendJSON(conn, {"data_type": "upload_scb.result", "data": result, "UID": protocolUID})

                            case typeServer.API_DATA:
                                if len(getRecvJSON['APIData']) != 4:
                                    continue
                                isSendBack = getRecvJSON['APIData']['SendBack']
                                del getRecvJSON['APIData']['SendBack']
                                if isSendBack:
                                    SuperLink.sendJSON(conn, {"data_type": "api.data", "data": getRecvJSON['data'], 'APIData': getRecvJSON['APIData']})
                                else:
                                    SuperLink.sendJSONOut({"data_type": "api.data", "data": getRecvJSON['data'], 'APIData': getRecvJSON['APIData']}, serverData.addr, serverData.channel)
                                msgConsole(f"[#0000FF]{serverData.serverName} >> 向 {serverData.channel} 发送API事件广播: {getRecvJSON['data']} - <{getRecvJSON['APIData']['ExtraData1']}> <{getRecvJSON['APIData']['ExtraData2']}> <{getRecvJSON['APIData']['ExtraData3']}>, 是否仅发回: {isSendBack}")

            except ConnectionResetError:
                SuperLink.sendJSONOut({"data_type": "disconnected", "serverName": serverData.serverName}, addr, serverData.channel)
                try:
                    SuperLink.ToChannel(serverData, "remove")
                except:
                    pass
                msgConsole(f"[#00FF00]客户端 [#00FFFF]IP:{addr[0]} < {serverData.serverName} [#FF9999]中止连接")

            except json.JSONDecodeError:
                SuperLink.sendJSONOut({"data_type": "disconnected", "serverName": serverData.serverName}, addr, serverData.channel)
                msgConsole(f"[#00FF00]客户端 [#00FFFF]IP:{addr[0]} < {serverData.serverName} [#FF9999]发送了无法被识别的数据，断开连接: {repr(SuperLink.multiJSONHandle(getRecvData))}")
                traceback.print_exc()
                SuperLink.ToChannel(serverData, "remove")

            except Exception as err:
                ...
                SuperLink.sendJSONOut({"data_type": "disconnected", "serverName": serverData.serverName}, addr, serverData.channel)
                msgConsole(f"[#00FF00]客户端 [#00FFFF]IP:{addr[0]} < {serverData.serverName} [#FF9999]意外断开连接， 报错如下")
                msgConsole(f"[#FF7777]{traceback.format_exc()}")
                SuperLink.ToChannel(serverData, "remove")
                conn.close()

        except LoginError as err:
            conn.close()
            msgConsole(f"客户端 IP:{addr[0]} 意外断开连接， 原因是发送了不合法数据: {err}")
            try:
                SuperLink.sendJSONOut({"data_type": "disconnected", "serverName": serverData.serverName}, addr, serverData.channel)
            except:
                pass
