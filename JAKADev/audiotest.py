import pyaudio
p = pyaudio.PyAudio()
num = p.get_device_count()
for i in range(0, num):
    device = p.get_device_info_by_index(i)
    if device.get('maxInputChannels')>0:
        print('Input index '+str(i)+' name:'+device.get('name'))
    if device.get('maxOutputChannels')>0:
        print('Output index '+str(i)+' name:'+device.get('name'))
