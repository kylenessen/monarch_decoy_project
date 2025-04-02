# Project Description

## Prompt

I would like your help developing a python script to extract pixel values out of three images. The purpose of this project is to see if different 3D printed materials sufficiently mimic the spectral properties of a monarch butterfly. I have taken a photo of different filaments along with a sample monarch under visible, UV, and NIR conditions. The images are currently in Nikon raw format (NEF). I need to set the white balance with an included teflon card in the image. Unfortunately, I cannot do this using traditional software (e.g. Photoshop) as the UV and NIR are so far out of the normal range that I cannot set it correctly. 

The project should do a few things:

1. Set the white balance for each image. We can than save each image as a jpeg to further process. This can be done as its own script. It's important that we are not constrained by a typical white balance range. Ideally, if I understand white balance correctly, the channels should be approximately equal. 
2. Define regions of interest within each photo. Each region should be freely drawn using a polygon tool. It should allow for irregular shapes, such as those found on the monarch. I should also be able to label each ROI so I can classify the values it produces for later analysis (e.g., black PLA vs black part of the monarch wing).
3. Once ROIs are established, extract pixel values per channel in each ROI. I want each pixel value to have its own row. So for example, a single pixel should have a brightness value (0-255), a channel (e.g., Red), the image it came from (e.g., UV), and the ROI (e.g., PLA black). I realize this will create a lot of rows, but that is fine. I want maximize flexibility when doing the analysis. This data should be saved to a csv. OK, to create a CSV per file, as there are relatively few. 

I believe that's it for the extract side of things. I want to do everything in python. Do you have any questions for me? 