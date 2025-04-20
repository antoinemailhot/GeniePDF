import cv2
import numpy as np
import pytesseract

def correct_orientation(pil_img):
    # Conversion PIL → OpenCV
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # ── Étape 1 : orientation large (0/90/180/270) ──
    osd = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
    angle = osd["rotate"]           # ex. 90, 180, 270, 0
    if angle != 0:
        # sens inversé pour cv2.rotate
        angle = 360 - angle
        # rotation autour du centre
        (h, w) = img.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)

    # ── Étape 2 : dé‑skew fin (optionnel, voir §2) ──
    img = deskew(img)

    # Retourne en PIL si besoin
    from PIL import Image
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def deskew(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # Seuillage binaire
    _, bw = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Recherche des contours → boîtes
    coords = np.column_stack(np.where(bw > 0))
    angle  = cv2.minAreaRect(coords)[-1]
    # minAreaRect renvoie un angle dans [-90, 0]
    if angle < -45:  # convertit en degrés classiques
        angle = -(90 + angle)
    else:
        angle = -angle
    # Si l’angle est inférieur à 0,5 °, on ignore
    if abs(angle) < .5:
        return cv_img
    (h, w) = cv_img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    return cv2.warpAffine(cv_img, M, (w, h),
                          flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)

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
    image = correct_orientation(image)
    
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpen = cv2.filter2D(thresh, -1, sharpen_kernel)
    resized = cv2.resize(sharpen, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    return resized



