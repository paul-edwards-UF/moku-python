################################################
# Moku:Lab Remote Phasemeter DAQ with Python (pymoku v2.8.3)
############################################### 
'''
NOTE: This is now "legacy" code, only for FW<=511.
Use IPv4 address to run Moku:Lab phasemeter.
'''

from pymoku import *
import pymoku.instruments as inst
import numpy as np
import csv
import time as tt
import os
import sys
import matplotlib.pyplot as plt
from scipy import signal

'''
Preamble for the MOKU connections and configuration settings.
deploy_instrument: If the instrument is already Phasemeter(PM), connects to it. Else, deploys the PM. Using external clock as reference.
inst.Phasemeter(): Choose what instrument you want to use.
take_ownership(): Takes ownership of the Moku and prevents any other device from connecting(?)

To execute the file: python remote_acquire_moku.py 'duration (secs)' 'info string'

'''

m = Moku('10.244.xx.xx') #-- connect to moku (fill in IPv4 here)

i=m.discover_instrument()
i = inst.Phasemeter()
m.deploy_instrument(i, set_default = True, use_external=True) 
m.take_ownership()

#-- Setting up PM parameters.
i.set_samplerate('veryslow') #-- PM sampling rate for data acquisition
fs = 30.5176

i.set_bandwidth(1, 10000) 
i.set_frontend(1, fiftyr=True, atten = False, ac = True)
i.set_initfreq(1,10e6)


i.set_bandwidth(2, 10000)
i.set_frontend(2, fiftyr=True, atten = False, ac = True)
i.set_initfreq(2,10e6)

i.auto_acquire()

genpath = r'P:\ResLabs\LISAscope\physics-svc-lisascope\data'
date = tt.strftime("%Y_%m_%d")
fname = 'PhasemeterData_' + tt.strftime("%Y_%m_%d_%H%M%S") + '.csv'
fname_reduced = 'ReducedPhasemeterData_' + tt.strftime("%Y_%m_%d_%H%M%S") + '.csv'
writepath = os.path.join(genpath,date)

if not os.path.isdir(writepath):
    print('Created new folder')
    os.mkdir(writepath)
    
writepath = os.path.join(genpath,date,fname)
writepath_reduced = os.path.join(genpath, date, fname_reduced)

print("Measurement duration: ", float(sys.argv[1])/3600," Hours")
length = int(sys.argv[1]) #-- Duration of data run in sec
info_string = str(sys.argv[2] + ' ') #-- Purpose of the measurement
if len(sys.argv) == 3: 
    two_channel = False
    print('single channel engaged')
elif len(sys.argv)>=4: 
    two_channel = True
    i.auto_acquire(ch = 1)
    i.auto_acquire(ch = 2)
    print('Two channel engaged')


# #-- Logging data to SD card
# try:
# 	i.stop_data_log() #-- Stops any previous logging
# 	i.start_data_log(duration=tlen, use_sd=True, ch1=True, filetype='csv' ) #-- Start a new data log for 600 seconds on the sd card with data from only Channel1 

try:
    # Stop previous network sessions, if any
    i.stop_stream_data()
 
    # Start a new network streaming session
    # length-second duration, single channel
    i.start_stream_data(duration=length, ch1=True, ch2=two_channel)
    
    f = open(writepath,'wt')
    f_reduced = open(writepath_reduced, 'a+', newline="")
    f2 = open(writepath_reduced, 'at')
    
    fwrite = csv.writer(f, delimiter=',', lineterminator='\n')
    fwrite_reduced = csv.writer(f_reduced, delimiter=',', lineterminator='\n')
    f2write = csv.writer(f2, delimiter=',', lineterminator='\n')

    loop_start_time = tt.time()
    start_time = 0
    loop_iter = 0
    plot_width = 7200
#     print('l')
    
    # plt.ion()
    # plt.figure(figsize=(10,10))
    # plt.xticks(fontsize=20)
    # plt.grid(b=True, which='major', color='black', linestyle='-', linewidth=1.2)
    # plt.grid(b=True, which='minor', color='grey', linestyle='--', linewidth=0.7)
    # plt.yticks(fontsize=20)
    # plt.title('Ongoing Time Series',fontsize=24)
    # plt.ylabel(r'Beat Frequency [$MHz$]', fontsize=20)
    # plt.xlabel(r'Time [$H$]', fontsize=20)

    f.write(info_string+tt.strftime("%Y_%m_%d_%H%M%S") +"\n")
    f_reduced.write("Date:"+tt.strftime("%Y_%m_%d") +"\nTime:"+tt.strftime("%H_%M_%S %Z") + "\n" + info_string + "\n")

    if two_channel: f.write("# Time(sec), Set f1(Hz), Measured F1(Hz), Index, Phi1, I1, Q1, Set F2(Hz), Measured F2(Hz), Index2, Phi2, I2, Q2 \n") #-- For double channel acquisition
    else: f.write("# Time(sec), Set f1(Hz), Measured F1(Hz), Index, Phi1, I1, Q1 \n") #-- For single channel acquisition

    if two_channel: f_reduced.write("# Time(sec), Measured F1(Hz), Measured F2(Hz) \n") #-- For double channel acquisition
    else: f_reduced.write("# Time(sec), Measured F1(Hz) \n") #-- For single channel acquisition

    f_reduced.close()
    f_reduced = open(writepath_reduced, 'a+', newline = "")
    fwrite_reduced = csv.writer(f_reduced, delimiter=',', lineterminator='\n')

    buffer_size = 1000

    if two_channel == False:
        buffer_ch1 = np.zeros((buffer_size+20,2))
        buffer_full = np.zeros((buffer_size+20,7))
        ch1_write = np.zeros((buffer_size,2))
        full_write = np.zeros((buffer_size,7))

    else:
        buffer_ch1 = np.zeros((buffer_size+20,3))
        buffer_full = np.zeros((buffer_size+20,13))
        ch1_write = np.zeros((buffer_size,3))
        full_write = np.zeros((buffer_size,13))
    # write_out = np.ones((100,2))
    index_count = 0

    order = 5
    b, a = signal.butter(order-1, 1, btype = 'low', output = 'ba', fs = fs)
    with open(writepath_reduced, 'a+', newline = "") as f_reduced:
        while True:
            current_time = tt.time()
            if (current_time-loop_start_time > length):break   #--- Checks if the desired time length is already attained
                
        #         print('m')
            while index_count<buffer_size:
                samples = i.get_stream_data(n=0)
                n = len(samples[0])
                # print("index_in:", index_count+n)
                
                stop_time = start_time+((n-1)/fs)
                timestamp = np.linspace(start_time,stop_time,n).reshape((n,1))
                start_time = stop_time + (1/fs)
                
                
        #         print(timestamp,n)
                if not any(samples): break
                ch1_samples = np.array(samples[0])
                if two_channel: ch2_samples = np.array(samples[1])

               
                # y = signal.decimate(np.reshape(ch1_samples[:,1], (len(ch1_samples),1)), q = 8, n=2, ftype = 'iir')
                # print(len(y))
                # print(len(ch1_samples))
                # print(np.shape(ch1_samples), np.shape(timestamp), np.shape(np.reshape(ch1_samples[:,1], (len(ch1_samples),1))))
                
                if two_channel: data_samples = np.hstack((timestamp, ch1_samples, ch2_samples)) #-- Make sure the format is correct here and that they concatenate in the correct way
                else: data_samples = np.hstack((timestamp, ch1_samples))

                if two_channel: data_samples_reduced = np.hstack((timestamp, np.reshape(ch1_samples[:,1], (len(ch1_samples),1)), np.reshape(ch2_samples[:,1], (len(ch2_samples),1)))) #-- Make sure the format is correct here and that they concatenate in the correct way
                else: data_samples_reduced = np.hstack((timestamp, np.reshape(ch1_samples[:,1], (len(ch1_samples),1))))
                # print(data_samples_reduced, np.shape(data_samples_reduced), index_count)
                buffer_ch1[index_count:index_count+n] = data_samples_reduced
                buffer_full[index_count:index_count+n] = data_samples
                index_count +=n

            # random_noise = np.random.randn(len(buffer_ch1[:,1]))+10e6 
            # buffer_ch1[:,1] = random_noise
            # buffer_full[:,2] = random_noise
            if index_count>buffer_size: write_to = buffer_size
            else: write_to = index_count
            ch1_write = buffer_ch1[:write_to].copy()

            # dc_step = np.mean(ch1_write[:,1])
            y2 = np.zeros(len(ch1_write[:,1]))
            if two_channel: y3 = np.zeros(len(ch1_write[:,2]))
            # x = ch1_write[:,1].copy()
            # x = ch1_write[:,1].copy()-dc_step
            


            if loop_iter==0:
                # print('in if')
                # x = ch1_write[:,1].copy()-dc_step
                x = ch1_write[:,1].copy()
                if two_channel: x3 = ch1_write[:,2].copy()
                # x = np.random.randn(50000)+1.0e6
                # y2 = signal.lfilter(b, a, x)
                for aa in range(len(x)):
                    if aa<order:
                        loop_count = aa
                        y2[0] = b[0]*(x[0])
                        if two_channel: y3[0] = b[0]*(x3[0])
                    else: loop_count = order
                    for k in range(loop_count):
                        # print(aa,k)
                        y2[aa] += b[k]*x[aa-k]
                        if two_channel: y3[aa] += b[k]*x3[aa-k]
                        if k>0: 
                            y2[aa] -= a[k]*y2[aa-k]
                            if two_channel: y3[aa] -= a[k]*y3[aa-k]
                # y2 +=dc_step
                # print(y2)
            else:
                # print('in else')
                # print(np.shape(prev_chunk_x), np.shape(x))
                # print(np.shape(prev_chunk_x), np.shape(x))
                # print(prev_chunk_x)
                # print(prev_chunk_y)
                x = ch1_write[:,1].copy()
                if two_channel: x3 = ch1_write[:,2].copy()
                # print(x[0:5])
                # print(y2)
                y2 = np.zeros(len(x))
                if two_channel: y3 = np.zeros(len(x3))
                # y_all_dc_step = prev_chunk_y[0]
                x_all = np.concatenate((prev_chunk_x, x))
                y_all = np.concatenate((prev_chunk_y, y2))
                if two_channel: 
                    x_all3 = np.concatenate((prev_chunk_x3, x3))
                    y_all3 = np.concatenate((prev_chunk_y3, y3))
                # x_all_dc_step = x_all[0]
                # y_all[order:] = dc_step + signal.lfilter(b, a, x_all-dc_step)
                # print(x_all[0:10])
                # print(y_all[0:10])
                # x_all_dc_step = np.mean(x_all)
                # y_all_dc_step = np.mean(y_all)
                # x_all -= x_all_dc_step
                # y_all[0:order] -= y_all_dc_step
                for aa in range(order, len(x_all)):
                    loop_count = order
                    for k in range(loop_count):
                        # print(aa,k)
                        y_all[aa] += b[k]*x_all[aa-k]
                        if two_channel: y_all3[aa] += b[k]*x_all3[aa-k]
                        if k>0: 
                            y_all[aa] -= a[k]*y_all[aa-k]
                            if two_channel: y_all3[aa] -= a[k]*y_all3[aa-k]
                # x_all += x_all_dc_step
                # y_all += y_all_dc_step
                y2 = y_all[order:]
                if two_channel: y3 = y_all3[order:]
                # print('y2:',y2)

            
            ch1_write[:,1] = y2.copy()
            if two_channel: ch1_write[:,2] = y3.copy()
            
            prev_chunk_y = y2[write_to-order:write_to].copy()
            prev_chunk_x = buffer_ch1[write_to-order:write_to, 1].copy()

            if two_channel:
                prev_chunk_y3 = y3[write_to-order:write_to].copy()
                prev_chunk_x3 = buffer_ch1[write_to-order:write_to, 2].copy()
            # print(dc_step)
            # ch1_write[:,1] = dc_step + signal.lfilter(b, a, ch1_write[:,1]-dc_step)
            # print(write_out, buffer_ch1[:100:10], ch1_write[0:100:10,1])

            full_write = buffer_full[:write_to].copy()


            if((loop_iter%100)==0):
            	# if np.abs(data_samples[0,2]-data_samples[1,2]) > 1e5:
            	# 	print("Broken Lock!!!")
            	# 	i.auto_acquire()

    	        
                if two_channel: 
                    time, f1, f2 = data_samples[0,0], data_samples[0,2], data_samples[0,8]
                    print("Beat frequency:", f1, f2)

                else:
                    time, f1 = data_samples[0,0], data_samples[0,2]
                    print("Beat Frequency:", f1)
                # if np.abs(data_samples[0,2]-data_samples[1,2])>100e3: 
                #     print("Broken Lock!!!")
                #     i.auto_acquire()
    	        
                # plt.scatter(time/3600, f1/1e6, label='1 Vpp frequency')
                # plt.pause(0.0001)
                # plt.xlim(int(start_time-1800)/3600,int(start_time+1800)/3600)

            write_out = ch1_write[0::10].copy()
            if two_channel == False: print(write_out[0,1])
            if two_channel: print(write_out[0,1], write_out[0,2])
            # write_out = ch1_write.copy()
            fwrite.writerows(full_write)
            fwrite_reduced = csv.writer(f_reduced, delimiter=',', lineterminator='\n')
            fwrite_reduced.writerows(write_out)

            # print("index_out:",index_count)
            if index_count<buffer_size: break
            buffer_ch1[:index_count-buffer_size] = buffer_ch1[buffer_size:index_count]
            buffer_full[:index_count-buffer_size] = buffer_full[buffer_size:index_count]
            index_count -= buffer_size

    #         print("loop Time:",time.time()-loop_start_time)
            loop_iter +=1
#     plt.legend(fontsize=20)
    # plt.show()
    
 
 
    # Session has completed.
    # Denote that we are done with the network stream so resources
    # may be cleaned up.
        print("Session done!")
        print("Beat frequency:", f1)
        i.stop_stream_data()
        f.close()
        f_reduced.close()
        m.close()
  
except StreamException as e:
    print("Network stream error: %s" % e.message)

except KeyboardInterrupt:
    f.close()
    f_reduced.close()
    i.stop_stream_data()
    m.close()
