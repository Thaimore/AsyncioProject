import asyncio


class ClientServerProtocol(asyncio.Protocol):
    response = []
    security = {}

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        resp = process_data(data.decode('utf8'))
        self.transport.write(resp.encode())


def process_data(some_data):
    some_data = some_data.split()
    correct = 'ok\n'
    if 'put' in some_data or 'get' in some_data:
        if 'put' in some_data:
            if len(some_data) != 4 or some_data[0] != 'put':
                return 'error\nwrong command\n\n'
            try:
                some_data[2] = float(some_data[2])
                some_data[3] = int(some_data[3])
            except:
                return 'error\nwrong command\n\n'
            if some_data[1] not in ClientServerProtocol.security:
                ClientServerProtocol.security.update({some_data[1]: []})
            if some_data[3] not in ClientServerProtocol.security[some_data[1]]:
                ClientServerProtocol.response += some_data[1], some_data[2], some_data[3]
                ClientServerProtocol.security[some_data[1]] += [some_data[3]]
            else:
                for i in range(len(ClientServerProtocol.response)):
                    if ClientServerProtocol.response[i] == some_data[3] and ClientServerProtocol.response[i-2] == some_data[1]:
                        ClientServerProtocol.response[i-1] = some_data[2]
            return 'ok\n\n'

        if 'get' in some_data:
            if len(some_data) != 2 or some_data[0] != 'get':
                return 'error\nwrong command\n\n'
            if some_data[1] == '*':
                for i in ClientServerProtocol.response:
                    if len(str(i)) == 10:
                        correct = correct + str(i) + str('\n')
                    else:
                        correct = correct + str(i) + ' '
                return correct + '\n'
            else:
                if some_data[1] in ClientServerProtocol.response:
                    for i in range(len(ClientServerProtocol.response)):
                        if ClientServerProtocol.response[i] == some_data[1]:
                            correct = correct + str(some_data[1]) + ' '
                            correct = correct + str(ClientServerProtocol.response[i+1]) + ' '
                            correct = correct + str(ClientServerProtocol.response[i+2]) + str('\n')
                    return correct + '\n'
                else:
                    return correct + '\n'
    else:
        return 'error\nwrong command\n\n'


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )

    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
