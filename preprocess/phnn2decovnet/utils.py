import pandas as pd
import nibabel as nib
import numpy as np
import scipy.ndimage

def threshold_mask(v_data,threshold):
    import scipy.ndimage.morphology
    from skimage import measure
    import numpy as np
    v_data[v_data>threshold]=1
    v_data[v_data<1]=0
    all_labels = measure.label(v_data)
    props=measure.regionprops(all_labels)
    props.sort(key=lambda x:x.area,reverse=True) #sort connected components by area
    thresholded_mask=np.zeros(v_data.shape)
    if len(props)>=2:
        #print(props[0].area)
        #print(props[1].area)
        if props[0].area/props[1].area>5: #if the largest is way larger than the second largest
            thresholded_mask[all_labels==props[0].label]=1 #only turn on the largest component
        else:
            thresholded_mask[all_labels==props[0].label]=1 #turn on two largest components
            thresholded_mask[all_labels==props[1].label]=1
    elif len(props):
        thresholded_mask[all_labels==props[0].label]=1

    thresholded_mask=scipy.ndimage.morphology.binary_fill_holes(thresholded_mask).astype(np.uint8)
    return thresholded_mask




def get_numpy_mask(path_in, path_out, threshold=0.75):
    try:
        # print(path_in, path_out)
        clip_range = [0.2, 0.7]
        print(f'Processing: {path_in}')
        volume=nib.load(path_in)
        v_data=np.squeeze(volume.get_fdata())
        v_data += 1
        v_data = scipy.ndimage.interpolation.zoom(v_data, (1, 1, volume.header.get_zooms()[2]), mode="nearest")
        v_data -= 1

        mask = threshold_mask(v_data,threshold)
        mask = mask.transpose(2, 1, 0)
        num_frames = len(mask)
        left, right = int(num_frames*clip_range[0]), int(num_frames*clip_range[1])
        mask = mask[left:right]
        #for i in range(mask.shape[0]):
        #    mask[i]=np.rot90(mask[i])
        np.save(path_out, mask)
        del(volume, v_data, mask)
    except Exception as e:
        print(f'{e}')

    

INPUT_CSV = 'patients_test.csv'
THRESHOLD = 0.75
df = pd.read_csv(INPUT_CSV)
in_list = []
out_list = []
for index, row in df.iterrows():
    in_list.append(row['path_in'])
    out_list.append(row['path_out'])
    #get_numpy_mask(row['path_in'], row['path_out'], THRESHOLD)


from concurrent import futures

num_threads=12

with futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
    fs = [executor.submit(get_numpy_mask, x, y) for x, y in zip(in_list, out_list)]
    for i, f in enumerate(futures.as_completed(fs)):
        print ("{}/{} done...".format(i, len(fs)))
