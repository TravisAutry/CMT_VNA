#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 15:05:35 2020

@author: tma
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import visa    #PyVisa is required along with NIVisa
import os

'''Library for controlling the M5065 Copper Mountain VNA.  The Network Remote
Control Settings must have Socket Server ON in ordr for this to work.  The 
default port is 5025

Note all commands are case sensitive so tamper at your own risk

This programs assumes that the VNA is sweeping in continuous mode.  Otherwise 
the trigger has to be adjusted.


'''

class VNA():
    
    
    def __init__(self,socket = '5025',start = '3 GHz',stop = '4 GHz',
                 IFBW = '1 kHZ',points = 3001):
        self.CMT = Open_Device()
        self.Num_Traces = 4
        self.start = start
        self.stop = stop
        self.BW = IFBW
        self.Points = points
        self.Traces_strings = ['S11','S12','S22','S21']
        self.power = -10 # in dBm
        
        self.display_set = 'MLOG|PHAS|GDEL|SLIN|SLOG|SCOM|SMIT|SADM|PLIN|PLOG|  \
        POL|MLIN|SWR|REAL|IMAG|UPH'
        
        #Initialize VNA with Default Params
        self.Freq_Range()
        self.IFBW()
        self.SetPower()
        self.NPoints()
        self.Traces(Format = 'MLOG')
        #self.data = self.Record()
        
        #figures
        self.logplot  = []
        self.linplot = []
        self.phaseplot = []
        self.phaseplot2 = []
        
        

    def Open_Device(socket = '5025'):
        '''Opens the Device Through PyVISA'''
        
        rm = visa.ResourceManager()
    
        try:
            string = 'TCPIP0::localhost::' + socket + '::SOCKET'
            CMT = rm.open_resource(string)
        except:
            print("Failure to connect to VNA!")
            print("Check network settings")
        #The VNA ends each line with this. Reads will time out without this
        CMT.read_termination='\n'
        #Set a really long timeout period for slow sweeps
        CMT.timeout = 100000
        
        return CMT
    
    
    def Freq_Range(self):
        '''Sets the Frequency Range'''
    
        print('Starting Frequency is: ' + self.start)
        print('Ending Frequency is: ' + self.stop)
        values=[]
        string = 'SENS1:FREQ:STAR ' + self.start + ';STOP ' + self.stop + '\n'
        self.CMT.write_ascii_values(string,values)
        
        return
    
    
    def IFBW(self):
        '''Sets the IF BW'''
    
        print('IFBW: ' + self.BW)
        values=[]
        string = 'SENS1:BWID ' + self.BW + '\n'
        self.CMT.write_ascii_values(string,values)
        
        return
    
    
    def NPoints(self):
        '''Sets the Number of Points'''
    
        print('NPoints is: ' + str(self.Points))
        values=[]
        string = 'SENS1:SWE:POIN ' + str(self.Points) +'\n'
        self.CMT.write_ascii_values(string,values)  #Number of points
        
        return
    
    def SetPower(self):
        '''Sets the power in dbm'''
        values = []
        string = "SOUR:POW:LEV:IMM " + str(self.power) +'\n'
        self.CMT.write_ascii_values(string,values)  #Number of points
        
        string = "SOUR:POW:LEV:IMM?\n"
        b = self.CMT.query(string)  #Number of points
        self.power = b
        return
    
    def Trigger(self,Setting = 'ON'):
        '''Sets the trigger to be continuous or not also sets the trigger to be
        software defined
        
        Selects the trigger source (see options below).If the the continuous trigger 
        initiation mode is enabled with the command INIT:C ONT ON, the 
        INTernalchoice leads to continuous sweep. The choice of another
        option switches the analyzer to the triggerwaiting state from the
        corresponding source.If the the continuous trigger initiation mode
        is disabled with the command INIT:C ONT OFF, the reactionto INIT command 
        is different. Selecting INTernal leads to a single sweep in response to
        the commandINIT, selection another option puts the analyzer in a single
        trigger waiting state in response to the INITcommand
        
        '''
        values=[]
        string = 'INIT:CONT ' + Setting +'\n'
        self.CMT.write_ascii_values(string,values) 
        self.CMT.write_ascii_values('TRIG:SOUR BUS\n',values)
        return
    
    
    def Traces(self,Format = 'POL'):
        '''Defines the traces with a default ordering that goes 
         S11, S12, S22, S21 and sets up the traces to be recorded in polar format
         
         The ordering is returned at the function end
         {MLOG|PHAS|GDEL|SLIN|SLOG|SC OM|SMIT|SADM|PLIN|PLOG| POL|MLIN|SWR|REAL|IMAG|UPH}
         '''
        
        values=[]
        str1 = 'CALC1:PAR:COUN ' + str(self.Num_Traces) + '\n'
        self.CMT.write_ascii_values(str1,values) #  Traces
        
        Traces_strings = self.Traces_strings #['S11','S12','S22','S21']
        TracesForm_strings = ['TRAC1','TRAC2','TRAC3','TRAC4'] 
        #For some reason the TRAC commands dont work
    
        for i in range(self.Num_Traces):
            '''Define the order and Format of the Traces'''
            str2 = 'CALC1:PAR' + str(i+1) + ':DEF ' + Traces_strings[i] + '\n'
            str4 = 'CALC1:PAR' + str(i+1) + ':SEL\n'
            str5 = 'CALC1:FORM ' +Format + '\n'
    #        str3 = 'CALC1:' + TracesForm_strings[i] + ':FORM POL\n'
            
            self.CMT.write_ascii_values(str2,values) #Choose which gets measured
            self.CMT.write_ascii_values(str4,values) #Log Mag format
            self.CMT.write_ascii_values(str5,values) #Log Mag format
            
        print('Trace ordering is: ')
        print(*Traces_strings[0:i+1])
        return Traces_strings[0:i+1] # returns the trace labels/ordering
    
    
    
    def Record(self):
        '''Records Data from the Traces with a single "new" measurement
         
         '''
         
        #Make sure the traces are in polar format
        self.Traces(Format = 'POL')
        
        values=[]    
        self.CMT.write_ascii_values('TRIG:SEQ:SING\n',values) #Trigger a single sweep
        self.CMT.query('*OPC?\n') #Wait for it to finish
        
        Traces_strings = self.Traces_strings 
        TracesForm_strings = ['TRAC1','TRAC2','TRAC3','TRAC4']
        
        Freq = self.CMT.query("SENS1:FREQ:DATA?\n") #Get data as string
        Freq = Freq.split(",")
        Freq = np.array(Freq)
        Freq = Freq.astype('float')
         
        
    # Define DataFrame
        dat_freq = pd.Series(data=Freq*1E-6,name = 'Freq (MHz)')
        df = pd.DataFrame(dat_freq)
        for i in range(self.Num_Traces):
            str2 = 'CALC1:' + TracesForm_strings[i] + ':DATA:FDAT?\n'
            
            data = self.CMT.query(str2) #Data is returned as a String
            data = data.split(",")
            data = np.array(data)
            data = data.astype('float')
            X = data[::2]
            Y = data[1::2]
            Z = X + np.complex(0,1)*Y
            df[Traces_strings[i]] = Z
        self.data = df
        return 
    
    def Rec_Sav_Res(self,direc = '/'):
        
        #Records Compelx data and then resets the Screen to log mag
        
        self.Record()
        self.SaveData(direc = direc)
        self.Traces(Format = 'MLOG')
        
        return

    def SaveData(self,direc  = '/'):
        # as an example direc should be 
        #direc = '/home/tma/Documents/Python Scripts/test1/'
    
        filepath = direc
        
        if os.path.isdir(direc):
            print('This Directory already exists. This data will not be saved')
        else:
            os.mkdir(direc)
            #Save the Data
            df = self.data
            df.to_csv(filepath + 'data.txt')
            
            
            #Save the VNA settings                        
            l1 = ['Num_Traces','Freq Start','Freq End','IFBW','Points','Power (dBm)']
            l2 = [self.Num_Traces ,self.start, self.stop,self.BW,self.Points,self.power]
    
            dictionary = dict(zip(l1, l2))
            Common_Params = pd.Series(dictionary)
            Common_Params.to_csv(filepath + 'VNAsettings.txt')
            
            #Make Plots and Plot the figures
            x = df[df.columns[0]].values
            y = (df[df.columns[1:]].values)
            
            logplot = plt.figure();
            self.logplot = logplot
            for y_arr,label in zip( np.transpose(y),self.Traces_strings):
                plt.plot(x,20*np.log10(np.abs(y_arr)),label = label + '|Z|')
            plt.legend()
            plt.ylabel('dB')
            plt.xlabel(df.columns[0])
            logplot.savefig(filepath + 'logplot.png',dpi=600)
        
        
            linplot = plt.figure();
            self.linplot = linplot

            for y_arr,label in zip( np.transpose(y),self.Traces_strings):
                plt.plot(x,(np.abs(y_arr)),label = label + '|Z|')
            plt.legend()
            plt.ylabel('Mag')
            plt.xlabel(df.columns[0])
            linplot.savefig(filepath + 'linplot.png',dpi=600)

            phaseplot = plt.figure();
            self.phaseplot = phaseplot

            for y_arr,label in zip( np.transpose(y),self.Traces_strings):
                plt.plot(x,np.unwrap(np.angle(y_arr)),label = label + 'phi')
            plt.legend()
            plt.ylabel('Unwrapped Phase')
            plt.xlabel(df.columns[0])
            phaseplot.savefig(filepath + 'phaseplot.png',dpi=600)

            phaseplot2 = plt.figure();
            self.phaseplot2 = phaseplot2

            for y_arr,label in zip( np.transpose(y),self.Traces_strings):
                plt.plot(x,(np.angle(y_arr)),label = label + 'phi')
            plt.legend()
            plt.ylabel('Unwrapped Phase')
            plt.xlabel(df.columns[0])
            phaseplot2.savefig(filepath + 'phaseplot2.png',dpi=600)

