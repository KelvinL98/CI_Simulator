#https://stackoverflow.com/questions/36894315/how-to-select-a-specific-input-device-with-pyaudio


import pyaudio


p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name')
        
       
# select device by id
#p.input_device_index = id
#p.output_device_index 


#add input devices to a list, kepeing device ID as its index,
#add add items to a combo box using the addItems() method. 
        #figure out how to handle combo box choices. 
                #either use name and index from the initial list
                #or figure out how to use combo boxes properly?
