import cv2
import numpy as np

def preprocess(image):
    """
    Prétraite une image pour améliorer les résultats de l'OCR.
    
    :param image: L'image à prétraiter.
    :return: L'image prétraitée, prête pour l'OCR.
    """
    """   # Conversion en niveau de gris
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Application d'un flou pour réduire le bruit
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    
    # Application de la méthode de seuillage pour rendre le texte plus net
    threshold_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # (Optionnel) Amélioration de la netteté de l'image
    sharpened_image = cv2.addWeighted(threshold_image, 1.5, threshold_image, -0.5, 0)
    
    return sharpened_image """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpen = cv2.filter2D(thresh, -1, sharpen_kernel)
    resized = cv2.resize(sharpen, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    return resized