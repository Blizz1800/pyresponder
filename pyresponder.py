import json
import socket
from types import FunctionType

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#messages = [{"message": "Message 1"}]
messages = []

#   Create a trigguer in db trigguers
def addTrigguer(trigguer: str, func, *args):
    '''Explain how to add trigguer:
            `trigguer` is an string (str) that will be called by a message.
            `func` is the function that will be called when the trigguer has been founded.
            `args` (optional) is the arguments that will be passed to func

            your function corpse will be ```func(info, [argoument1, argument2, argument3, ..., argumentN])```

            `info` is a required argument object that contains information about the message recived from the user.
            '''
    if trigguer is None or func is None:
        raise Exception('`trigguer` and `func` must be specified...')
    if (not trigguer.startswith("/") and trigguer != "*"):
        trigguer = "/" + trigguer
    trigguers.append({"key": trigguer, "action": func, "args": args})
    print(f"Trigger [{trigguer}] added!!")


class info:
    APP: str
    HEAD: str
    USER: str
    MESSAGE: str
    isGroup: bool
    groupParticipant: str
    headers: list[list[2]]


def reciveInfo(client: socket.socket):

    while True:
        try:
            DATA = client.recv(1024*8).decode('utf8')
            #print(type(DATA), DATA)
            obj = ""
            head = ""
            headers = []
            for i in DATA.splitlines():
                if i.startswith('{'):
                    obj = i
                    break
                elif i.startswith("POST "):
                    i = i.split(' ')
                    head = i[1]
                elif i == "\n" or i=="":
                    continue
                else:
                    i = i.split(': ')
                    headers.append([i[0], i[1]])
            obj = json.loads(obj)  # Carga el objeto JSON
            inf = info()
            inf.HEAD = head
            inf.APP = obj["messengerPackageName"]
            inf.USER = obj["query"]["sender"]
            inf.MESSAGE = obj["query"]["message"]
            inf.isGroup = obj["query"]["isGroup"]
            inf.groupParticipant = obj["query"]["groupParticipant"]
            inf.HEADERS = headers
            trigguered = False
            for i in trigguers:
                # Eschucha los comandos del cliente y ajusta los messages de respuesta en base a ellos...
                if i["key"] == "*":
                    continue
                if obj["query"]["message"].split(' ')[0] == i["key"]:
                    trigguered = True
                    if i["args"] != ():
                        i["action"](inf, *i["args"])
                    else:
                        i["action"](inf)
                    break
                if not trigguered:
                    for t in trigguers:
                        if t["key"] == "*":
                            if i["args"] != ():
                                t["action"](inf, *i["args"])
                            else:
                                t["action"](inf)
                            break
            responseBase = {"replies": messages}
            data = str(responseBase)
            # print(data)
            client.send(
                f"HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json; charset=UTF-8\r\nAccess-Control-Allow-Methods: POST\r\nAccess-Control-Max-Age: 3600\r\nAccess-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With\r\n\n{data}".encode('utf8'))
            client.close()
            break
        except ConnectionResetError:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            break
        except KeyboardInterrupt:
            server.close()
            print("server is shutting down...")
            break
    messages.clear()


def server_start(startAt=("0.0.0.0", 8000)):
    '''The server starts in the `main thread`, if you want to start it in the `background`, you should create a new thread and associate it with these function.'''
    if len(trigguers) > 0:
        server.bind(startAt)
        server.listen()
        while True:
            try:
                client, address = server.accept()
                reciveInfo(client)
            except KeyboardInterrupt:
                break
    else:
        print(
            "need some trigguers\n\nadd them with addTrigguer('trigguer', function, fArgs)")


trigguers: list[dict[str, str | FunctionType, None | tuple]] = [
]


def addResponse(response: str):
    messages.append({"message": response})


def defaultStart(info: info, *argsstr = *["Bienvenido {0}, esto es un mensaje de respuesta automatico!!\n\nLa API funciona con autoresponder, puede encontrar la libreria en https://github.com/blizz1800/pyresponder"]):
    for i in args:
        txt = i.format(f"**{info.USER}**")
        messages.append({"message": txt})

def allResp(inf):
    addResponse("Has dicho: \n\"{0}\"".format(inf.MESSAGE))

if __name__ == '__main__':
    global gAddress
    gAddress = ("0.0.0.0", 8000)
    addTrigguer("start", defaultStart)
    addTrigguer("*", allResp)
    server_start(gAddress)
