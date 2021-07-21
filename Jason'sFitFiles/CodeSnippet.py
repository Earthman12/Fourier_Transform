# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 11:29:36 2020

@author: Earthman
"""

   def proces2(self):
        if data3.any():
            print((data2.shape))
            F1=  do_fft(data3)
            F2 = fftpack.fftshift( F1 )
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
            ax.imshow((numpy.log10(pwr_sp)),cmap = cm.Greys_r,vmin=minv, vmax=maxv)
            ax.set_frame_on(False)
            ax.set_xticks([]); ax.set_yticks([])
            plt.show()
       #        ax.imshow(data3,cmap = cm.Greys_r,vmin=vmin_in, vmax=vmax_in)
            #plt.savefig('th_ar_pwr_test.svg', bbox_inches='tight',format='svg', dpi=1000, transparent=True,pad_inches=0)              
       ###END PLOT POWER     
            
            bb=ax.imshow((numpy.log10(pwr_sp)),cmap = cm.Greys_r,vmin=minv, vmax=maxv/.8, picker=True)
            ax.invert_yaxis()
            ax2 = fig2.add_subplot(222)

            print(("The Min is", minv))
            
            print(("The max is",maxv))
            axcolor = 'lightgoldenrodyellow'
            axfreq = plt.axes([0.1, 0.01, 0.8, 0.04], axisbg=axcolor)
            sfreq = Slider(axfreq, 'y_max', minv/.9, maxv/.9, valinit=maxv) 

            ax3 = fig2.add_subplot(223)
            ax4 = fig2.add_subplot(224)
            ax3.set_title('Selected Rows')
            ax4.set_title('Summed Spectrum')
            def update(val):
    
               freq = sfreq.val
               print((sfreq.val))
               ax2.set_ylim([-.1*maxv,sfreq.val])
               ax3.set_ylim([(-.1*maxv),sfreq.val])
               ax3.set_title('Selected Rows')
               plt.draw()
            sfreq.on_changed(update)
