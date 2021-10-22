"""
This demo demonstrates how to embed a matplotlib (mpl) plot 
into a PyQt4 GUI application, including:

* Using the navigation toolbar
* Adding data to the plot
* Dynamically modifying the plot's properties
* Processing mpl events
* Saving the plot to a file from a menu

The main goal is to serve as a basis for developing rich PyQt GUI
applications featuring mpl plots (using the mpl OO API).

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 19.01.2009
"""
import sys
sys.path.append("C:\\Users\\jbcorli\\Anaconda3\\Scripts_import\\")
#   *******
#import window_fromspec as windo

import astroscrappy as cosmics
import sys, os, random
#from astropy.io.fits import getdata
import pyfits
import numpy
import matplotlib.cm as cm
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import *#QApplication, QMainWindow, QLabel
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, pyqtSignal
#   *******
#import pyspeckit

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
#from matplotlib.figure import Figure
from matplotlib.widgets import Slider, Button
from pylab import axes, ylim
from PIL import Image
import scipy
from scipy import ndimage, fftpack
import pickle as cp
from PyQt5.QtWidgets import QAction
#import cosmics3_5
from astroscrappy import detect_cosmics
#import mpfitexpr
#data =pyfits.getdata('ffdf.fits')
data2=numpy.arange(1)
data3=numpy.array( [(0,0),(0,0)])
rows_s=[]   
#tmplist=list(windo.window_names.keys())
#tmplist = QStringList(windo.window_names.keys())
cnt =0
plt.ion()
#import congrid

class Main(QMainWindow):
    slotin = pyqtSignal()
    def __init__(self, parent = None):
        super(Main, self).__init__(parent)
        #super(QMainWindow, self).__init__(self, parent)
        self.create_datadict()
        self.setWindowTitle('SHS DATA REDUCTION')

        self.create_menu()

        self.create_status_bar()
        #self.try_me()
        self.create_fig_frame()
        self.create_main_frame()
        self.textbox.setText('1 2 3 4')
        #self.on_draw()
        
##############################################################################

    def create_main_frame(self): 
        self.mainLayout = QGridLayout()
        self.addButton = QPushButton('Load Interferogram')
        self.addButton.clicked.connect(self.QfileDialog4)
        self.addButton2 = QPushButton('Load Bias')
        self.addButton2.clicked.connect( self.QfileDialog4)
        self.addButton3 = QPushButton('Load Flat')
        self.addButton3.clicked.connect(self.QfileDialog4)
        self.menu =  QComboBox()
        #self.menu.addItems(tmplist)#'Hanning None'.split())
        self.menu.setCurrentIndex(3)
        #self.menu.
        
        #self.addButton5 = QPushButton('Pad')
        #self.addButton5.clicked.connect( self.padit)
        
        self.lcd = QLCDNumber(self)
        #self.lcd.setStyle
        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setRange(0,4)
       
        self.addButton5 = QPushButton('APPLY FFT')
        self.addButton5.clicked.connect( self.proces2)
        
        #   Bias, flat field, hanning window, and padding checkboxs/functions
        self.checkBox1 = QCheckBox("Apply")
        self.checkBox2 = QCheckBox("Apply")
        self.checkBox3 = QCheckBox("Apply H")
        self.checkBox4 = QCheckBox("Apply Pad")
        self.label1 = QLabel("Choose your Window")
        self.labelpad = QLabel(" Padding")
        self.checkBox3.stateChanged.connect( self.gen_process)
        self.menu.currentIndexChanged.connect(self.gen_process)
        self.checkBox4.stateChanged.connect(self.gen_process)
        
        #   Sets the slider to change the slider display val when slider changes
        self.sld.valueChanged.connect(self.lcd.display)
        #   Checkboxs, fft button, slider, and drop down list start out unclickable
        self.checkBox1.setEnabled(False)
        self.checkBox2.setEnabled(False)        
        self.checkBox3.setEnabled(False)
        self.checkBox4.setEnabled(False)
        self.addButton5.setEnabled(False)
        self.sld.setEnabled(False)
        self.menu.setEnabled(False)
        
        #self.mainLayout.setRowStretch(4,2)
        #self.mainLayout.setRowStretch(5,2)
        # add all main to the main vLayout
        self.mainLayout.addWidget(self.addButton, 0, 0)
        self.mainLayout.addWidget(self.checkBox1, 1, 2) 
        self.mainLayout.addWidget(self.addButton2, 1, 0)
        self.mainLayout.addWidget(self.checkBox2, 2, 2) 
        self.mainLayout.addWidget(self.addButton3, 2, 0)
        self.mainLayout.addWidget(self.menu, 3, 0)
        self.mainLayout.addWidget(self.checkBox3, 3, 2) 
        self.mainLayout.addWidget(self.checkBox4, 4, 2, 1, 1) 
        #self.mainLayout.addWidget(self.addButton5, 4, 0, 1, 1)
        self.mainLayout.addWidget(self.lcd, 4, 1, 1, 1)
        self.mainLayout.addWidget(self.sld, 4, 0, 1, 1)
        self.mainLayout.addWidget(self.addButton5, 7, 0, 1, 3)
        self.mainLayout.addWidget(self.scrollArea, 8, 0, 2, 3)
        self.mainLayout.addWidget(self.label1,3,1)
        
        self.mainLayout.addWidget(self.lcd, 4, 1, 1, 1)
        self.mainLayout.addWidget(self.sld, 4, 0, 1, 1)
        self.mainLayout.addWidget(self.labelpad,4,1,1,1)
        # central widget
        self.mainLayout.addWidget(self.mpl_toolbar, 10, 0, 1, 3)

        # set central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)

        # set central widget
        self.setCentralWidget(self.centralWidget)

    ##############################################################################

    def create_fig_frame(self):
        self.scrollLayout = QGridLayout()

        # scroll area widget contents
        self.scrollWidget = QWidget()
  
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = plt.Figure( dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.scrollWidget )
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        #self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.scrollWidget)
        
        # Other GUI controls
        # 
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.textbox.editingFinished.connect(self.on_draw)
        #self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
        
        self.draw_button = QPushButton("&Draw")
        self.draw_button.clicked.connect(self.on_draw)
        #self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged[int].connect(self.on_draw)
        #self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.valueChanged[int].connect(self.on_draw)
        #self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)

        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
   #     nnWidget = QWidget()
    #    nnWidget.setLayout(hbox)
        for w in [  self.textbox, self.draw_button, self.grid_cb,
                    slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
                # scroll area
        self.scrollLayout.addWidget(self.canvas, 1, 0, 3, 1)
        
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(False)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.scrollWidget)
  
        #self.scrollLayout.addWidget(self.mpl_toolbar, 1, 0)
 #scrollLayout)
                # scroll area

    ############################################################################## 

    def create_status_bar(self):
        self.status_text = QLabel("This is SHS REDUCE")
        self.statusBar().addWidget(self.status_text, 1)
        
    ##############################################################################
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))
        
    ##############################################################################
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    
    ##############################################################################
    
    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
            
    ##############################################################################

    def create_action(self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
            
            #self.slotin.connect(action,slot)
           # self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    
    ##############################################################################
    
    def create_datadict(self):
        #   data_dict is a dictionary containing all the images data from the OG fits, flats, padded image, etc
        self.data_dict={'NAME':['Original_Data','data_bias','data_flat','data_window','data_pad','data_final','data_spec','data_process'],
                  'USE':[False, False, False,False,False,False,False,False],
                  'DATA':[0,0,0,0,0,0,0,0]
                  }

#        for ind,x in enumerate(self.data_dict['USE']):
#            if x==True:print "I am", x, "at " , ind

    ##############################################################################

    def on_draw(self):
        """ Redraws the figure
        """
        textbox_text = str(self.textbox.text())
        self.data = list(map(int, textbox_text.split()))
        
        x = list(range(len(self.data)))

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.bar(
            left=x, 
            height=self.data, 
            width=self.slider.value() / 100.0, 
            align='center', 
            alpha=0.44,
            picker=5)
        self.axes
        self.canvas.draw()

    ##############################################################################    

    def on_draw2(self):
        """ Redraws the figure"""
        subplot_tot=sum(x > 0 for x in self.data_dict['USE'])
        #ax5 = self.fig.add_subplot(subplot_tot,1,1)
        subplot_num=1
        self.fig.clf()
        self.scrollWidget.resize(600,500*subplot_tot)
        #self.fig.set_figheight(12)

        #self.scrollLayout.addWidget(self.canvas, 0, 0, 3, 6)
        for ind,x in enumerate(self.data_dict['USE']):
            if x==True:
                cur_ax=str(self.data_dict['NAME'][ind])
                cur_ax=self.fig.add_subplot(subplot_tot,1,subplot_num)
                cur_ax.clear()
                #cur_data=self.data_dict['DATA'][ind]

                bb=cur_ax.imshow(self.data_dict['DATA'][ind],cmap = cm.Greys_r)#,cmap = cm.Greys_r,vmin=0, vmax=1, picker=6)
                subplot_num+=1

        # clear the axes and redraw the plot anew
        #
        #ax5 = self.fig.add_subplot(111)
        #ax5.clear()   
        #bb=ax5.imshow(datan,cmap = cm.Greys_r)#,cmap = cm.Greys_r,vmin=0, vmax=1, picker=6)
        
        #ax.invert_yaxis()
        #ax2 = fig.add_subplot(222)
        #self.axes.clear()        
        #self.canvas.resize(20,20)
        
        
        #self.scrollArea.resize(500,1000)
        #self.scrollWidget.adjustSize()
        #self.scrollArea.adjustSize()
        self.canvas.draw()
        
        #self.scrollLayout.update()
    
    #use below to load zemax detewctor file in txt format
    
    ##############################################################################
    
    def QfileDialog3(self):
        file_name = QFileDialog.getOpenFileName(None, "Open Data File", r"D:\papers\6300_SHS\zemax_models\pupil_size\new2\smaller_f\detector_dist\new_fcs", "TXT ZEMAX files (*.TXT)")
        interf = zem_inter(str(file_name))        
        global data2        
        folder = r"D:\papers\6300_SHS\zemax_models"
        os.chdir(folder)
        #data2 = ndimage.rotate(interf,90)
        data2=interf
        print  ("HERERRRRR")
        self.addButton5.setEnabled(True)
        self.sld.setEnabled(True)
        self.menu.setEnabled(True)
        self.checkBox4.setEnabled(True)
        self.checkBox3.setEnabled(True)
        #plt.imshow(data2)

        self.data_dict['USE'][0]=True
        self.data_dict['DATA'][0]=data2
        #gg=self.data_dict.iterkeys
        self.gen_process()
        self.on_draw2()
        
    ##############################################################################
        
    def QfileDialog4_old(self):
        bias_fname = QFileDialog.getOpenFileName(None, "Open Data File", r"D:\papers", "FITS data files (*.fits)")         
        print(( pyfits.info(str(bias_fname))   )) 
        data_bias=pyfits.getdata(str(bias_fname))
        data_bias2 = ndimage.rotate(data_bias,90)
        plt.ion()
        plt.imshow(data_bias2)
        self.checkBox1.setEnabled(True)
        self.data_dict['data_bias'] = {True:data_bias2}

    ##############################################################################

    def QfileDialog4(self):
        ''' Opens a fits file and applies cosmic filter, puts it in the data_dict and shows it on the GUI '''
        #data2_fname = QFileDialog.getOpenFileName(None, "Open Data File", r"D:\papers", "FITS data files (*.fits)")      
        file_filter = 'Data File (*.fits *.fit *.dat);; Excel File (*.xlsx *.xls)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a data file',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='Fits File (*.fits *.fit)'
        )
        print(response[0])
        print ("HELP")
        #return response[0]
        
        #   Fits file name
        data2_fname=response[0]
        
        #data2_fname = QFileDialog.getOpenFileName(self, 'Open Image', 'D:\papers', 'Image Files (*.fits *.fit )')
       #data2_fname = QFileDialog.getOpenFileName(self, tr("Open Image"), "D:\papers", tr("Image Files (*.png *.jpg *.bmp)"))
        
        #data2_fname= QFileDialog.getOpenFileName(None,tr("Open Image"), "/home/jana", tr("Image Files (*.png *.jpg *.bmp)"));
        #print((pyfits.info(str(data2_fname)))) 
        print (data2_fname)
        
        #   HDU list, consists of header and data array
        hdul = pyfits.open(str(data2_fname))
        
        #print((pyfits.info.
        global data2    
        
        #   Gets raw image data array from HDU
        data2 = pyfits.getdata(data2_fname)
        
        #data2=pyfits.open(data2_fname)
        data1=data2
        
        #pyfits.
        #pyfits.getdata('ff.fits')
        
        print((data1.shape))
        nx,ny = data1.shape
        print((nx,ny))
        
        #ddf=pyfits.
        #datan2=data1[0,:]
        #data2=(data1[0,:,:])
        
        print((data2.shape))
        
        #data3 = ndimage.rotate(data2,90)
        
        #   Rotate image array
        data3 = ndimage.rotate(data2,0)   
        
        #data2=data3[0:2000,1500:3500]
        #data3 = ndimage.rotate(data2,-14) 
        #data3 = ndimage.rotate(data3,90)
        
        #   *******
        #data2=data3[400:750,100:950]
        data2=data3
        
        print((data2.shape))
        #data4=rebin(data2,850,850)
        #data2=data4
        #data2=congrid(data2, (850,850), method='linear', centre=False, minusone=False)
        #data2=data3[70:175,30:200]
        #data2=data3[0:200,0:240]
        #c = cosmics.cosmicsimage(data2, gain=2.2, readnoise=10.0, sigclip = 5.0, sigfrac = 0.3, objlim = 5.0)
        
        #   Applying cosmics filter to data2
        mask,c = detect_cosmics(data2 , inmask=None , sigclip = 5.0 ,sigfrac = 0.3,objlim = 5.0, readnoise=10.0,
                                gain=2.2, satlevel =65536, niter=4 , cleantype='meanmask' , fsmode='median',sepmed=True,
                                psfmodel='gauss', psffwhm =2.5,psfsize =7)
                                             
                                            #  p s s l =0.0 , n i t e r =4, sepmed=True ,
                                             #  cl e a n t y p e =’meanmask , fsmode=’median ’ ,
                                              # p sfmodel =’ gauss ’ , psffwhm =2.5 ,
                                              # p s f s i z e =7,
                                               #p sf k=None , p sf b e t a =4.765 , v e r bo s e=Fal s e )
        # There are other options, check the manual...

        # Run the full artillery :
        #c.run(maxiter =2)
        #data2=c.cleanarray
        
        #   data2 now filtered cosmics image
        data2=c
        #   Subtract its min value from all values
        data2=data2-numpy.min(data2)
        
#        img_sm = scipy.signal.medfilt(data2, 5)
 #       bad = numpy.abs(data2 - img_sm) / sigma > 8.0
#        img_cr = data2.copy()
 #       img_cr[bad] = img_sm[bad]
        print ("HELLO")
        
        #   FFT button, slider for padding, drop down menu, hanning checkbox, pad checkbox enabled
        self.addButton5.setEnabled(True)
        self.sld.setEnabled(True)
        self.menu.setEnabled(True)
        self.checkBox4.setEnabled(True)
        self.checkBox3.setEnabled(True)
        
        #   Display cosmics image
        plt.imshow(data2,cmap = cm.Greys_r,vmin=0, vmax=1)
        
        print (data2.shape)
        
        #   Sets the boolean value and cosmic image to the 'Original Data' in the image dictionary
        self.data_dict['USE'][0]=True
        self.data_dict['DATA'][0]=data2
        #gg=self.data_dict.iterkeys
        
        #   Re-draw figure
        self.on_draw2()
        
    ##############################################################################
        
    def gen_process(self):   
        #### Inteferogram loaded as data2
        
        global data3
        #   data3 should be rotated filtered cosmic image
        data3=data2
        
        print (data2.shape)
        rowpl=1  
        print ("did it")
        
        #   If bias box checked, subtract bias
        if self.checkBox1.isChecked():
            data3=data2 - data_bias #-data_bias2
        else:
            pass
        
        #   If flat box checked, divide the image by it
        if self.checkBox2.isChecked():
            data3=data2/data_flat2
            
        #   If hanning window box checked
        if self.checkBox3.isChecked():
            data3 = data2*window2d(self,*data2.shape)   
            #   Set hanning window in data dictionary
            self.data_dict['USE'][3]=True
            self.data_dict['DATA'][3]=data3
        #gg=self.data_dict.iterkeys
            rowpl=rowpl+1
        else:
            self.data_dict['USE'][3]=False
            
        #   If the padding window box checked
        if self.checkBox4.isChecked():
            padn = self.lcd.value()
            h, w = data3.shape
            px1, px2 = round(padn*w/2), round(padn*w/2)
            py1, py2 = round(padn*h/2),round(padn*h/2)
            #   Pads the array
            data3 = numpy.pad(data3,((px1,px2),(py1,py2)),'constant')
            print(('padded by a factor of: ', padn))
            rowpl=rowpl+1
            self.checkBox3.setEnabled(False)
            self.sld.setEnabled(False)
            #   Sets padded image in the data dictionary
            self.data_dict['USE'][4]=True
            self.data_dict['DATA'][4]=data3
        #gg=self.data_dict.iterkeys
        else:
            self.sld.setEnabled(True)
            self.checkBox3.setEnabled(True)           
            self.data_dict['USE'][4]=False
        
        self.on_draw2()    
        #plt.clf()
        #plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        #   Set min and max but multiply min by 0.1
        vmax_in=numpy.max(data3)
        vmin_in=numpy.min(data3)*0.1
        
        plt.axis('off')
        plt.tight_layout()            
            #plt.axis([0, 20, 0, 20])
        ax.imshow(data3,cmap = cm.Greys_r,vmin=vmin_in, vmax=vmax_in)
        ax.set_frame_on(False)
        ax.set_xticks([]); ax.set_yticks([])
        plt.show()
       #        ax.imshow(data3,cmap = cm.Greys_r,vmin=vmin_in, vmax=vmax_in)
        plt.savefig('th_ar_test.svg', bbox_inches='tight',format='svg', dpi=1000, transparent=True,pad_inches=0)
        
 #       print vmax_in
  #      ax.imshow(data3,cmap = cm.Greys_r,vmin=vmin_in, vmax=vmax_in)
        #plt.savefig("th_ar_test.eps", format='eps', dpi=1000, bbox_inches='tight',transparent=True,pad_inches=0)
        #fign=plt.imshow(data3,cmap = cm.Greys_r,vmin=vmin_in, vmax=vmax_in)
        #, format='eps', dpi=1000
        #fig.
        #
        
    ##############################################################################    
    
    def proces(self):
        if data2.any():
            
            h, w = data2.shape
            r = numpy.arange(w, dtype='float64')
            t = numpy.arange(w, dtype='float64')
            t.fill(1)
            #print r.shape 
            #print t.shape 
            zp_image = data2*(-1)**(r+t) 
            pwr_sp=do_fft(zp_image)
            plt.ion()
            plt.imshow(abs(pwr_sp),cmap = cm.Greys_r,vmin=0, vmax=1)
            
    ##############################################################################
            
    def proces2(self):
        '''Function that runs when you apply fft'''
        #   data3 is image with cosmics filter/padding/debias/flats applied
        if data3.any():
            #   data2 just image with cosmics filter
            print((data2.shape))
            
            #   Transform filtered image
            F1=  do_fft(data3)
            F2 = fftpack.fftshift( F1 )
            #   'pwr_sp' is the transform image with filter/padding/debias/flats
            pwr_sp = (numpy.abs( F2 )**2)
            
            #pwr_sp = (numpy.abs( F2 )**2)
            plt.ion()
            fig2=plt.figure()
            ax = fig2.add_subplot(221)
            maxv=numpy.max(numpy.log10(pwr_sp))#pwr_sp)
            #maxv=3.0e7
            minv=numpy.min(numpy.log10(pwr_sp))

            ###PLOT POWER            
            fig = plt.figure()
            ax = fig.add_subplot(111)

            plt.axis('off')
            plt.tight_layout()            
            #plt.axis([0, 20, 0, 20])
            
            #   Shows transform
            ax.imshow((numpy.log10(pwr_sp)),cmap = cm.Greys_r,vmin=minv, vmax=maxv)
            ax.set_frame_on(False)
            ax.set_xticks([]); ax.set_yticks([])
            
            #plt.show()
            #ax.imshow(data3,cmap = cm.Greys_r,vmin=vmin_in, vmax=vmax_in)
            #plt.savefig('th_ar_pwr_test.svg', bbox_inches='tight',format='svg', dpi=1000, transparent=True,pad_inches=0)              
            ###END PLOT POWER     
            
            #bb=ax.imshow((numpy.log10(pwr_sp)),cmap = cm.Greys_r,vmin=minv, vmax=maxv/.8, picker=True)
            ax.invert_yaxis()
            
            ax2 = fig2.add_subplot(222)

            print(("The Min is", minv))
            print(("The max is",maxv))
            
            #   Transform axis
            axcolor = 'lightgoldenrodyellow'
            axfreq = plt.axes([0.1, 0.01, 0.8, 0.04], facecolor=axcolor)
            sfreq = Slider(axfreq, 'y_max', minv/.9, maxv/.9, valinit=maxv) 

            #   Unsure if these are meant to be used axis'
            ax3 = fig2.add_subplot(223)
            ax4 = fig2.add_subplot(224)
            ax3.set_title('Selected Rows')
            ax4.set_title('Summed Spectrum')
            
            #   *******
            #plt.show()
            
            #-----------------------------------------------------------------------------
            
            def update(val):
    
               freq = sfreq.val
               print((sfreq.val))
               ax2.set_ylim([-.1*maxv,sfreq.val])
               ax3.set_ylim([(-.1*maxv),sfreq.val])
               ax3.set_title('Selected Rows')
               plt.draw()
               
            #-----------------------------------------------------------------------------
               
            sfreq.on_changed(update)
            
            #-----------------------------------------------------------------------------

            def onmotion(event2):
                  if event2.inaxes == bb.axes:
                     print((round(event2.xdata), round(event2.ydata) ))
                     #curax = event2.inaxes
                     ax2.cla()
                     ax2.set_ylim([-.05*maxv,sfreq.val])
                     
                     ax2.plot(pwr_sp[round(event2.ydata),:])
                     plt.draw()
                     
            #-----------------------------------------------------------------------------
   
            #ax3.plot(pwr_sp[round(2),:])
            #plt.draw()
            #plt.ion()
            
            #-----------------------------------------------------------------------------
            
            def on_key2(event3):
                #print('you pressed', event.key, event.xdata, event.ydata)
                global rows_s
                if event3.inaxes == bb.axes:
                                        
                    if event3.key == ' ':
                      #print "HIIIIIIIIIIIIIII", round(event3.ydata)
                      row_sel=numpy.rint(event3.ydata)
                      row_sel=row_sel.astype(int)
                      #print "HIII", row_sel
                      #rows_s=[91,92,93]
                      ax3.cla()
                      ax3.set_ylim([(-.05*maxv),sfreq.val])
                      ax3.set_title('Selected Rows')

                      if row_sel in rows_s:
                          i = rows_s.index(row_sel)
                          rows_s.pop(rows_s.index(row_sel))       
                      else:
                          rows_s.append(row_sel)
                                           
                      for i in rows_s:
                          ax3.plot(pwr_sp[i,:])                  
                          plt.draw()

                      ax3.legend(rows_s,'upper right', shadow=True,title="Rows",prop={'size':8})
                      
                      plt.draw()
                      new_spec=numpy.sum(pwr_sp[rows_s,:], axis=0)
                      maxnp=1.1*numpy.max(new_spec)
                      minnp= (-0.05)*maxnp
                      ax4.cla()
                      ax4.set_title('Summed Spectrum')                      
                      ax4.plot(new_spec)
                      ax4.set_ylim([minnp,maxnp])
                      plt.draw()
            
                      #cnt=cnt+1
                #cur_spec=
                
            #-----------------------------------------------------------------------------
                
            axbutt = plt.axes([0.9, 0.92, .09, 0.07])
            axbutt2 = plt.axes([0.8, 0.92, .09, 0.07])
            but_reset = Button(axbutt2,"Reset",color='0.85', hovercolor='0.95') 
            but_done = Button(axbutt,"Done",color='0.85', hovercolor='0.95')
            
            #-----------------------------------------------------------------------------
            
            def spec_done2(event):
                print ("HIIIIII" )               
                print (rows_s)
                
                self.data_spec=numpy.sum(pwr_sp[rows_s,:], axis=0)
                y=self.data_spec
                nx = y.shape[0]
                
            
                plt.close()
                f = open("try.dat", "w")
                xn2= numpy.linspace(0,(nx-1),nx)
                
                numpy.savetxt(f, numpy.array([xn2,self.data_spec]).T)
                f.close()
                #self.gen_spec2(self.data_spec)
                ####do a fit
                parinfo = [{'value':0., 'fixed':0, 'limited':[0,0], 'limits':[0.,0.]}  
                                    for i in range(5)]                                        
                print((parinfo[0]))

                parinfo[0]['fixed'] = 1
                parinfo[4]['limited'][0] = 1
                parinfo[4]['limits'][0]  = 50.
                values = [5.7, 2.2, 312., 1.5, 2000.]
                #print type(parinfo)
                print(( parinfo[0]))
                err=numpy.sqrt(y)
                p=[0.0,150000,1050.,1.]#,17]#,205.,1.]
                print((p[1:4]))
                #print p[4:7]
        
                for i in range(5): parinfo[i]['value']=values[i]
                expr='p[0] + fit_models.gauss1p(x,p[1:4])' #+ fit_models.gauss1p(x,p[4:7])'#'# + gauss1p(x,0.0,17,205.,1.)'#'p[0] + numpy.sin(x) + numpy.sin(p[1])'#
                params,yfit=mpfitexpr.mpfitexpr(expr,xn2,y,err,p)
                print (params)
                FWHMf=params[3]*2.3548  ##multiply w times 2*SQRT(2*ln(2))
                ampltf=params[1]-params[0]
    
                AREAf=(FWHMf*0.5*ampltf)*2.128934039   ##() * SQRT(PI/ln(2))# =HWHM * Ampl *SQRT(PI/ln(2))
                ##AMPL=AREA*2/2.12FWHM                
                print ('FWHM:  ')
                print (FWHMf)
                print ('AREA:  ')
                print (AREAf)
                print(('height: ',ampltf))
                print((AREAf,'\t', FWHMf))
                y2=yfit
                plt.clf()
                plt.ion()
                fig2=plt.figure()
                #self.ax3 = self.fig.add_subplot(111)
                #self.ax3.cla()            

                #ax.invert_yaxis()

                maxv=numpy.max(y)
                minv=numpy.min(y)
                plt.ylabel('some numbers')
                #self.ax3.set_ylim([-.05*maxv,maxv/0.95])
                axcolor = 'lightgoldenrodyellow'
                #axfreq = plt.axes([0.1, 0.01, 0.8, 0.04], axisbg=axcolor)
                #sfreq = Slider(axfreq, 'y_max', minv/.9, maxv/.9, valinit=maxv) 
                #self.ax3.set_title('Spectrum')                    
                plt.plot(xn2,y,'b',xn2,y2,'r')
        
                #plt.show()
                
            #-----------------------------------------------------------------------------

            but_done.on_clicked(spec_done2)
            
            axbutt2._button = but_reset
            axbutt._button = but_done  ##this make button clickable because of variable loses scope
            cidk = fig2.canvas.mpl_connect('key_press_event', on_key2) 
            cid = fig2.canvas.mpl_connect('motion_notify_event', onmotion) 
            temp=self.gen_spec2
            print ("OHHHHHH")
            #temp.
        #   end if
            
        #   *******
        plt.show()
        #   end 'proces2' method
         
    ##############################################################################

    def gen_spec2(self,rows_s):
        spec_out=open('spec_save.pk', 'wb')
        cp.dump(rows_s,spec_out)
        spec_out.close()
        print ("IIIIMMMMM")
        t= numpy.linspace(-50,50,200)
        sp = pyspeckit.Spectrum(data=rows_s,xarr=t,header={})
        sp.plotter(xmin=-100,xmax=100,ymax=150,ymin=0)
        #return
        
    ##############################################################################
        
    def fit_specn(self):

        parinfo = [{'value':0., 'fixed':0, 'limited':[0,0], 'limits':[0.,0.]}  
                                    for i in range(5)]                                        
        print((parinfo[0]))

        parinfo[0]['fixed'] = 1
        parinfo[4]['limited'][0] = 1
        parinfo[4]['limits'][0]  = 50.
        values = [5.7, 2.2, 500., 1.5, 2000.]
        #print type(parinfo)
        print((parinfo[0]))
        err=numpy.sqrt(y)
        p=[0.0,5,98.,2.]#,17]#,205.,1.]
        print((p[1:4]))
        print((p[4:7]))
        
        for i in range(5): parinfo[i]['value']=values[i]
        expr='p[0] + fit_models.gauss1p(x,p[1:4])' #+ fit_models.gauss1p(x,p[4:7])'#'# + gauss1p(x,0.0,17,205.,1.)'#'p[0] + numpy.sin(x) + numpy.sin(p[1])'#
        params,yfit=mpfitexpr.mpfitexpr(expr,x,y,err,p)
        print (params)
 
        y2=yfit
        self.ax.plot(x,y2)
        
    ##############################################################################
        
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = str(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
            
    ##############################################################################
            
    def on_about(self):
        msg = """ SHS DATA REDUCTION:
        
         * De-Bias
         * FLAT Field
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip()) 
    
##############################################################################

def my_imshow(my_img,ax=None,**kwargs):
                if ax is None:
                    ax = plt.gca()
                def format_coord(x, y):
                    x = int(x + 0.5)
                    y = int(y + 0.5)
                    try:
                        return "%s @ [%4i, %4i]" % (my_img[y, x], x, y)
                    except IndexError:
                        return ""
                ax.imshow(my_img,**kwargs)
                ax.format_coord = format_coord
                plt.draw()
#class Test(QWidget):
  #def __init__( self, parent=None):
      #super(Test, self).__init__(parent)

     # self.qlabel2 = QLabel('I am in Test widget')

      #layout = QHBoxLayout()
      #layout.addWidget(self.qlabel2)
      #self.setLayout(layout)
      
##############################################################################
      
def zem_inter(fname):
      data = numpy.genfromtxt(fname,skip_header=24, dtype='float64')
      wd = data.shape[1]
      #print data.shape
      data = numpy.genfromtxt(fname,skip_header=24,usecols=list(range(1,wd)), dtype='float64')
      #hits=numpy.genfromtxt(fname,skip_header=7,usecols=(1,2), dtype='float64')
      #print hits
      return data
  
##############################################################################
      
def gray2qimage(gray): 
      
    gray= (gray / (gray.max()/255.))
    #print gray.max()
    gray = numpy.require(gray, numpy.uint8, 'C')
    
    h, w = gray.shape

    result = QImage(gray.data , w, h, QImage.Format_Indexed8)
    result.ndarray = gray
    for i in range(256):
        result.setColor(i, QColor(i, i, i).rgb())
    return result

##############################################################################

def do_fft(inter):   
    
    pwr_s = fftpack.fft2(inter)    
    return pwr_s

##############################################################################

def window2d(self,M, N):
    """
   
    """
    win_nam=str(self.menu.currentText())
    print (('Applied:', win_nam))
    #print type(win_nam)
    if N <= 1:
        return numpy.hanning(M)
    elif M <= 1:
        return numpy.hanning(N) # scalar unity; don't window if dims are too small
    else:
        return numpy.outer(windo.Window(M, win_nam).data,windo.Window(N, win_nam).data)
    
##############################################################################

def hanning2d(M, N):
    """
   
    """

    if N <= 1:
        return numpy.hanning(M)
    elif M <= 1:
        return numpy.hanning(N) # scalar unity; don't window if dims are too small
    else:
        return numpy.outer(numpy.hanning(M),numpy.hanning(N))
    
##############################################################################

def do_fit():
    t= numpy.linspace(-50,50,100)
    sp = pyspeckit.Spectrum(data=x,xarr=t,header={})
    sp.plotter(xmin=-100,xmax=100,ymax=150,ymin=0)
    
##############################################################################

def rebin(a, *args):
    '''rebin ndarray data into a smaller ndarray of the same rank whose dimensions
    are factors of the original dimensions. eg. An array with 6 columns and 4 rows
    can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
    example usages:
    >>> a=rand(6,4); b=rebin(a,3,2)
    >>> a=rand(6); b=rebin(a,2)
    '''
    shape = a.shape
    lenShape = len(shape)
    factor = numpy.asarray(shape)/numpy.asarray(args)
    evList = ['a.reshape('] + \
             ['args[%d],factor[%d],'%(i,i) for i in range(lenShape)] + \
             [')'] + ['.sum(%d)'%(i+1) for i in range(lenShape)] + \
             ['/factor[%d]'%i for i in range(lenShape)]
    print((''.join(evList)))
    return eval(''.join(evList))
        
##############################################################################
        
app = QApplication(sys.argv)
myWidget = Main()
myWidget.show()
app.exec_()