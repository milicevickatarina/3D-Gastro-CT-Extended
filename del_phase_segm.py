# -*- coding: utf-8 -*-
"""
Created on January 2022

@author: Katarina Milicevic, School of Electrical Engineering
         Belgrade, Serbia

Segmentation process of delayed phase
"""
import SimpleITK as sitk
import numpy as np
import os

def main(work_dir):
    
    img_del = sitk.ReadImage(work_dir + "/data/delayed_phase_preprocessed.mha")
    
    # Reading bones segmentation image
    bones = sitk.ReadImage(work_dir + "/segmentation results/bones.mhd")
    stone_sitk = sitk.ReadImage(work_dir + "/segmentation results/stone.mhd")
    stone_sitk.CopyInformation(img_del)
    
    thres_del = 135
    phase_del = img_del > thres_del

    cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(phase_del, [5, 5, 5])
    phase_del = sitk.BinaryClosingByReconstruction(cleaned_thresh_img, [5, 5, 5])

    save_dir = os.path.join(work_dir, "delayed phase segmentation results")
    # Commented savings are for visualization of algorithm steps
    # sitk.WriteImage(phase_del, os.path.join(save_dir, "phase_del.mhd"))
    
    dil_filter =  sitk.BinaryDilateImageFilter()
    dil_filter.SetKernelRadius(3)
    
    bones_roi = dil_filter.Execute(bones)
    bones_roi = dil_filter.Execute(bones_roi)
    bones_del = phase_del * bones_roi

    stone_sitk.SetOrigin(img_del.GetOrigin())
    phase_del = phase_del-bones_del

    # sitk.WriteImage(bones_del, os.path.join(save_dir, "phase_del_bones.mhd"))
    # sitk.WriteImage(phase_del, os.path.join(save_dir, "phase_del_kidney.mhd"))
    img_all = phase_del + bones_del*2 + stone_sitk*5
    all_array = sitk.GetArrayFromImage(img_all)
    
    # Rotation of axial slices around y-axis
    X_for_mirror = np.transpose(all_array, (0,2,1))
    X_mirrored = X_for_mirror[::-1]
    whole_segm_mirror = np.transpose(X_mirrored,(0,2,1))
    
    whole_segm_sitk = sitk.GetImageFromArray(whole_segm_mirror)
    whole_segm_sitk.SetSpacing(img_del.GetSpacing())
    
    # Segmentation image saving
    save_dir = os.path.join(work_dir, "delayed phase segmentation results")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    sitk.WriteImage(whole_segm_sitk, os.path.join(save_dir, "del_phase_segmentation.mhd"))