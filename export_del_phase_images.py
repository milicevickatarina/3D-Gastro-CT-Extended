# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 17:28:56 2021

@author: Katarina Milicevic, School of Electrical Engineering
         Belgrade, Serbia

Exporting rendered data to .jpg and .stl files
"""
import vtk
import os
from datetime import datetime

def main(fileName, main_dir):
    # Creating export directory                                          
    exp_dir = os.path.join(main_dir, "export")
    if not os.path.exists(exp_dir):
        os.makedirs(exp_dir)
    
    colors = vtk.vtkNamedColors()

    organsMap = CreateOrgansMap()
    colorLut = CreateColorLut()

    # Setup render window, renderer, and interactor.
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    
    appendPolydata = vtk.vtkAppendPolyData() 

    # Use this to ensure that the organs are selected in this order.
    organs = [
    'heart',
    'bones',
    'liver and spleen',
    'kidneys',
    'stone',
    'stone2'
]

    for i in range(0, len(organs)):
        actor, normals = CreateOrganActor(fileName, organsMap[organs[i]][0])
        actor.GetProperty().SetOpacity(organsMap[organs[i]][1])
        actor.GetProperty().SetDiffuseColor(colorLut.GetTableValue(organsMap[organs[i]][0])[:3])
        actor.GetProperty().SetSpecular(.5)
        actor.GetProperty().SetSpecularPower(10)
        renderer.AddActor(actor)
        # Collect data for stl
        appendPolydata.AddInputConnection(normals.GetOutputPort())

    # Save to stl
    # stlWriter = vtk.vtkSTLWriter()
    # stlWriter.SetInputConnection(appendPolydata.GetOutputPort())
    # stlWriter.SetFileName(generate_file_name(exp_dir,'.stl'))
    # stlWriter.Write()

    renderer.GetActiveCamera().Elevation(-90)
    renderer.ResetCamera()
    renderer.GetActiveCamera().Zoom(2)
    renderer.ResetCameraClippingRange()
    renderer.SetBackground(colors.GetColor3d("white"))

    renderWindow.SetSize(800, 800)
    renderWindow.OffScreenRenderingOn()
    renderWindow.Render()

    # Save first window view to jpg
    vtk_win_im = vtk.vtkWindowToImageFilter()
    vtk_win_im.SetInput(renderWindow)
    vtk_win_im.Update()
    vtk_image = vtk_win_im.GetOutput()
    writer = vtk.vtkJPEGWriter()
    writer.SetInputData(vtk_image)
    writer.SetFileName(generate_file_name(exp_dir,'.jpg'))
    writer.Write()


def get_program_parameters():
    import argparse
    description = 'Kidneys with some other abdominal organs'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='organs.mhd.')
    args = parser.parse_args()
    return args.filename


def CreateColorLut():
    colors = vtk.vtkNamedColors()

    colorLut = vtk.vtkLookupTable()
    colorLut.SetNumberOfColors(7)
    colorLut.SetTableRange(0, 6)
    colorLut.Build()

    colorLut.SetTableValue(0, 0, 0, 0, 0)
    colorLut.SetTableValue(1, colors.GetColor4d("red"))
    colorLut.SetTableValue(2, colors.GetColor4d("wheat"))
    colorLut.SetTableValue(3, colors.GetColor4d("darkred"))
    colorLut.SetTableValue(4, colors.GetColor4d("cadmium_orange"))
    colorLut.SetTableValue(5, colors.GetColor4d("lightslategray")) #lightslategray
    colorLut.SetTableValue(6, colors.GetColor4d("lightslategray"))
    
    return colorLut


def CreateOrgansMap():
    organMap = dict()
    organMap["heart"] = [1, 0.3]
    organMap["bones"] = [2, 1.0]
    organMap["liver and spleen"] = [3, 0.4]
    organMap["kidneys"] = [4, 0.4]
    organMap["stone"] = [5, 1.0]
    organMap["stone2"] = [6, 1.0]

    return organMap


def CreateOrganActor(fileName, organ):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(fileName)
    reader.Update()

    selectorgan = vtk.vtkImageThreshold()
    selectorgan.ThresholdBetween(organ, organ)
    selectorgan.SetInValue(255)
    selectorgan.SetOutValue(0)
    selectorgan.SetInputConnection(reader.GetOutputPort())

    gaussianRadius = 1
    gaussianStandardDeviation = 2.0
    gaussian = vtk.vtkImageGaussianSmooth()
    gaussian.SetStandardDeviations(gaussianStandardDeviation, gaussianStandardDeviation, gaussianStandardDeviation)
    gaussian.SetRadiusFactors(gaussianRadius, gaussianRadius, gaussianRadius)
    gaussian.SetInputConnection(selectorgan.GetOutputPort())

    isoValue = 127.5
    mcubes = vtk.vtkMarchingCubes()
    mcubes.SetInputConnection(gaussian.GetOutputPort())
    mcubes.ComputeScalarsOff()
    mcubes.ComputeGradientsOff()
    mcubes.ComputeNormalsOff()
    mcubes.SetValue(0, isoValue)

    smoothingIterations = 5
    passBand = 0.001
    featureAngle = 60.0
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputConnection(mcubes.GetOutputPort())
    smoother.SetNumberOfIterations(smoothingIterations)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(featureAngle)
    smoother.SetPassBand(passBand)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(smoother.GetOutputPort())
    normals.SetFeatureAngle(featureAngle)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(normals.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor, normals

def generate_file_name(dir_path, extension):
    n = datetime.now().strftime("%Y%m%d-%I%M%S")
    return dir_path + '/' + n + extension
    
def stl_file_name():
    n = datetime.now().strftime("%Y%m%d-%I%M%S")
    return '/'+n+".stl"

if __name__ == '__main__':
    main()