# import libraries here
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
import sys
import os


def intersection(first_circle_radius, second_circle_radius, distance):
    distance_1 = (first_circle_radius**2 - second_circle_radius**2 + distance**2)/(2*distance)
    distance_2 = (distance - distance_1)

    if distance < abs(first_circle_radius - second_circle_radius):
        return np.pi * min(first_circle_radius**2, second_circle_radius**2)
    else:
        return first_circle_radius**2 * np.arccos(distance_1 / first_circle_radius) - distance_1 * \
               np.sqrt(first_circle_radius**2 - distance_1**2) + second_circle_radius**2 * \
               np.arccos(distance_2 / second_circle_radius) - distance_2 * \
               np.sqrt(second_circle_radius**2 - distance_2**2)


def save_image(image_path, image_name, file):

    blood_image = cv2.imread(image_path)
    area_of_image = blood_image.shape[0] * blood_image.shape[1]
    blood_image = cv2.cvtColor(blood_image, cv2.COLOR_BGR2RGB)
    bw_image = cv2.cvtColor(blood_image, cv2.COLOR_RGB2GRAY)
    binary_image = cv2.adaptiveThreshold(bw_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 405, 5)
    kernel = np.ones((3, 3))
    dilated_image = cv2.dilate(binary_image, kernel, iterations=3)
    dilated_image = (255 - dilated_image)

    # region Trazenje WBC na osnovu plave boje
    image_for_wbc = blood_image[:, :, 2] < 209
    image_for_wbc = image_for_wbc.astype(binary_image.dtype)*255
    image_for_wbc = cv2.adaptiveThreshold(image_for_wbc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 405, 5)
    image_for_wbc = cv2.dilate(image_for_wbc, kernel, iterations=3)
    image_for_wbc = (255 - image_for_wbc)

    _, figures, _ = cv2.findContours(image_for_wbc, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    output_image = blood_image.copy()
    white_blood_cells = []
    i = 0
    while i < len(figures):
        figure = figures[i]
        area = cv2.contourArea(figure)
        cv2.drawContours(output_image, [figure], 0, (0, 0, 255), 3)
        if area / area_of_image > 0.15 or area / area_of_image < 0.003:
            i += 1
            continue
        c, r = cv2.minEnclosingCircle(figure)
        white_blood_cells.append((c, r))
        i += 1

    blood_cell_rectangles = []
    i = 0
    while i < len(white_blood_cells):
        cell_bounding_circle = white_blood_cells[i]
        c = cell_bounding_circle[0]
        r = cell_bounding_circle[1]
        x_min = c[0] - r
        y_min = c[1] - r
        x_max = c[0] + r
        y_max = c[1] + r
        blood_cell_rectangles.append([x_min, y_min, x_max, y_max])
        i += 1

    for rectangle in blood_cell_rectangles:
        cv2.rectangle(blood_image, (int(rectangle[0]), int(rectangle[1])), (int(rectangle[2]), int(rectangle[3])),
                      (0, 0, 255), 2)
    # endregion

    _, figures, _ = cv2.findContours(dilated_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    output_image = blood_image.copy()
    circles = []

    i = 0
    while i < len(figures):
        figure = figures[i]
        area = cv2.contourArea(figure)
        if area / area_of_image < 0.003 or area / area_of_image > 0.15:
            i += 1
            continue
        c, r = cv2.minEnclosingCircle(figure)
        circles.append((c, r))
        i += 1

    circles_copy = circles.copy()
    avg_area = 0
    for cell_bounding_circle in circles_copy:
        avg_area += cell_bounding_circle[1]**2 * np.pi
    avg_area /= len(circles)
    for cell_bounding_circle in circles_copy:
        area = cell_bounding_circle[1]**2 * np.pi
        if area < 0.2 * avg_area:
            circles.remove(cell_bounding_circle)

    circles_copy = circles.copy()
    for cell_bounding_circle in circles_copy:
        c = cell_bounding_circle[0]
        r = cell_bounding_circle[1]
        area = r**2 * np.pi
        covered_area = 0
        for b_circle in white_blood_cells:
            bc = b_circle[0]
            br = b_circle[1]
            # distance between centers
            distance = np.sqrt((c[0] - bc[0])**2 + (c[1] - bc[1])**2)
            if distance < r + br:
                covered_area += intersection(r, br, distance)
        if covered_area / area > 0.2:
            circles.remove(cell_bounding_circle)

    circles_copy = circles.copy()
    i = 0
    while i < len(circles_copy):
        circle1 = circles_copy[i]
        c1 = circle1[0]
        j = 0
        while j < len(circles_copy):
            circle2 = circles_copy[j]
            c2 = circle2[0]
            distance = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
            if distance + circle1[1] < circle2[1]:
                j += 1
                circles.remove(circle1)
                break
            j += 1
        i += 1

    blood_cell_rectangles = []
    for cell_bounding_circle in circles:
        c = cell_bounding_circle[0]
        r = cell_bounding_circle[1]
        x_min = max(0, int(c[0] - r))
        y_min = max(0, int(c[1] - r))
        x_max = min(blood_image.shape[1], int(c[0] + r))
        y_max = min(blood_image.shape[0], int(c[1] + r))
        blood_cell_rectangles.append([x_min, y_min, x_max, y_max])

    file.write(image_name + '; ')
    for rec in blood_cell_rectangles:
        file.write(str(rec[0]) + ' ' + str(rec[1]) + ' ' + str(rec[2]) + ' ' + str(rec[3]) + ',')
    file.write('\n')

    for rectangle in blood_cell_rectangles:
        cv2.rectangle(output_image, (int(rectangle[0]), int(rectangle[1])), (int(rectangle[2]), int(rectangle[3])), (255, 0, 0), 2)

    write_location = '.' + os.path.sep + 'results' + os.path.sep + image_name
    output_image = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(write_location, output_image)


if __name__ == "__main__":
    file = open("results.txt", "w")
    file.truncate()
    dataset = '.' + os.path.sep + 'dataset' + os.path.sep + 'JPEGImages' + os.path.sep

    processed_image_names = []
    red_blood_cell_counts = []

    for image_path in glob.glob(dataset + "*.jpg"):
        image_directory, image_name = os.path.split(image_path)
        processed_image_names.append(image_name)
        red_blood_cell_counts.append(save_image(image_path, image_name, file))

    file.close()
