
import ctypes

class QuoteLib:
    def __init__(self, lib_path):
        self.lib = ctypes.CDLL(lib_path)
        self._define_functions()

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

        self.lib.ReadHQFile.restype = ctypes.c_char_p

        self.lib.QueryHQFileData.argtypes = [ctypes.c_char_p]
        self.lib.QueryHQFileData.restype = ctypes.c_char_p

    def new_quote(self, config):
        self.lib.NewQuote(config)

    def connect(self):
        return self.lib.Connect()

    def disconnect(self):
        return self.lib.DisConnect()

    def write(self, req):
        return self.lib.Write(req)

    def read(self):
        return self.lib.Read()

    def query_data(self, req):
        return self.lib.QueryData(req)

    def read_hq_file(self):
        return self.lib.ReadHQFile()

    def query_hq_file_data(self, req):
        return self.lib.QueryHQFileData(req)
