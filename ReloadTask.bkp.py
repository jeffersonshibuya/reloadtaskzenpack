
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
        'zIPCDeviceName',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        try:
            self.eventRouterInstance = EventsRouter(dmd, "")

            self.headers = {
                'Accept': 'application/json',
                'Cache-Control': 'no-cache',
                'X-Qlik-Xrfkey': '123456789ABCDEFG',
                'vnoc': 'vnoc',
            }

            self.params = (
                ('xrfkey', '123456789ABCDEFG'),
            )

            deviceName = getattr(device, 'zIPCDeviceName', None)
            if not deviceName:
                deviceName = device.id

            self.response = json.loads(requests.get('https://'+deviceName+'/vnoc/qrs/reloadtask/full', headers=self.headers, params=self.params).text)

            #log.info('response: %s' % response)
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
                    #if x['isManuallyTriggered']:

                    if x['operational']['lastExecutionResult']['startTime'][:10] == '1753-01-01':
                        startTime = ''
                    else:
                        startTime = x['operational']['lastExecutionResult']['startTime'][:16].replace('-', '/').replace('T', ' ')

                    if x['operational']['lastExecutionResult']['stopTime'][:10] == '1753-01-01':
                        stoptTime = ''
                    else:
                        stopTime = x['operational']['lastExecutionResult']['stopTime'][:16].replace('-', '/').replace('T', ' ')

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
