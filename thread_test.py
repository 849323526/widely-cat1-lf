import _thread, log, utime


log.basicConfig(level=log.INFO)
thread_log = log.getLogger("Thread")


class Py_thread(object):
    def __init__(self):
        pass

    @staticmethod
    def start_new_thread(size, func, *args):
        """
        This is to create a heartbeat thread module, receiving 3 parameters
        :param size:size is a bytes
        :param func:fuc is a function pointer
        :param args:Can include function pointer
        """
        argv = []
        for i in args:
            argv.append(i)
        if size != 0:
            _thread.stack_size(size)
        _thread.start_new_thread(func, tuple(argv))

