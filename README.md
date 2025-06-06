# contour-based-OD
Implementation of a contour-based object detection algorithm for ScaleCam. 

- Image is converted from RGB to HSV
- Then two sets of lower and upper bounds are defined for every HSV channel to filter out all shades of blue color and low brightness pixels. This removes most of the pixels of the conveyor belt.
- Then two sets pf dilation-erosion process.
- Finally contour detection with a set threshold that defines if the area contained in the contour must counted as an object or not.
