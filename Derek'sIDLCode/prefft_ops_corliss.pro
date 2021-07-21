function prefft_ops_corliss,file=file,pathbase=pathbase,BI=BI,ff=ff,win=win,remavg=remavg;,sigma=sigma
;this function takes raw interferogram, isolates subregion, sigma filters, subtracts median nand flat-field
; /win flag tells windows to display
common share

image = readfits(pathbase+file+'.fit')

  
if (n_elements(BI) ne 0) then begin
  bias   = readfits(BI,/silent)
  image = image - bias
endif

;add to share block, set if to determine if already determined for night, get cent for individual spectra, compare, return differnce for phase shift correction
;cent =  shs_barber_finder(pathbase=pathbase) ;NOTE: it's getting the median from thar and wl fits in directory


  ;Ha bounds
  bnds = 500/2
  nxl = cent-bnds; 196+1; this puts first point to right of fringe max in ft array element zero!
  nxh = cent + bnds; see "Corrections of ph. err. in Fourier Spect." Porter, Tanner (1983) J.Infr.&mm Waves, 4,2
  nyl = 40;
  nyh = 159 ;ybin = 4 for camera chip binning in some data.
  
  bicorr_image = image
  
  ; Sigma filter image
   if sigma eq 1 then BEGIN
   image = sigma_filter(image, 20, N_sigma=(3), /ALL,/iterate,/monitor)   ;11/5/15 changed to iterative approach. declared common share, sigma_count variable to track
   print,'sigma filterd ',n_elements(sigma_count),' times'
   endif else begin
    print, 'not sigma filterd'
   endelse

  tempim = image
  
  sub_image  = image(nxl:nxh,nyl:nyh)
  sub_image_preFF=sub_image
  ;print,size(sub_image)
   sz = size(tempim) 
  ; Use tempim to display the cropped image
  tempim(nxl,*) = max(tempim) 
  tempim(nxh,*) = max(tempim) 
  tempim(*,nyl) = max(tempim) 
  tempim(*,nyh) = max(tempim)
  
  tempim(cent,nyl:sz(2)/4)=max(tempim)
  tempim(cent,3*sz(2)/4:nyh)=max(tempim) 
print,size(sub_image),' = ===sub image size'

  ;FF (normalized flatfield image here)
if (n_elements(ff) ne 0) then begin
  type = size(ff,/type)
  if type(0) EQ 4 then begin   ;type 4 is float (e.g. "3.0"), the number itself is mult factor of variance used in signal mask
    sub_image = ff_noise_maskA(sub_image,ff,file=file,win=win);set win=win to see
    ff_type = 'SM';'Signal Mask'
  endif else begin
    if FILE_TEST(ff) EQ 1 then begin ;type 7 is string (presumed a WL file name)
      tempff = readfits(ff,/silent)
      sub_ff = tempff(nxl:nxh,nyl:nyh)
      sub_image = sub_image/sub_ff
      ff_type = 'WL'
    endif else begin
      print,'unrecognized flat field file'
      ff_type = 'NF';'No File'
    endelse
  endelse
endif else begin
  print, 'No flat field file'
  ff_type = 'NF';'No File'
endelse
sub_image_FF=sub_image

;;compute actual center by interpolation
;cent_fit = shs_barber_finderIFG(sub_image=sub_image,range=25)

if n_elements(remavg) NE 0 THEN BEGIN
  ;Average/median correction (after FF)
  result    = moment(sub_image)
  avgim     = result[0]
  sub_image = sub_image - avgim
  sub_image_med=sub_image
endif

if n_elements(win) NE 0 THEN BEGIN
  sz = size(tempim)
  ; Display bias corrected IFG w/sub_image location
  window, /free, xsize=sz(1), ysize=sz(2), title='bias corrected interferogram w/sub_image location'
  tvscl, (bicorr_image^2)
  ;;profiles,tempim

if type(0) EQ 7 then begin ;only for WL (same as SM ff)
  ;check cent
  ff_type='none, uncorrected'
  ;cent_fit=shs_barber_finderIFG(sub_image=sub_image_preFF,range=25)

  window, /free, xsize=sz(1), ysize=sz(2), title='sigma filt. IFG w/sub_image location'
  tvscl, tempim
  ;;profiles,tempim

  window, /free, xsize=800, ysize=600, title='sigma filtered row cuts'
  cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2])),image[nxl:nxh,(nyh-nyl)/2]
  ;;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2-10])),image[nxl:nxh,(nyh-nyl)/2-10],color='blue',/overplot,/noerase
  ;;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2+10])),image[nxl:nxh,(nyh-nyl)/2+10],color='red',/overplot,/noerase
  ;;profiles,tempim
endif

  sz=size(sub_image)
  window,/free,xsize=800,ysize=600, title='centerburst (blck) +-1(blue) & end Vcuts(red)'
  cgplot,sub_image_FF[sz(1)/2,*],color='black'
  cgplot,sub_image_FF[sz(1)/2-1,*],/overplot,/noerase,color='blue';,linestyle=1
  cgplot,sub_image_FF[sz(1)/2+1,*],/overplot,/noerase,color='blue'
  cgplot,sub_image_FF[0,*],/overplot,/noerase,color='red'
  cgplot,sub_image_FF[sz(1)-1,*],/overplot,/noerase,color='red'
  
  ;window, /free, xsize=sz(1), ysize=sz(2), $
  ;  title=(n_elements(ff) ne 0)?'sub_image: Flat-Fielded by '+ff_type:'sub_image: NOT flat-fielded'
  ;tvscl,sub_image_FF
  ;;profiles,sub_image
  
  ;window, /free, xsize=800, ysize=600, title='FF row cuts'
  ;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2])),sub_image_FF[*,(nyh-nyl)/2]
  ;;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2-10])),image[nxl:nxh,(nyh-nyl)/2-10],color='blue',/overplot,/noerase
  ;;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2+10])),image[nxl:nxh,(nyh-nyl)/2+10],color='red',/overplot,/noerase
  ;
  ;
  ;if n_elements(remavg) NE 0 THEN BEGIN 
  window,/free,xsize=sz(1), ysize=sz(2),$
    title=ff_type+' FF & median corrected sub_image'
    tvscl,sub_image_med
  ;
  ;window, /free, xsize=800, ysize=600, title='FF & med cor row cuts'
  ;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2])),sub_image_med[*,(nyh-nyl)/2]
  ;;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2-10])),image[nxl:nxh,(nyh-nyl)/2-10],color='blue',/overplot,/noerase
  ;;cgplot, indgen(n_elements(image[nxl:nxh,(nyh-nyl)/2+10])),image[nxl:nxh,(nyh-nyl)/2+10],color='red',/overplot,/noerase 
  ;endif
  
ENDIF


Return, sub_image

END