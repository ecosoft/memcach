"""This module has class Client for working with memcached"""

import socket
import pickle


class Client:
    """
    Client for memcached
    Implemented commands: set, get, delete
    """
    FLAG_BYTES = 0
    FLAG_INT = 1
    FLAG_FLOAT = 2
    FLAG_STR = 3
    FLAG_PICKLE = 4

    BUFFER_SIZE = 4096
    DEFAULT_PORT = 11211
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_TIMEOUT = 3
    DEFAULT_STORAGE_TIME = 600

    TYPE_ERROR = 'Incompatible value type'

    def __init__(self, server=DEFAULT_HOST, port=DEFAULT_PORT,
                 socket_timeout=DEFAULT_TIMEOUT):
        """ Init Client, create connection """
        self.buffer = b''
        self.server = server
        self.port = port
        self.socket_timeout = socket_timeout
        self.socket = socket.create_connection((self.server, self.port),
                                               socket_timeout)

    def _send(self, cmd):
        """ Send cmd to socket """
        if self.socket:
            self.socket.sendall(cmd)

    def _close(self):
        """ Close socket """
        if self.socket:
            self.socket.close()

    def _read_line(self):
        """
        Read a line and return it.
        If the error received, will return ConnectionError
        """
        buf = self.buffer
        index = buf.find(b'\r\n')
        if index == -1:
            if self.socket:
                while True:
                    chunk = self.socket.recv(self.BUFFER_SIZE)
                    if not chunk:
                        self.buffer = b''
                        raise ConnectionError('socket.recv() returned 0 bytes')
                    buf += chunk

                    index = buf.find(b'\r\n')
                    if index >= 0:
                        break
            else:
                raise ConnectionError('Error in socket')

        self.buffer = buf[index + 2:]
        return buf[:index]

    def _read_data(self, size):
        """ Reads data of specified size """
        buf = self.buffer
        while len(buf) < size:
            chunk = self.socket.recv(self.BUFFER_SIZE)
            if not chunk:
                raise ConnectionError('socket.recv() returned 0 bytes')
            buf += chunk
        self.buffer = buf[size:]
        return buf[:size]

    def _pack(self, value):
        if isinstance(value, bytes):
            flag = self.FLAG_BYTES
            data = value
        elif isinstance(value, int):
            flag = self.FLAG_INT
            data = str(value).encode()
        elif isinstance(value, float):
            flag = self.FLAG_FLOAT
            data = str(value).encode()
        elif isinstance(value, str):
            flag = self.FLAG_STR
            data = value.encode()
        else:
            flag = self.FLAG_PICKLE
            data = pickle.dumps(value)
        return flag, data

    def _unpack(self, flag, data):
        if flag == self.FLAG_BYTES:
            value = data
        elif flag == self.FLAG_INT:
            value = int(data.decode())
        elif flag == self.FLAG_FLOAT:
            value = float(data.decode())
        elif flag == self.FLAG_STR:
            value = data.decode()
        elif flag == self.FLAG_PICKLE:
            value = pickle.loads(data)
        else:
            raise TypeError(self.TYPE_ERROR)
        return value

    def set(self, key, value, storage_time=DEFAULT_STORAGE_TIME):
        """
        Set value for key
        Return TRUE if successful
        """
        flag, data = self._pack(value)
        data_size = len(data)
        header = 'set {} {} {} {}\r\n'.format(
            key, flag, storage_time, data_size).encode()
        body = data + b'\r\n'
        cmd = header + body
        self._send(cmd)
        return self._read_line() == b'STORED'

    def get(self, key):
        """ Get value for key """
        cmd = 'get {}\r\n'.format(key).encode()
        self._send(cmd)
        line = self._read_line()
        if line == b'END':
            return None
        answer = line.decode().split()

        flag = int(answer[2])
        data_size = int(answer[3])

        data = self._read_data(data_size)
        self._read_line()  # Empty line (end of data)
        self._read_line()  # END

        return self._unpack(flag, data)

    def delete(self, key):
        """ Delete key """
        cmd = 'delete {}\r\n'.format(key).encode()
        self._send(cmd)
        line = self._read_line()
        return line == b'DELETED'
