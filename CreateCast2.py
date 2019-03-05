#! /usr/bin/env python

#In addition to the listed imports in this software, this requires that AFNI be installed and working
#on the host computer. The 2dseq, reco, and method files from a Bruker imager are required for header
#information. These are located in the scan folder in the case of the method file, and in the
#scan/pdata/1/ folder in the case of the 2dseq and reco files. The software assumes that the user
#is running the script from the scan/pdata/1/ folder.
#
#
# Programmer     Date            Modification
#---------------|---------------|-------------------------------------
#
#
#
#---------------|---------------|-------------------------------------
#
#If you find this software useful in any way, please hug your local developer (or, perhaps, consider
#paying him/her more). If you do not find this software useful, use something else, or ask your local
#developer for help.
#
#Enjoy!
#

#System commands
import commands
#Line reading
import linecache
#Numerical python stuff
import numpy

#NIFTI library stuff
import nibabel
##ASN NIFTI module died a long time ago. Long live NIBABEL
##import nifti
##import nifti.clib as ncl

#GUI stuff
import Tkinter as tk
import Pmw

#MATPLOTLIB stuff
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure

#pyDICOM stuff
import dicom


#############################
#Populate Header Information#
#############################

#Get the info from the reco file
recoFile = open('reco','r')

#Step through the lines, checking for the FOV
myContinue = 1
while myContinue:
    tempLine = recoFile.readline()
    if tempLine == '':
        myContinue = 0;
    if "RECO_size=" in tempLine:
        recoSizeArr = recoFile.readline().split()
    if "RECO_fov=" in tempLine:
        recoFOVArr = recoFile.readline().split()
        for index in range(len(recoFOVArr)):
            recoFOVArr[index] = float(recoFOVArr[index])*10.0

recoFile.close()

#Get info from ../../method
methodFile = open('../../method','r')

#Step through the lines, checking for the number of repetitions
myContinue = 1
while myContinue:
    tempLine = methodFile.readline()
    if tempLine == '':
        myContinue = 0
    if "$PVM_NRepetitions=" in tempLine:
        reps = tempLine.split('=')[-1]
    if "$PVM_SPackArrNSlices" in tempLine:
        print tempLine
        tempLine = methodFile.readline()
        if len(recoSizeArr) == 2:
            recoSizeArr.append(tempLine.split()[0])

methodFile.close()

#Fix the recoFOVArr if it is incorrect
if len(recoFOVArr) == 2:
    recoFOVArr.append(0.1)

#Verify
print recoSizeArr

######################
#Create the AFNI Data#
######################

#Actually run the to3d
cmd = "to3d -omri -prefix recoed -xFOV %fL-R -yFOV %fA-P -zFOV %fS-I \
       -time:zt %i %i %i seq+z -view orig 3Ds:0:0:%i:%i:%i:2dseq" \
       % (recoFOVArr[0]/2.0, recoFOVArr[1]/2.0, recoFOVArr[2]/2.0, \
       int(recoSizeArr[2]), int(reps), 1, int(recoSizeArr[1]), int(recoSizeArr[0]), int(recoSizeArr[2])*int(reps))

failure, output = commands.getstatusoutput(cmd)

#####################################
#Get the AFNI data into NIFTI format#
#####################################

cmd = "3dAFNItoNIFTI recoed+orig"

failure, output = commands.getstatusoutput(cmd)

###############################
#Get the NIFTI data into here!#
###############################

niftiData = nifti.NiftiImage('recoed')

#########################################
#Create DICOM images from the nifti data#
#########################################


####################################
#Launch an interactive data browser#
####################################

#Functions for when the counters are incremented
def locWidgetChanged():
    myAxisD1.imshow(niftiData.data[sliceWidget.getvalue(),:,:])
    myAxisD2.imshow(niftiData.data[:,rowWidget.getvalue(),:])
    myAxisD3.imshow(niftiData.data[:,:,colWidget.getvalue()])
    print niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()]
    voxValue.set('Current Voxel Value is %g' % niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()])
    canvasD1.show()
    canvasD2.show()
    canvasD3.show()

#Functions for dealing with mouse clicks on the plots
def canvasD1OnClick(event):
    print 'Canvas 1, button %d, x=%d, y=%d, xdata=%d, ydata=%d' % (event.button, event.x, event.y, event.xdata, event.ydata)
    print niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()]
    colWidget.setvalue( int(event.xdata) )
    rowWidget.setentry( int(event.ydata) )
    voxValue.set('Current Voxel Value is %g' % niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()])
    if event.button == 2:
        d1SeedEntry.setvalue( sliceWidget.getvalue() )
        d2SeedEntry.setvalue( rowWidget.getvalue() )
        d3SeedEntry.setvalue( colWidget.getvalue() )
def canvasD2OnClick(event):
    print 'Canvas 2, button %d, x=%d, y=%d, xdata=%d, ydata=%d' % (event.button, event.x, event.y, event.xdata, event.ydata)
    print niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()]
    sliceWidget.setvalue( int(event.ydata) )
    colWidget.setvalue( int(event.xdata) )
    voxValue.set('Current Voxel Value is %g' % niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()])
    if event.button == 2:
        d1SeedEntry.setvalue( sliceWidget.getvalue() )
        d2SeedEntry.setvalue( rowWidget.getvalue() )
        d3SeedEntry.setvalue( colWidget.getvalue() )
def canvasD3OnClick(event):
    print 'Canvas 3, button %d, x=%d, y=%d, xdata=%d, ydata=%d' % (event.button, event.x, event.y, event.xdata, event.ydata)
    print niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()]
    sliceWidget.setvalue( int(event.ydata) )
    rowWidget.setvalue( int(event.xdata) )
    voxValue.set('Current Voxel Value is %g' % niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()])
    if event.button == 2:
        d1SeedEntry.setvalue( sliceWidget.getvalue() )
        d2SeedEntry.setvalue( rowWidget.getvalue() )
        d3SeedEntry.setvalue( colWidget.getvalue() )

#Function for creating the cast
def createCast():
    do26Neighbors=1
    #Initialize the cast data array to zeroes
    castDataSet = niftiData.copy()
    castDataSet.data = castDataSet.data * 0
    #Find the seed values
    seedValue = float(niftiData.data[d1SeedEntry.getvalue(), d2SeedEntry.getvalue(), d3SeedEntry.getvalue()])
    threshValue = float(thresholdEntry.getvalue())
    print 'Seed value: %g, Threshold value: %g' % (seedValue, threshValue)
    #Start the looping
    newPoints = [(d1SeedEntry.getvalue(), d2SeedEntry.getvalue(), d3SeedEntry.getvalue()), ]
    castPoints = []
    newPoints2 = []
    myContinue = 1
    iteration = 0
    while myContinue == 1:
        iteration = iteration+1
        newPoints2 = []
        print 'Iteration #%g' %iteration
        for point in newPoints:
            if do26Neighbors == 1:
                for d1index in range(int(point[0])-1,int(point[0])+2):
                    if d1index >= 0:
                        if d1index <= 1000:
                            for d2index in range(int(point[1])-1,int(point[1])+2):
                                for d3index in range(int(point[2])-1,int(point[2])+2):
                                    testValue = niftiData.data[d1index, d2index, d3index]
                                    castValue = castDataSet.data[d1index, d2index, d3index]
                                    if testValue > threshValue:
                                        if castValue == 0:
                                            castDataSet.data[d1index,d2index,d3index] = 1
                                            newPoints2.append( (d1index, d2index, d3index) )
                                        #End of if (castvalue)
                                    #End of if (testValue)
                                #End of d3 loop
                            #End of d2 loop
                #End of d1 loop
            else: #End of 26 neighbors, now 6 neighbors
                for d1index in range(int(point[0])-1,int(point[0])+2):
                    if d1index > -1: #22:
                        if d1index < 10: #57:
                            d2index = int(point[1])
                            d3index = int(point[2])
                            testValue = niftiData.data[d1index, d2index, d3index]
                            castValue = castDataSet.data[d1index, d2index, d3index]
                            if testValue > threshValue:
                                if castValue == 0:
                                    castDataSet.data[d1index,d2index,d3index] = 1
                                    newPoints2.append( (d1index, d2index, d3index) )
                                #End of if (castvalue)
                            #End of if (testValue)
                #End of d1 for loop
                for d2index in range(int(point[1])-1,int(point[1])+2):
                    d1index = int(point[0])
                    d3index = int(point[2])
                    testValue = niftiData.data[d1index, d2index, d3index]
                    castValue = castDataSet.data[d1index, d2index, d3index]
                    if testValue > threshValue:
                        if castValue == 0:
                            castDataSet.data[d1index,d2index,d3index] = 1
                            newPoints2.append( (d1index, d2index, d3index) )
                        #End of if (castvalue)
                    #End of if (testValue)
                #End of d2 for loop
                for d3index in range(int(point[2])-1,int(point[2])+2):
                    d2index = int(point[1])
                    d1index = int(point[0])
                    testValue = niftiData.data[d1index, d2index, d3index]
                    castValue = castDataSet.data[d1index, d2index, d3index]
                    if testValue > threshValue:
                        if castValue == 0:
                            castDataSet.data[d1index,d2index,d3index] = 1
                            newPoints2.append( (d1index, d2index, d3index) )
                        #End of if (castvalue)
                    #End of if (testValue)
                #End of d3 for loop
            #End of 6 neighbor case
        #End of newPoints loop
        castPoints.extend(newPoints[:])
        newPoints = newPoints2[:]
        print '%g points added to cast' % len(newPoints)
        if len(newPoints) < 1:
            myContinue = 0
    #End of while loop
    #Save the cast data set
    castDataSet.save(filename='Cast', filetype='NIFTI', update_minmax=True)

#def checkSliceWidget(inputValue):
#    print inputValue
#    locWidgetChanged()
#    return Pmw.OK

#The root window
root = Pmw.initialise()
root.wm_title('Cast Creation Tool')
root.geometry("750x750")

#The top level frame
top = tk.Frame(root)
top.pack(side='top')

#The dimension frames
bigFrame1 = tk.Frame(top)
bigFrame1.pack(side='top')

bigFrame2 = tk.Frame(top)
bigFrame2.pack(side='top')

d1Frame = tk.Frame(bigFrame1)
d1Frame.pack(side='left')

d2Frame = tk.Frame(bigFrame1)
d2Frame.pack(side='left')

d3Frame = tk.Frame(bigFrame2)
d3Frame.pack(side='top')

d1AxisFrame = tk.Frame(d1Frame)
d1AxisFrame.pack(side='top')

d1CounterFrame = tk.Frame(d1Frame)
d1CounterFrame.pack(side='top')

d2AxisFrame = tk.Frame(d2Frame)
d2AxisFrame.pack(side='top')

d2CounterFrame = tk.Frame(d2Frame)
d2CounterFrame.pack(side='top')

d3AxisFrame = tk.Frame(d3Frame)
d3AxisFrame.pack(side='top')

d3CounterFrame = tk.Frame(d3Frame)
d3CounterFrame.pack(side='top')

seedFrame = tk.Frame(top)
seedFrame.pack(side='top')

seedPixelLocFrame = tk.Frame(seedFrame)
seedPixelLocFrame.pack(side='left')

seedPixelInfoFrame = tk.Frame(seedFrame)
seedPixelInfoFrame.pack(side='left')

#The figures
plt.gray()

myFigureD1 = Figure(figsize=(3,3), dpi=100,)
myFigureD2 = Figure(figsize=(3,3), dpi=100,)
myFigureD3 = Figure(figsize=(3,3), dpi=100,)

myAxisD1 = myFigureD1.add_subplot(1,1,1,title='Dimension 1')
myAxisD2 = myFigureD2.add_subplot(1,1,1,title='Dimension 2')
myAxisD3 = myFigureD3.add_subplot(1,1,1,title='Dimension 3')

myAxisD1.imshow(niftiData.data[niftiData.data.shape[0]/2,:,:])
myAxisD2.imshow(niftiData.data[:,niftiData.data.shape[1]/2,:])
myAxisD3.imshow(niftiData.data[:,:,niftiData.data.shape[2]/2])

#The canvas
canvasD1 = FigureCanvasTkAgg(myFigureD1, master=d1AxisFrame)
canvasD2 = FigureCanvasTkAgg(myFigureD2, master=d2AxisFrame)
canvasD3 = FigureCanvasTkAgg(myFigureD3, master=d3AxisFrame)

canvasD1.show()
canvasD2.show()
canvasD3.show()

canvasD1.get_tk_widget().pack(side='left', fill='both', expand=1)
canvasD2.get_tk_widget().pack(side='left', fill='both', expand=1)
canvasD3.get_tk_widget().pack(side='left', fill='both', expand=1)

canvasD1.mpl_connect('button_press_event',canvasD1OnClick)
canvasD2.mpl_connect('button_press_event',canvasD2OnClick)
canvasD3.mpl_connect('button_press_event',canvasD3OnClick)

#The buttons
sliceWidget = Pmw.Counter(d1CounterFrame,
                          labelpos = 'w',
                          label_text = 'Dimension 1',
                          entryfield_value = niftiData.data.shape[0]/2,
                          datatype = 'numeric',
                          entryfield_validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.data.shape[0]-1},
                          entryfield_command = locWidgetChanged,
                          entryfield_modifiedcommand = locWidgetChanged)
sliceWidget.pack(side='top');

rowWidget = Pmw.Counter(d2CounterFrame,
                        labelpos = 'w',
                        label_text = 'Dimension 2',
                        entryfield_value = niftiData.data.shape[1]/2,
                        datatype = 'numeric',
                        entryfield_validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.data.shape[1]-1},
                        entryfield_command = locWidgetChanged,
                        entryfield_modifiedcommand = locWidgetChanged)
rowWidget.pack(side='top');

colWidget = Pmw.Counter(d3CounterFrame,
                        labelpos = 'w',
                        label_text = 'Dimension 3',
                        entryfield_value = niftiData.data.shape[2]/2,
                        datatype = 'numeric',
                        entryfield_validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.data.shape[2]-1},
                        entryfield_command = locWidgetChanged,
                        entryfield_modifiedcommand = locWidgetChanged)
colWidget.pack(side='top')

#The seed pixel
d1SeedEntry = Pmw.EntryField(seedPixelLocFrame,
                             labelpos = 'w',
                             label_text = 'Seed Dimension 1',
                             value = niftiData.data.shape[0]/2,
                             validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.data.shape[0]-1})
d1SeedEntry.pack(side='top')

d2SeedEntry = Pmw.EntryField(seedPixelLocFrame,
                             labelpos = 'w',
                             label_text = 'Seed Dimension 2',
                             value = niftiData.data.shape[1]/2,
                             validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.data.shape[1]-1})
d2SeedEntry.pack(side='top')

d3SeedEntry = Pmw.EntryField(seedPixelLocFrame,
                             labelpos = 'w',
                             label_text = 'Seed Dimension 3',
                             value = niftiData.data.shape[2]/2,
                             validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.data.shape[2]-1})
d3SeedEntry.pack(side='top')

#The pixel value
voxValue = tk.StringVar()
voxValue.set('Current Voxel Value is %d' % niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()])

voxValueLabel = tk.Label(seedPixelInfoFrame, textvariable=voxValue, width=30)
voxValueLabel.pack(side='top')

#The threshold
thresholdEntry = Pmw.EntryField(seedPixelInfoFrame,
                                labelpos = 'w',
                                label_text = 'Cast intensity cutoff',
                                value = niftiData.data[sliceWidget.getvalue(), rowWidget.getvalue(), colWidget.getvalue()],
                                validate = {'validator' : 'numeric', 'min' : 0, 'max' : 50000})
thresholdEntry.pack(side='top')

#The cast creation button
createMaskButton = tk.Button(seedPixelInfoFrame, text="Generate Cast", command=createCast)
createMaskButton.pack(side='top')

#Run the GUI
root.mainloop()
