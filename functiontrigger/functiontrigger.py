import logging
import os
import re
import time
import docker

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class Functions(object):

    def __init__(self, label='ftrigger', name=None, refresh_interval=5):
        self.refresh_interval = int(os.getenv('TRIGGER_REFRESH_INTERVAL', refresh_interval))
        self.last_refresh = 0
        self._functions = {}
        self._stack_namespace = os.getenv('STACK_NAMESPACE', None)
        self._label = os.getenv('TRIGGER_LABEL', label)
        self._name = os.getenv('TRIGGER_NAME', name)
        self._register_label = f'{label}.{name}'
    
    @property
    def label(self):
        return self._label
    
    @property
    def name(self):
        return self._name
    
    def refresh(self, force=False):
        #if not force and time.time() - self.last_refresh < self.refresh_interval:
            #return [], [], []
    
        add_functions = []
        update_functions = []
        remove_functions = []
    
        functions = self.get_docker_swarm_function_list()
        #functions = self.gateway.get(self._gateway_base + '/system/functions').json()
        #if self._stack_namespace:
            #functions = filter(lambda f: f.get('labels', {}).get('com.docker.stack.namespace') == self._stack_namespace,
                               #functions)
        #functions = list(filter(lambda f: self._register_label in f.get('labels', {}), functions))
     
        # Scan for new and updated functions
        for function in functions:
            existing_function = self._functions.get(function['name'])
    
            if not existing_function:
                # register a new function
                log.debug(f'Add function: {function["name"]}')
                add_functions.append(function)
                self._functions[function['name']] = function
            elif False:
            # elif function['service'].attrs['UpdatedAt'] > existing_function['service'].attrs['UpdatedAt']:
                # maybe update an already registered function
                log.debug(f'Update function: {function["name"]}')
                update_functions.append(function)
                self._functions[function['name']] = function
    
        # Scan for removed functions
        for function_name in set(self._functions.keys()) - set([f['name'] for f in functions]):
            function = self._functions.pop(function_name)
            log.debug(f'Remove function: {function["name"]}')
            remove_functions.append(function)
    
        self.last_refresh = time.time()
        return add_functions, update_functions, remove_functions
    
    def get_docker_swarm_function_list(self):
        tls_config = docker.tls.TLSConfig(client_cert=('/c/Users/r_kar/bottled-water/certs/cert.pem', '/c/Users/r_kar/bottled-water/certs/key.pem'))
        client = docker.DockerClient(base_url='tcp://192.168.99.100:2376', tls=tls_config)
        function_list = []
        
        for service in client.services.list():
            #Format: <Service: 27fyq6peb4>
            service_str = str(service)
            firstpart, secondpart = service_str.split(':')
            secondpart = secondpart.strip()
            service_id = secondpart.replace('>','')
            service_obj = client.services.get(service_id)
            
            if service_obj.attrs:
               service_spec =  service_obj.attrs['Spec']
               log.debug(str(service_spec))
                         
               if service_spec:
                   service_name = service_spec['Name']
                   service_labels = service_spec['Labels']
                   
                   #if service_labels['ftrigger.kafka']=='true' and service_labels['com.docker.stack.namespace'] == self._stack_namespace:
                   kafka_triggered = service_labels.get('ftrigger.kafka')   
                   if kafka_triggered and kafka_triggered =='true':   
                      
                      function = {}
                      function['name'] = service_name
                      function['labels'] = service_labels
                      function_list.append(function)
        
        log.debug(str(function_list))
        return function_list      
   
    if(__name__ == "__main__"):
        from functiontrigger import Functions
        log.debug('In main method')
        obj = Functions('ftrigger', None, 5) 
        obj.refresh(False)

