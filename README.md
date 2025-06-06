# contour-based-OD
Implementation of a contour-based object detection algorithm for ScaleCam. 

- Image is converted from RGB to to HSV
- Then two sets of lower and upper bounds are defined for every channel to filter out the blue shades and low brightness pixels.
- Then two sets pf dilation-erosion process.
- Finally contour detection with a set threshold that defines if the area contained in the contour must counted as an object or not.
