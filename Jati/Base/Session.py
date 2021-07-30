import threading
import random
import datetime
import pickle, os


class Session:
    """
    Session Base Class.
    Session <One to many> connection.
    """

    def __init__(self, sesid, timeout = 259200):
        self.id = sesid
        self.timeout = timeout
        self.idle = datetime.datetime.now()
        self.data = {}


    def set_data(self, param, value):
        """Save data"""
        self.data[param] = value
        self.idle = datetime.datetime.now()


    def get_data(self, param):
        """Get data"""
        if param in self.data:
            self.idle = datetime.datetime.now()
            return self.data[param]
        return None


    def del_data(self, param):
        """Delete data"""
        del self.data[param]
        self.idle = datetime.datetime.now()


    def del_all_data(self):
        """Delete all data"""
        self.data = {}
        self.idle = datetime.datetime.now()


class SessionHandler(threading.Thread):
    """Session Handler"""

    def __init__(self, path_save):
        threading.Thread.__init__(self)
        self.path_save = path_save
        self.isClose = threading.Event()
        if os.path.isfile(self.path_save):
            with open(self.path_save, 'rb') as input:
                self.sessionList = pickle.load(input)
        else:
            self.sessionList = {}


    def generate_id_cookies(self):
        """Generate Cookie id"""
        sesid = ''
        for x in range(26):
            c = random.randint(1, 31)
            c2 = random.randint(0, 1)
            if(c < 27):
                if c2:
                    c = c | 64
                else:
                    c = c | 96
                sesid += chr(c)
            else:
                c = c % 27
                if c2:
                    c += 5
                sesid += str(c)
        return sesid


    def generate_key(self):
        """Generate session id"""
        session_id = self.generate_id_cookies()
        while session_id in self.sessionList:
            session_id = self.generate_id_cookies()
        return session_id


    def get_cookies(self, request):
        """Get cookies from request header"""
        cookies = {}
        if 'Cookie' in request.headers:
            for cookies_header in request.headers['Cookie'].split('; '):
                key, val = cookies_header.split('=', 1)
                cookies[key] = val
        return cookies


    def create(self, request, response):
        """create Session"""
        cookies = self.get_cookies(request)
        if 'PySessID' in cookies:
            session_id = cookies['PySessID']
            if session_id in  self.sessionList:
                return self.sessionList[session_id]

        session_id = self.generate_key()
        response.set_header('Set-Cookie', 'PySessID='+session_id+';path=/')
        self.sessionList[session_id] = Session(session_id)
        return self.sessionList[session_id]


    def run(self):
        """
        Running handler until application is closed.
        expired session will be deleted.
        """
        while not self.isClose.wait(60):
            now = datetime.datetime.now()
            s_l = sorted(self.sessionList.values(), key=lambda g:g.idle+datetime.timedelta(seconds=g.timeout))
            for s in s_l:
                if now > s.idle+datetime.timedelta(seconds=s.timeout):
                    del self.sessionList[s.id]
                else:
                    break


    def close(self):
        """Close Session Handler"""
        self.isClose.set()
        with open(self.path_save, 'wb') as output:  # Overwrites any existing file.
            pickle.dump(self.sessionList, output, pickle.HIGHEST_PROTOCOL)
