import cv2


def draw(img, x, y):
    for i in range(4):
        if i < 4:
            cv2.circle(img, (int(x[i]), int(y[i])), 3, (255, 255, 0), -1)
        else:
            cv2.circle(img, (int(x[i]), int(y[i])), 3, (0, 0, 255), -1)
    return img
