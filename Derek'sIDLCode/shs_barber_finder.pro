FUNCTION shs_barber_finder, pathbase = pathbase

file_array_wl=file_search(pathbase,'wl*.fit',count=wl_num_file)
file_array_th=file_search(pathbase,'th*.fit',count=th_num_file)

file_array = [file_array_wl,file_array_th]

;print,file_array

barbers = intarr(wl_num_file+th_num_file)
  lims = [200,320]; create general sub box to check in each file for barber pole
  
for i=0,(wl_num_file+th_num_file)-1 DO BEGIN
  image1  = readfits(file_array[i],/silent)
  ;print,file_array[i]
  tempim = image1
  tempim(lims[0],*) = max(image1) 
  tempim(lims[1],*) = max(image1) 
  tempim(*,lims[0]) = max(image1) 
  tempim(*,lims[1]) = max(image1)
  
  sz = size(image1)
  ;window, /free, xsize=sz(1), ysize=sz(2), title='(1) raw interferogram'
  ;tvscl, tempim

  mx = max(image1[lims[0]:lims[1],lims[0]:lims[1]],index) ;divide row by ybin=4 for 4x1 binned data (i.e., [column, rows/4] 
  ind = array_indices(image1[lims[0]:lims[1],lims[0]:lims[1]],index)
  ind[0] = ind[0]+lims[0]
  ind[1] = ind[1]+lims[0]  
  ;print,ind, image1[ind[0],ind[1]], FORMAT = '(%"[fx,fy]=(0,0) peak value is at [%d, %d] = %f")'
  ;profiles, image1
  barbers[i] = ind[0]
endfor
;print,'files found for barber pole calc=',uint(barbers)
return, uint(median(barbers))

END