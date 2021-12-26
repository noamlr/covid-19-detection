import pydicom
import os
import numpy as np

listdironly = lambda d: [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
paths = ['/ssd/share/HCPA-organizado-parte-2/', '/ssd/share/CT-Original/DICOM-HCPA/exame-pulmao/']


for p in paths:
    patients = listdironly(p)
    for patient in patients:
        slices = [pydicom.read_file(os.path.join(patient, s), force=True) for s in os.listdir(patient)]
        
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        #slice_thickness does not matter so much, there are not different from zero
        # if slice_thickness != 1:
        #     print(f'patient: {patient}, thickness: {slice_thickness}')
        for s in slices:
            if s.RescaleSlope != 1:
                print(f'patient: {patient}, thickness: {s.RescaleSlope}')
                break
        if slices[0].pixel_array.shape != (512, 512):
            sh = slices[0].pixel_array.shape
            print(f'patient: {patient}, shape: {sh}')
        # print(len(slices))
