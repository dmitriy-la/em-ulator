import json


class IoManager(object):
    def __init__(self):
        pass

    # @staticmethod
    def loadJsonFile(self, fileHandler):
        return json.load(fileHandler)

    def dumpJsonFile(self, fileHandler, fileDatalist=None):
        if fileDatalist is None:
            fileDatalist = []

        json.dump(fileDatalist, fileHandler, indent=4, ensure_ascii=False)
