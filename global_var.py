import ujson


class GlobalMap(object):
    # 拼装成字典构造全局变量  借鉴map  包含变量的增删改查
    map = {}

    def set_map(self, key, value):
        if isinstance(value, dict):
            value = ujson.dumps(value)
        self.map[key] = value

    def set(self, **keys):
        try:
            for key_, value_ in keys.items():
                self.map[key_] = str(value_)
                # print(key_ + ":" + str(value_))
        except BaseException as msg:
            print(msg)
            raise msg

    def del_map(self, key):
        try:
            del self.map[key]
            return self.map
        except KeyError:
            print("key:'" + str(key) + "'  不存在")

    def del_allMap(self):
        try:
            self.map = {}
            return self.map
        except Exception as e:
            print(e)
            return e

    def get(self, *args):
        try:
            dic = {}
            for key in args:
                if len(args) == 1 and args[0] != 'all':
                    dic = self.map[key]
                    # print(key + ":" + str(dic))
                elif len(args) == 1 and args[0] == 'all':
                    dic = self.map
                else:
                    dic[key] = self.map[key]
            # print("here")
            # print(dic)
            return dic
        except KeyError:
            print("key:'" + str(key) + "'  not difent")
            return 'Null_'
