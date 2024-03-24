import numpy as np
import torch
import cv2
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from scipy.ndimage import zoom
from scipy.special import logsumexp

import deepgaze_pytorch

BLACK_PIXEL_PERCENTAGE = 0.90
SALIENCY_THRESHOLD = 0.70
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
model = deepgaze_pytorch.DeepGazeIIE(pretrained=True).to(DEVICE)


def saliency(image, thresh=SALIENCY_THRESHOLD):
    centerbias_template = np.load('centerbias_mit1003.npy')
    centerbias = zoom(centerbias_template,
                      (image.shape[0] / centerbias_template.shape[0], image.shape[1] / centerbias_template.shape[1]),
                      order=0, mode='nearest')
    centerbias -= logsumexp(centerbias)
    centerbias_tensor = torch.from_numpy(centerbias).to(DEVICE).unsqueeze(0)

    image_tensor = torch.from_numpy(image.transpose(2, 0, 1)).to(DEVICE).unsqueeze(0)

    log_density_prediction = model(image_tensor, centerbias_tensor)
    log_density_prediction = log_density_prediction.detach().cpu().numpy()[0, 0]

    min_val = np.min(log_density_prediction)
    max_val = np.max(log_density_prediction)
    normalized_arr_2d = (log_density_prediction - min_val) / (max_val - min_val)
    normalized_arr_2d = np.where(normalized_arr_2d > thresh, 255, 0)
    normalized_arr_2d = normalized_arr_2d.astype(np.uint8)
    return cv2.cvtColor(normalized_arr_2d, cv2.COLOR_GRAY2BGR)


def max_hist(row):
    result = []
    top_val = 0
    max_area = 0
    area = 0
    start = 0
    height = 0

    i = 0
    while i < len(row):
        if (len(result) == 0) or (row[result[-1]] <= row[i]):
            result.append(i)
            i += 1
        else:
            top_val = row[result.pop()]
            area = top_val * i
            if len(result):
                area = top_val * (i - result[-1] - 1)
            if area > max_area:
                max_area = area
                start = result[-1] + 1 if result else 0
                height = top_val

    while len(result):
        top_val = row[result.pop()]
        area = top_val * i
        if len(result):
            area = top_val * (i - result[-1] - 1)
        if area >= max_area:
            max_area = area
            start = result[-1] + 1 if result else 0
            height = top_val

    return max_area, start, height


def max_rectangle(A):
    result = max_hist(A[0])
    max_area, start_row, height = result
    start_col = 0

    for i in range(1, len(A)):
        for j in range(len(A[i])):
            if A[i][j]:
                A[i][j] += A[i - 1][j]
        result = max_hist(A[i])
        area, start, h = result
        if area > max_area:
            max_area = area
            start_row = i - h + 1
            start_col = start
            height = h

    return max_area, start_row, start_col, height


def get_coords(image_rgb):
    height, width, _ = image_rgb.shape
    rows = height // 10
    cols = width // 10
    cell_height = height // rows
    cell_width = width // cols
    ratios = np.zeros((rows, cols), dtype=int)
    for i in range(rows):
        for j in range(cols):
            y1 = i * cell_height
            y2 = (i + 1) * cell_height
            x1 = j * cell_width
            x2 = (j + 1) * cell_width
            cell = image_rgb[y1:y2, x1:x2]
            black_pixels = np.sum(np.all(cell == [0, 0, 0], axis=-1))
            total_pixels = cell.shape[0] * cell.shape[1]
            ratio = black_pixels / total_pixels
            ratios[i, j] = 1 if ratio > BLACK_PIXEL_PERCENTAGE else 0
    max_area, start_row, start_col, height = max_rectangle(ratios.copy())
    tl1 = (start_row, start_col)
    br1 = (start_row + height, start_col + max_area // height)
    for i in range(tl1[0], br1[0]):
        for j in range(tl1[1], br1[1]):
            ratios[i][j] = 0
    max_area, start_row, start_col, height = max_rectangle([row[:] for row in ratios])
    tl2 = (start_row, start_col)
    br2 = (start_row + height, start_col + max_area // height)
    return (tl1[0] * cell_height, tl1[1] * cell_width, br1[0] * cell_height, br1[1] * cell_width), (
    tl2[0] * cell_height, tl2[1] * cell_width, br2[0] * cell_height, br2[1] * cell_width)


def text_details(r):
    width = abs(r[3] - r[1])
    height = abs(r[2] - r[0])
    area = width * height
    # font_size = (0.0062 * area)**(0.5)
    font_size = 19
    num_char = area / (font_size) ** 2
    max_chars = width // (font_size // 2)
    print(font_size, int(num_char), max_chars, width, height)
    return font_size, int(num_char), max_chars


def split_sentence(sentence, max_length=30):
    words = sentence.split(" ")
    chunks = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) <= max_length:
            current_chunk += word + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def get_gpt_response(query, max_length=160):
    client = OpenAI()
    query = f"Summarize within {max_length} characters including spaces (return only the summary) - " + query
    print("Query:", query)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    return completion.choices[0].message.content


def build_html(filename, text, coord):
    with open("template.html", "r") as f:
        soup = BeautifulSoup(f, "html.parser")
    script = soup.find("script")

    new_text_lines = str(text).replace("'", '"')
    new_img_src = f'"{filename}"'
    new_img_des = '"Image_Generated.png"'
    new_x = f'{coord[1] + 10}'
    new_y = f'{coord[0] + 10}'
    print(new_text_lines)
    script.string = script.string.replace('"PLACEHOLDER_text"', new_text_lines)
    script.string = script.string.replace('"PLACEHOLDER_IMGSRC"', new_img_src)
    script.string = script.string.replace('"PLACEHOLDER_IMGDES"', new_img_des)
    script.string = script.string.replace('"PLACEHOLDER_x"', new_x)
    script.string = script.string.replace('"PLACEHOLDER_y"', new_y)
    with open("idk.html", "w") as f:
        f.write(str(soup))


def add_text(image, prompt):
    fn = "Image.png"
    image = np.array(image)
    cv2.imwrite(fn, image)
    image = saliency(image)
    r1, r2 = get_coords(image)
    fs, nc, mc = text_details(r1)
    response = get_gpt_response(prompt, nc)
    response = split_sentence(response, mc)
    print(prompt, response)
    build_html(fn, response, r1)
