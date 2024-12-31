import ctypes
import os
import platform
import json


class QuoteLib:
    def __init__(self, ops: dict = ()):
        if 'lib_path' in ops and ops['lib_path'] != "":
            self.__lib_path = ops.pop('lib_path')
        else:
            self.__lib_path = self._get_lib_path()

        self.lib = ctypes.CDLL(self.__lib_path)
        self._define_functions()
        self.lib.NewQuote(json.dumps(ops).encode('utf-8'))

    def _get_lib_path(self):
        system = platform.system()
        if system == 'Linux':
            lib_path = os.path.join(os.path.dirname(__file__), 'libquote.so')
        elif system == 'Darwin':
            lib_path = os.path.join(os.path.dirname(__file__), 'libquote.dylib')

        # todo windows找时间再生成dll
        # elif system == 'Windows':
        #     lib_path = os.path.join(os.path.dirname(__file__), 'libquote.dll')
        else:
            raise OSError('Unsupported operating system')
        return lib_path

    def _define_functions(self):
        self.lib.NewQuote.argtypes = [ctypes.c_char_p]
        self.lib.NewQuote.restype = None

        self.lib.Connect.restype = ctypes.c_char_p

        self.lib.DisConnect.restype = ctypes.c_int

        self.lib.Write.argtypes = [ctypes.c_char_p]
        self.lib.Write.restype = ctypes.c_char_p

        self.lib.Read.restype = ctypes.c_char_p

        self.lib.QueryData.argtypes = [ctypes.c_char_p]
        self.lib.QueryData.restype = ctypes.c_char_p

    # def new_quote(self, config: str = ""):
    #     self.lib.NewQuote(config.encode('utf-8'))

    def connect(self):
        return self.lib.Connect()

    def disconnect(self):
        return self.lib.DisConnect()

    def write(self, req: str = ""):
        return self.lib.Write(req.encode('utf-8'))

    def read(self):
        return self.lib.Read()

    def query_data(self, req: str = ""):
        return self.lib.QueryData(req.encode('utf-8'))
