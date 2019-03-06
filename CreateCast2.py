#! /usr/bin/env python3

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
import tkinter as tk
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


###########################
# Bring in the NIFTI file #
###########################
niftiName = '18991230_000000Lql75ocUVupuu0WhLMhPASevVs002a1001.nii.gz'
niftiFile = nibabel.load(niftiName)

###############################
#Get the NIFTI data into here!#
###############################

niftiData = niftiFile.get_data()
castDataSet = niftiData * 0.0

#########################################
#Create DICOM images from the nifti data#
#########################################


####################################
#Launch an interactive data browser#
####################################

#Nencka solution for fixing the whole asnToInt(float(str( thing
def asnToInt(x):
    return int(float(str(x)))

#Functions for when the counters are incremented
def locWidgetChanged():
    masked = numpy.ma.masked_where(castDataSet==0,castDataSet)
    myAxisD1.imshow(niftiData[asnToInt(sliceWidget.getvalue()),:,:])
    myAxisD1.imshow(masked[asnToInt(sliceWidget.getvalue()),:,:],'jet',alpha=0.7)
    myAxisD2.imshow(niftiData[:,asnToInt(rowWidget.getvalue()),:])
    myAxisD2.imshow(masked[:,asnToInt(rowWidget.getvalue()),:],'jet',alpha=0.7)
    myAxisD3.imshow(niftiData[:,:,asnToInt(colWidget.getvalue())])
    myAxisD3.imshow(masked[:,:,asnToInt(colWidget.getvalue())],'jet',alpha=0.7)
    print(niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    voxValue.set('Current Voxel Value is %g' % niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    canvasD1.show()
    canvasD2.show()
    canvasD3.show()

#Functions for dealing with mouse clicks on the plots
def canvasD1OnClick(event):
    print('Canvas 1, button %d, x=%d, y=%d, xdata=%d, ydata=%d' % (event.button, event.x, event.y, event.xdata, event.ydata))
    print(niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    colWidget.setvalue( asnToInt(event.xdata) )
    rowWidget.setentry( asnToInt(event.ydata) )
    voxValue.set('Current Voxel Value is %g' % niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    if event.button == 2:
        d1SeedEntry.setvalue( asnToInt(sliceWidget.getvalue() ))
        d2SeedEntry.setvalue( asnToInt(rowWidget.getvalue() ))
        d3SeedEntry.setvalue( asnToInt(colWidget.getvalue() ))
def canvasD2OnClick(event):
    print('Canvas 2, button %d, x=%d, y=%d, xdata=%d, ydata=%d' % (event.button, event.x, event.y, event.xdata, event.ydata))
    print(niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    sliceWidget.setvalue( asnToInt(event.ydata) )
    colWidget.setvalue( asnToInt(event.xdata) )
    voxValue.set('Current Voxel Value is %g' % niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    if event.button == 2:
        d1SeedEntry.setvalue( asnToInt(sliceWidget.getvalue()) )
        d2SeedEntry.setvalue( asnToInt(rowWidget.getvalue()) )
        d3SeedEntry.setvalue( asnToInt(colWidget.getvalue() ))
def canvasD3OnClick(event):
    print('Canvas 3, button %d, x=%d, y=%d, xdata=%d, ydata=%d' % (event.button, event.x, event.y, event.xdata, event.ydata))
    print(niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    sliceWidget.setvalue( asnToInt(event.ydata) )
    rowWidget.setvalue( asnToInt(event.xdata) )
    voxValue.set('Current Voxel Value is %g' % niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])
    if event.button == 2:
        d1SeedEntry.setvalue( asnToInt(sliceWidget.getvalue() ))
        d2SeedEntry.setvalue( asnToInt(rowWidget.getvalue() ))
        d3SeedEntry.setvalue( asnToInt(colWidget.getvalue() ))

#Function for creating the cast
def createCast():
    do26Neighbors=1
    #Initialize the cast data array to zeroes
    #castDataSet = niftiData.copy()
    #castDataSet = castDataSet * 0
    #Find the seed values
    seedValue = float(niftiData[asnToInt(d1SeedEntry.getvalue()), asnToInt(d2SeedEntry.getvalue()), asnToInt(d3SeedEntry.getvalue())])
    threshValue = float(thresholdEntry.getvalue())
    print('Seed value: %g, Threshold value: %g' % (seedValue, threshValue))
    #Start the looping
    newPoints = [(asnToInt(d1SeedEntry.getvalue()), asnToInt(d2SeedEntry.getvalue()), asnToInt(d3SeedEntry.getvalue())), ]
    castPoints = []
    newPoints2 = []
    myContinue = 1
    iteration = 0
    origThresh = seedValue * 0.75
    while myContinue == 1:
        iteration = iteration+1
        newPoints2 = []
        print('Iteration #%g' %iteration)
        for point in newPoints:
            thisThresh = 0.975*float(niftiData[point[0],point[1],point[2]])
            if do26Neighbors == 1:
                for d1index in range(asnToInt(point[0])-1,asnToInt(point[0])+2):
                    if d1index >= 0:
                        if d1index <= 1000:
                            for d2index in range(asnToInt(point[1])-1,asnToInt(point[1])+2):
                                for d3index in range(asnToInt(point[2])-1,asnToInt(point[2])+2):
                                    testValue = niftiData[d1index, d2index, d3index]
                                    castValue = castDataSet[d1index, d2index, d3index]
                                    if ((testValue > thisThresh) or (testValue > threshValue)) and (testValue > origThresh): #threshValue:
                                        if castValue == 0:
                                            castDataSet[d1index,d2index,d3index] = 1
                                            newPoints2.append( (d1index, d2index, d3index) )
                                        #End of if (castvalue)
                                    #End of if (testValue)
                                #End of d3 loop
                            #End of d2 loop
                #End of d1 loop
            else: #End of 26 neighbors, now 6 neighbors
                for d1index in range(asnToInt(point[0])-1,asnToInt(point[0])+2):
                    if d1index > -1: #22:
                        if d1index < 10: #57:
                            d2index = asnToInt(point[1])
                            d3index = asnToInt(point[2])
                            testValue = niftiData[d1index, d2index, d3index]
                            castValue = castDataSet[d1index, d2index, d3index]
                            if testValue > threshValue:
                                if castValue == 0:
                                    castDataSet[d1index,d2index,d3index] = 1
                                    newPoints2.append( (d1index, d2index, d3index) )
                                #End of if (castvalue)
                            #End of if (testValue)
                #End of d1 for loop
                for d2index in range(asnToInt(point[1])-1,asnToInt(point[1])+2):
                    d1index = asnToInt(point[0])
                    d3index = asnToInt(point[2])
                    testValue = niftiData[d1index, d2index, d3index]
                    castValue = castDataSet[d1index, d2index, d3index]
                    if testValue > threshValue:
                        if castValue == 0:
                            castDataSet[d1index,d2index,d3index] = 1
                            newPoints2.append( (d1index, d2index, d3index) )
                        #End of if (castvalue)
                    #End of if (testValue)
                #End of d2 for loop
                for d3index in range(asnToInt(point[2])-1,asnToInt(point[2])+2):
                    d2index = asnToInt(point[1])
                    d1index = asnToInt(point[0])
                    testValue = niftiData[d1index, d2index, d3index]
                    castValue = castDataSet[d1index, d2index, d3index]
                    if testValue > threshValue:
                        if castValue == 0:
                            castDataSet[d1index,d2index,d3index] = 1
                            newPoints2.append( (d1index, d2index, d3index) )
                        #End of if (castvalue)
                    #End of if (testValue)
                #End of d3 for loop
            #End of 6 neighbor case
        #End of newPoints loop
        castPoints.extend(newPoints[:])
        newPoints = newPoints2[:]
        print('%g points added to cast' % len(newPoints))
        if (len(newPoints) < 1) or (iteration>200) or (len(newPoints)>1500):
            myContinue = 0
    #End of while loop
    #Save the cast data set
    #numpy.save('myCast',castDataSet)
    newNifti = nibabel.nifti1.Nifti1Image(castDataSet,niftiFile.affine,niftiFile.header)
    nibabel.save(newNifti,'GeneratedCast.nii.gz')
    #castDataSet.save(filename='Cast', filetype='NIFTI', update_minmax=True)

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

myAxisD1.imshow(niftiData[asnToInt(niftiData.shape[0]/2),:,:])
myAxisD2.imshow(niftiData[:,asnToInt(niftiData.shape[1]/2),:])
myAxisD3.imshow(niftiData[:,:,asnToInt(niftiData.shape[2]/2)])

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
                          entryfield_value = niftiData.shape[0]/2,
                          datatype = 'numeric',
                          entryfield_validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.shape[0]-1},
                          entryfield_command = locWidgetChanged,
                          entryfield_modifiedcommand = locWidgetChanged)
sliceWidget.pack(side='top');

rowWidget = Pmw.Counter(d2CounterFrame,
                        labelpos = 'w',
                        label_text = 'Dimension 2',
                        entryfield_value = niftiData.shape[1]/2,
                        datatype = 'numeric',
                        entryfield_validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.shape[1]-1},
                        entryfield_command = locWidgetChanged,
                        entryfield_modifiedcommand = locWidgetChanged)
rowWidget.pack(side='top');

colWidget = Pmw.Counter(d3CounterFrame,
                        labelpos = 'w',
                        label_text = 'Dimension 3',
                        entryfield_value = niftiData.shape[2]/2,
                        datatype = 'numeric',
                        entryfield_validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.shape[2]-1},
                        entryfield_command = locWidgetChanged,
                        entryfield_modifiedcommand = locWidgetChanged)
colWidget.pack(side='top')

#The seed pixel
d1SeedEntry = Pmw.EntryField(seedPixelLocFrame,
                             labelpos = 'w',
                             label_text = 'Seed Dimension 1',
                             value = niftiData.shape[0]/2,
                             validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.shape[0]-1})
d1SeedEntry.pack(side='top')

d2SeedEntry = Pmw.EntryField(seedPixelLocFrame,
                             labelpos = 'w',
                             label_text = 'Seed Dimension 2',
                             value = niftiData.shape[1]/2,
                             validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.shape[1]-1})
d2SeedEntry.pack(side='top')

d3SeedEntry = Pmw.EntryField(seedPixelLocFrame,
                             labelpos = 'w',
                             label_text = 'Seed Dimension 3',
                             value = niftiData.shape[2]/2,
                             validate = {'validator' : 'numeric', 'min' : 0, 'max' : niftiData.shape[2]-1})
d3SeedEntry.pack(side='top')

#The pixel value
voxValue = tk.StringVar()
voxValue.set('Current Voxel Value is %d' % niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())])

voxValueLabel = tk.Label(seedPixelInfoFrame, textvariable=voxValue, width=30)
voxValueLabel.pack(side='top')

#The threshold
thresholdEntry = Pmw.EntryField(seedPixelInfoFrame,
                                labelpos = 'w',
                                label_text = 'Cast intensity cutoff',
                                value = niftiData[asnToInt(sliceWidget.getvalue()), asnToInt(rowWidget.getvalue()), asnToInt(colWidget.getvalue())],
                                validate = {'validator' : 'numeric', 'min' : 0, 'max' : 50000})
thresholdEntry.pack(side='top')

#The cast creation button
createMaskButton = tk.Button(seedPixelInfoFrame, text="Generate Cast", command=createCast)
createMaskButton.pack(side='top')

#Run the GUI
root.mainloop()
