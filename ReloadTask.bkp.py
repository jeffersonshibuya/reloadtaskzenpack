import Globals
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
dmd = ZenScriptBase(connect=True, noopts=True).dmd

from Products.Zuul.routers.zep import EventsRouter

import requests
import json

#twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin, CommandPlugin


class ReloadTask(PythonPlugin):

    relname = 'qlik_Sense_ReloadTasks'
    modname = 'ZenPacks.IPC.Qlik.Qlik_Sense_ReloadTask'

    requiredProperties = (
        'zPropertie',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        try:
            self.eventRouterInstance = EventsRouter(dmd, "")

            self.headers = {
                'Accept': 'application/json',
            }

            self.params = ()
            
            url = "https://API-URL.com"
            self.response = json.loads(requests.get(url, headers=self.headers, params=self.params)
                                       
            rm = yield self.relMap()

            returnValue(rm)
        except Exception as e:
            log.error('Error: %s' % str(e))
            summary = 'Reload task modeler plugin failed:' +  str(e)
            EventsRouter.add_event(self.eventRouterInstance, summary=summary, device=device.id, severity=4, evclasskey='ReloadTask_modeler_failed', evclass='/App/Failed', component=None)

    def process(self, device, results, log):
        try:
            for x in self.response:
                if x['name'].startswith('Manually triggered'):
                   
                    results.append(self.objectMap({
                        'id': self.prepId(x['id']),
                        'title': x['name'],
                        'taskID': x['id'],
                        'startTime': startTime,
                        'stopTime': stopTime,
                        'manuallyTriggered': x['isManuallyTriggered']
                    }))
                else:
                    results.append(self.objectMap({
                        'id': self.prepId(x['id']),
                        'title': x['name'],
                        'taskID': x['id'],
                        'manuallyTriggered': x['isManuallyTriggered']
                    }))

            #raise Exception('!!error modeling!!')
            success = True
        except Exception as e:
            log.error('Reload task modeler plugin failed: %s' % str(e))
            summary = 'Reload task modeler plugin failed:' +  str(e)
            EventsRouter.add_event(self.eventRouterInstance, summary=summary, device=device.id, severity=4, evclasskey='ReloadTask_modeler_failed', evclass='/App/Failed', component=None)
            success = False

        if success:
            EventsRouter.add_event(self.eventRouterInstance, summary='', device=device.id, severity=0, evclasskey='ReloadTask_modeler_failed', evclass='/App/Failed', component=None)

        log.debug('Reload Tasks: %s' % results)
        return results
