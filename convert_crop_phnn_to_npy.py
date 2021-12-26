import nibabel as nib
import pandas as pd
import scipy.ndimage

df = pd.read_csv('patients_dir.csv')


for index, row in df.iterrows():
   #print(row['path']) 
    patient = row['patient']
    path_seg = row['path_segmented']
    path_ori = row['path_original']
    if index > 3: 
        break
    ct_seg = nib.load(path_seg)
    pixels = ct_seg.get_fdata()
    if pixels.shape[0] != 512 or pixels.shape[1] != 512:
        print(f'Patient {patient} shape greater than 512: {pixels.shape}')
        continue
    zoom_z = ct_seg.header.get_zooms()[2]
    max_value = pixels[0,0,0]
    pixels[pixels == max_value] = 0
    # dd = scipy.ndimage.interpolation.zoom(d, (1, 1, 0.625), mode="nearest")
    print(ct_seg.header.get_zooms(), pixels.shape)




print(len(df))
