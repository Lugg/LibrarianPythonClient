import datetime
import json
import requests

from io import BytesIO
import matplotlib.pyplot as plt

class pyScribbler:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.resetScribbler()

    def resetScribbler(self):
        self.experiment = {
            "parameterGroups" : [],
            "performanceMeasures" : []
        }
        self.files = []
    def getPath(self):
        return self.host + ":" + str(self.port) + "/documentation/" + self.documentationId + "/experiment/" + self.experimentId;

    def setMetaData(self, author, description, title):
        self.experiment["author"] = author
        self.experiment["description"] = description
        self.experiment["title"] = title

    def setExperimentName(self, documentationId, experimentId):
        self.experimentId = experimentId
        self.documentationId = documentationId

    def addParameter(self, iteration, group, name, value):
        self.experiment["parameterGroups"].append(
        {
            "group" : group,
            "name" : name,
            "value" : value,
            "iteration" : iteration
        })

    def addPerformanceMeasure(self, iteration, name, value):
        self.experiment["performanceMeasures"].append(
        {
            "iteration" : iteration,
            "name" : name,
            "value" : value
        })

    def experimentStarted(self, iterations=1, estimatedTimeLeft=0):
        self.experiment["timestampStart"] = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()
        payload = {
            "iterations" : iterations,
            "estimatedTimeLeft" : estimatedTimeLeft,
        }
        send = json.dumps(payload)
        r = requests.post(self.getPath() + "/experimentStarted", data=send)

    def experimentEnded(self):
        self.experiment["timestampEnd"] = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()
        r = requests.post(self.getPath() + "/experimentFinished")

        send = {"experimentJSON": json.dumps(self.experiment)}
        r = requests.post( self.getPath(),data=send )
        print r.text

    def experimentIterationFinished(self, currentIteration=0, estimatedTimeLeft=0 ):
        payload = {
            "currentIteration" : currentIteration,
            "estimatedTimeLeft" : estimatedTimeLeft
        }
        send = json.dumps(payload)
        r = requests.post( self.getPath() + "/iterationFinished", data=send)

    def savePyplotFigure(self, plt, name):
        buf = BytesIO()
        plt.savefig(buf, format='png')
        self.saveBufferAsFile(buf,name, '.png' , 'image/png')

    def saveBufferAsFile(self, buf, name, fileEnding, mimetype):
        buf.seek(0)
        files = [('file', ( name + fileEnding, buf, mimetype))]
        r = requests.post(self.getPath() + "/file", files=files)
        buf.close()
        print r.text

    def saveHTML(self, html, name):
        files = [('file', ( name + '.html', html, "text/html"))]
        r = requests.post(self.getPath() + "/file", files=files)
        print r.text
