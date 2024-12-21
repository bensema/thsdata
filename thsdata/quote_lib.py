import ctypes


class QuoteLib:
    def __init__(self, lib_path, config):
        self.lib = ctypes.CDLL(lib_path)
        self._define_functions()
        self.lib.NewQuote(config.encode('utf-8'))

    def _define_functions(self):
        self.lib.NewQuote.argtypes = [ctypes.c_char_p]
        self.lib.NewQuote.restype = None

        self.lib.Connect.restype = ctypes.c_int

        self.lib.DisConnect.restype = ctypes.c_int

        self.lib.Write.argtypes = [ctypes.c_char_p]
        self.lib.Write.restype = ctypes.c_int

        self.lib.Read.restype = ctypes.c_char_p

        self.lib.QueryData.argtypes = [ctypes.c_char_p]
        self.lib.QueryData.restype = ctypes.c_char_p

    def new_quote(self, config):
        self.lib.NewQuote(config.encode('utf-8'))

    def connect(self):
        return self.lib.Connect()

    def disconnect(self):
        return self.lib.DisConnect()

    def write(self, req):
        return self.lib.Write(req.encode('utf-8'))

    def read(self):
        return self.lib.Read()

    def query_data(self, req):
        return self.lib.QueryData(req.encode('utf-8'))
