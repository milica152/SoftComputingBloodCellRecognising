import xml.etree.ElementTree as ET
import os
import glob


def overlapping_area(rectangle1, rectangle2):
    x_overlap = max(0, min(rectangle1[2], rectangle2[2]) - max(rectangle1[0], rectangle2[0]))
    y_overlap = max(0, min(rectangle1[3], rectangle2[3]) - max(rectangle1[1], rectangle2[1]))
    return x_overlap * y_overlap


annotations_path = '.' + os.path.sep + 'dataset' + os.path.sep + 'Annotations' + os.path.sep
solution = {}
# region for loop that goes through given solution, and constructs a dictionary where the name of every image is paired
# with all RBC rectangles in said image
for image_path in glob.glob(annotations_path + "*.xml"):
    image_directory, image_name = os.path.split(image_path)
    tree = ET.parse(image_path)
    root = tree.getroot()
    objects = root.findall('object')
    rectangles = []
    for instance in objects:
        rectangle = instance.find('bndbox')
        xmin = int(rectangle.find('xmin').text)
        ymin = int(rectangle.find('ymin').text)
        xmax = int(rectangle.find('xmax').text)
        ymax = int(rectangle.find('ymax').text)
        rectangles.append([xmin, ymin, xmax, ymax])
    solution[image_name[:-4]] = rectangles
# endregion

# region constructing dictionary out of my results
my_results = {}
filepath = 'results.txt'
with open(filepath) as file:
    for line in file:
        split = line.split(';')
        coordinates = split[1].split(',')[:-1]
        rectangles = []
        for rectangle in coordinates:
            points = rectangle.strip().split(' ')
            rectangles.append([int(points[0]), int(points[1]), int(points[2]), int(points[3])])
        my_results[split[0][:-4]] = rectangles
# endregion

file = open("score.txt", "w")
file.truncate()
total_recall = 0
total_precision = 0
total_images = 0
for name in solution.keys():
    matching_rectangles = 0
    correct_results = solution[name]
    for rectangle in my_results[name]:
        for correct_rectangle in correct_results:
            o_a = overlapping_area(rectangle, correct_rectangle)
            area1 = (rectangle[2] - rectangle[0]) * (rectangle[3] - rectangle[1])
            area2 = (correct_rectangle[2] - correct_rectangle[0]) * (correct_rectangle[3] - correct_rectangle[1])
            combined_area = area1 + area2 - o_a
            if o_a/combined_area > 0.5:
                matching_rectangles += 1
                break
    precision = matching_rectangles / len(my_results[name])
    recall = matching_rectangles / len(correct_results)
    total_precision += precision
    total_recall += recall
    total_images += 1
    file.write(name + ': mine: ' + str(len(my_results[name])) + ',correct: ' + str(len(correct_results)) +
               ',matched:' + str(matching_rectangles) + ' PRECISION: ' + str(precision) + ' RECALL: ' + str(recall) +
               '\n')
file.close()
average_precision = total_precision/total_images
average_recall = total_recall/total_images
print('Average precision: ' + str(average_precision) + ' Average recall: ' + str(average_recall))
