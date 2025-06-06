import numpy as np
import cv2 as cv
import boto3
import io
import matplotlib.pyplot as plt
import csv

####################
# list objectcs in the S3 bucket
bucket_name = "veg-dpd-iae-nonprod-scalecam-object-detection-benchmark-dataset"
client = boto3.client("s3")
dict_with_objects = client.list_objects_v2(Bucket=bucket_name)  # -> dict with a Contents[] list of dicts
list_of_objects = []
for obj in dict_with_objects["Contents"]:
    if obj["Key"].endswith("png") and obj["Key"].startswith("EmptyFlight/dirty_belt"):
        list_of_objects.append(obj["Key"])
print(f"images: {len(list_of_objects)}\n")

####################
# read file content
bucket = boto3.resource("s3").Bucket(bucket_name)
# iterating over the list_of_objects
results_list = []
for key in list_of_objects[:]:
    file_stream = io.BytesIO()
    bucket.Object(key).download_fileobj(file_stream)
    np_1d_array = np.frombuffer(file_stream.getbuffer(), dtype="uint8")
    im = cv.imdecode(np_1d_array, cv.IMREAD_COLOR)

    # OD algorithm
    # crop the image
    p_h = int(im.shape[0] * 0.125)  # 0.125
    p_w = int(im.shape[1] * 0.065)  # 0.065
    im = im[p_h:im.shape[0]-p_h, p_w:im.shape[1]-p_w, :]

    # Convert to HSV space
    hsv = cv.cvtColor(im, cv.COLOR_BGR2HSV)

    # Define limits in HSV space (0,35,20) - (60,255,255)
    low_bound = np.array([0, 35, 20])
    up_bound = np.array([60, 255, 255])
    binary1 = cv.inRange(hsv, low_bound, up_bound)

    # Define new limits in HSV space for the second range (150,35,20) - (179,255,255)
    low_bound = np.array([150, 35, 20])
    up_bound = np.array([179, 255, 255])
    binary2 = cv.inRange(hsv, low_bound, up_bound)

    # Add both masks together
    binary3 = cv.add(binary1, binary2)

    # dilate and erode the image to remove noise
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))  # Rectangular kernel
    dilate = cv.dilate(binary3, kernel, iterations=5)
    erode = cv.erode(dilate, kernel, iterations=5)

    # erode and dilate the image again to remove noise
    erode2 = cv.erode(erode, kernel, iterations=5)
    mask = cv.dilate(erode2, kernel, iterations=5)
    result = cv.bitwise_and(im, im, mask=mask)

    # contours
    # contours: tuple of arrays, cv.RETR_TREE: all, 
    # cv.RETR_EXTERNAL: only external contours
    contours, hierarchy = cv.findContours(
        mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # compute areas of the contours
    areas = []
    for cnt in contours:
        A = cv.contourArea(cnt)
        areas.append(A)

    # filter out objects with low area (algorithm ends here)
    objects = [a for a in areas if a > 3000]

    # put results in a list of dictonaries for later store in csv
    results_list.append({"key": key, "objects": len(objects)})

    # print the results
    print(f"image = {key}")
    print(f"objects = {len(objects)}")
    print(f"areas = {areas}")
    print("")

    # # plot images
    # cv.drawContours(im, contours, -1, (0, 0, 0), 4)
    # im_plt = cv.cvtColor(im, cv.COLOR_BGR2RGB)
    # plt.figure()
    # plt.imshow(im_plt)
    # mask_plt = cv.cvtColor(mask, cv.COLOR_BGR2RGB)
    # plt.figure()
    # plt.imshow(mask_plt)

# save results in a csv file
with open("results__100xx-00xx_2025-05-19.csv", "a") as file:
     writer = csv.DictWriter(file, fieldnames=["key", "objects"])
     writer.writeheader()
     for result in results_list:
         writer.writerow(result)
