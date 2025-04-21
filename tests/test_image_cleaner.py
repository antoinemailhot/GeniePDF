import numpy as np
from src.pdf_tools import image_cleaner
from PIL import Image

def test_preprocess_returns_numpy(dummy_images):
    result = image_cleaner.preprocess(dummy_images[0])
    assert isinstance(result, (np.ndarray, Image.Image))
