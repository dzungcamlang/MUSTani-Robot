
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import characteristics
import numpyjsonencoder
import json
import wave
import uuid
import numpy
import math
import os
import datetime
from scipy.io.wavfile import write
from path import __wavedestination__

class util:

    def __init__(self, debug):
        self.debug = debug
        self.characteristic = characteristics.characteristic(debug)

    def showdictentriesbyid(self):
        json_data = self.getDICT()
        for dict_entries in json_data['dict']:
            print (dict_entries['id'] + ' ' + dict_entries['uuid'])

    def showdictentry(self, sid):
        json_data = self.getDICT()
        ids = [ ]
        for dict_entries in json_data['dict']:
            if ((dict_entries['id'] == sid or sid == "*") and dict_entries['id'] not in ids):
                print (dict_entries['id'] + ' - ' + dict_entries['uuid'])
                for i, entry in enumerate(dict_entries['characteristic']):
                    output = str(entry['norm'])
                    print (str(i)+ ', ' + str(entry['fc']) + ', ' + output[1:len(output)-1])

    @staticmethod
    def compile_analysis(json_data):
        analysis = { }
        for dict_entries in json_data['dict']:
            if (dict_entries['id'] not in analysis):
                analysis[dict_entries['id']] = { 'min_tokens': 0, 'max_tokens': 0, 'peaks': [ ], 'df': [ ], 'minp': [ ], 'maxp': [ ], 'cp': [ ], 'mincp': [ ], 'maxcp': [ ] }
            l = len(dict_entries['characteristic'])
            if (l < 2):
                print ('the following characteristic is < 2!')
                print (dict_entries['id'] + ', ' + dict_entries['uuid'])
            if (l > analysis[dict_entries['id']]['max_tokens']):
                analysis[dict_entries['id']]['max_tokens'] = l
            if (l < analysis[dict_entries['id']]['min_tokens'] or analysis[dict_entries['id']]['min_tokens'] == 0):
                analysis[dict_entries['id']]['min_tokens'] = l
            for i, entry in enumerate(dict_entries['characteristic']):
                if (i == len(analysis[dict_entries['id']]['cp'])):
                    analysis[dict_entries['id']]['cp'].append([len(entry['peaks'])])
                else:
                    ll = len(entry['peaks'])
                    if (ll not in analysis[dict_entries['id']]['cp'][i]):
                        analysis[dict_entries['id']]['cp'][i].append(ll)
                if (i == len(analysis[dict_entries['id']]['peaks'])):
                    analysis[dict_entries['id']]['peaks'].append(entry['peaks'])
                else:
                    for miss in entry['peaks']:
                        if (miss not in analysis[dict_entries['id']]['peaks'][i]):
                            analysis[dict_entries['id']]['peaks'][i].append(miss)
                    op = sorted(analysis[dict_entries['id']]['peaks'][i])
                    analysis[dict_entries['id']]['peaks'][i] = op
                if (i == len(analysis[dict_entries['id']]['df'])):
                    analysis[dict_entries['id']]['df'].append([])
                if (entry['df'] not in analysis[dict_entries['id']]['df'][i]):
                    analysis[dict_entries['id']]['df'][i].append(entry['df'])
                    op = sorted(analysis[dict_entries['id']]['df'][i])
                    analysis[dict_entries['id']]['df'][i] = op
        for id in analysis:
            for p in analysis[id]['peaks']:
                 analysis[id]['minp'].append(min(p))
                 analysis[id]['maxp'].append(max(p))
            for cp in analysis[id]['cp']:
                analysis[id]['mincp'].append(min(cp))
                analysis[id]['maxcp'].append(max(cp))
        return analysis

    @staticmethod
    def store_raw_dict_entry(dict_id, raw_characteristics):
        json_obj = {'id': dict_id, 'characteristic': raw_characteristics, 'created': datetime.datetime.now().isoformat() }
        with open("dict/"+str(uuid.uuid4())+".raw", 'w') as json_file:
            json.dump(json_obj, json_file, cls=numpyjsonencoder.numpyjsonencoder)
        json_file.close()

    def learndict(self, characteristics, word_tendency, id):
        dict_model = self.prepare_dict_model(characteristics)
        self.add2dict(dict_model, word_tendency, id)

    @staticmethod
    def prepare_dict_model(characteristics):
        tokens = [ ]
        for o in characteristics:
            characteristic, meta = o
            for m in meta:
                token = m['token']            
                if (token != 'stop'):
                    if (characteristic != None):
                        tokens.append(characteristic)
                    if (token == 'start analysis'):
                        break
        return tokens

    def add2dict(self, obj, word_tendency, id):
        json_obj = self.getDICT()
        json_obj['dict'].append({'id': id, 'characteristic': obj, 'word_tendency': word_tendency, 'uuid': str(uuid.uuid4())})
        self.writeDICT(json_obj)
        return json_obj

    @staticmethod
    def writeDICT(json_data):
        with open("dict/dict.json", 'w') as json_file:
            json.dump(json_data, json_file)
        json_file.close()

    @staticmethod
    def getDICT():
        with open("dict/dict.json") as json_file:
            json_data = json.load(json_file)
        json_file.close()
        return json_data

    def getCompiledDict(self):
        compiled_dict = { 'dict': [ ] }
        for filename in os.listdir("dict/"):
            if (filename.endswith(".raw")):
                fu = filename.split('.')
                file_uuid = fu[0]
                tokens = [ ]
                with open("dict/"+filename) as raw_json_file:
                    json_obj = json.load(raw_json_file, object_hook=numpyjsonencoder.numpyjsonhook)
                    for raw_obj in json_obj['characteristic']:
                        meta = raw_obj['meta']
                        fft = raw_obj['fft']
                        norm = raw_obj['norm']
                        characteristic = self.characteristic.getcharacteristic(fft, norm, meta)
                        if (characteristic != None):
                            for m in meta:
                                if (m['token'] != 'stop'):
                                    tokens.append(characteristic)
                    if (len(tokens) > 0):
                        self.add_weighting(tokens)
                        compiled_dict['dict'].append({'id': json_obj['id'], 'characteristic': tokens, 'uuid': file_uuid })
                    else:
                        print (json_obj['id'] + ' ' + file_uuid+ ' got no tokens!')
                raw_json_file.close()
        return compiled_dict

    @staticmethod
    def add_weighting(tokens):
        high = 0
        for token in tokens:
            cs = sum(token['token_peaks'])/1000.0
            if (cs > high):
                high = cs
        for token in tokens:
            token['weighting'] = sum(token['token_peaks'])/1000.0 / high

    def deletefromdict(self, id):
        json_obj = self.getDICT()
        new_dict = { 'dict': [ ] }
        if (id != '*'):
            dict_objects = json_obj['dict']
            for do in dict_objects:
                if (do['id'] != id):
                    new_dict['dict'].append(do)
        self.writeDICT(new_dict)

    def recreate_dict_from_raw_files(self):
        self.writeDICT(self.getCompiledDict())

    @staticmethod
    def saverawwave(filename, start, end, raw):
        wf = wave.open(__wavedestination__+filename+'.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        data = raw[start:end] 
        wf.writeframes(b''.join(data))

    @staticmethod
    def savefilteredwave(filename, buffer):
        scaled = numpy.int16(buffer/numpy.max(numpy.abs(buffer)) * 32767)
        write(__wavedestination__+filename+'.wav', 44100, scaled)  

    @staticmethod
    def manhatten_distance(arr1, arr2):
        ll = int(max(len(arr1), len(arr2))/2)
        mdl = sum(abs(e - s) for s, e in zip(arr1[0:ll], arr2[0:ll]))
        mdr = sum(abs(e - s) for s, e in zip(arr1[ll:], arr2[ll:]))
        return mdl, mdr

    @staticmethod
    def similarity(arr1, arr2):
        ll = len(arr1)
        ll2 = len(arr2)
        rl = max(ll, ll2)
        sim = 0
        for x in range(0, rl):
            v1 = 0
            v2 = 0
            if (x < ll):
                v1 = arr1[x]
            if (x < ll2):
                v2 = arr2[x]
            if (v1 != 0 and v2 != 0):
                sim += min(v1, v2) / float(max(v1, v2))
        sim = sim / float(rl)
        return sim

    @staticmethod
    def single_similarity(a, b):
        if (a == 0 and b == 0):
            return 1
        elif (a == 0 or b == 0):
            return 0
        elif (a < b):
            return float(a) / float(b)
        return float(b) / float(a)
