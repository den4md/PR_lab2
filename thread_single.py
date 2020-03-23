import threading


class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def start(self):
        if type(self.thr) is threading.Thread:
            self.thr.start()

    thr = None
