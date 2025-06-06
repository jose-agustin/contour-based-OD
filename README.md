# contour-based-OD
Implementation of a contour-based object detection algorithm for ScaleCam. 

Algorithm summary:
- Image is converted from RGB to HSV
- Then two sets of lower and upper bounds are defined for every HSV channel to filter out all shades of blue color and low brightness pixels. This removes most of the pixels of the conveyor belt. The output image is a binary image with filtered-out pixels set at 0.
- Then two sets of dilation-erosion process are applied to the binary image. This helps reduce noise and groups the pixels of the white blobs in the image.
- Finally contour detection with a set threshold that defines if the area contained in the contour must be counted as an object or not.
