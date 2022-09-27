# -*- coding: utf-8 -*-
"""
Created on January 2022

@author: Katarina Milicevic, School of Electrical Engineering
         Belgrade, Serbia

Making individual phase images with appropriate geometry
"""
import SimpleITK as sitk
import os
from os import walk


def main(imagesDir):
    
    save_dir = os.path.join(imagesDir, "phases")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    files = []
    for (dirpath, dirnames, filenames) in walk(imagesDir):
        files.extend(filenames)
        break
  
    nat_image_name = ''
    art_image_name = ''
    del_image_name = ''
    vein_image_name = ''
    for filename in files:
        if (filename.find('NAT')!=-1) | (filename.find('Nat')!=-1):
            if nat_image_name!='':
                if os.path.getsize(os.path.join(imagesDir, nat_image_name)) < os.path.getsize(os.path.join(imagesDir, filename)):
                    nat_image_name = filename
            else:
                nat_image_name = filename
        elif (filename.find('ART')!=-1) | (filename.find('Art')!=-1):
            if art_image_name!='':
                if os.path.getsize(os.path.join(imagesDir, art_image_name)) < os.path.getsize(os.path.join(imagesDir, filename)):
                    art_image_name = filename
            else:
                art_image_name = filename
        elif (filename.find('ODL')!=-1) | (filename.find('Odl')!=-1):
            if del_image_name!='':
                if os.path.getsize(os.path.join(imagesDir, del_image_name)) < os.path.getsize(os.path.join(imagesDir, filename)):
                    del_image_name = filename
            else:
                del_image_name = filename
        elif (filename.find('VEN')!=-1) | (filename.find('Portna')!=-1):
            if vein_image_name!='':
                if os.path.getsize(os.path.join(imagesDir, vein_image_name)) < os.path.getsize(os.path.join(imagesDir, filename)):
                    vein_image_name = filename
            else:
                vein_image_name = filename
            
                
    # Native phase image preparation
    try:
        nat_image = sitk.ReadImage(os.path.join(imagesDir, nat_image_name))
    except:
        return 1
    
    nat_image = sitk.Flip(nat_image, [False, False, True])
    sitk.WriteImage(nat_image, save_dir+"/native.mha")
    
    # # Vein phase image preparation (not needed for excretory phase segmentation)                        
    # if vein_image_name!='':
    #     try:
    #         vein_image = sitk.ReadImage(os.path.join(imagesDir, vein_image_name))
    #         vein_image = sitk.Flip(vein_image, [False, False, True])
    #         sitk.WriteImage(vein_image, save_dir+"/vein.mha")
    #     except:
    #         print("There was a mistake in reading vein phase!")
    # else:         
    #     # Division of ART/VEN image to separated arterial and vein images and their preparation
    #     # Note: This was the case with one set of used CT scans (from one scanner which brings these series together)
    #     try:
    #         image = sitk.ReadImage(os.path.join(imagesDir, art_image_name))
    #         image_array = sitk.GetArrayFromImage(image)
            
    #         # art_image_array = image_array[0:image_array.shape[0]//2,:,:]
    #         ven_image_array = image_array[image_array.shape[0]//2:,:,:]
            
    #         # art_image = sitk.GetImageFromArray(art_image_array)
    #         # art_image.SetSpacing(nat_image.GetSpacing())
    #         # sitk.WriteImage(art_image, save_dir + "/arterial.mha")
            
    #         vein_image = sitk.GetImageFromArray(ven_image_array)
    #         vein_image.SetSpacing(nat_image.GetSpacing())
    #         sitk.WriteImage(vein_image, save_dir+"/vein.mha")
    #     except:
    #         print("There was a mistake in reading vein phase!")
    
    # Delayed phase image preparation
    try:
        del_image = sitk.ReadImage(os.path.join(imagesDir, del_image_name))
    except:
        return 1
            
    del_image = sitk.Flip(del_image, [False, False, True])
    sitk.WriteImage(del_image, save_dir+"/delayed.mha")
    
    return 0