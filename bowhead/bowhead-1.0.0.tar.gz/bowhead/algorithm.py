import numpy as np
from scipy import ndimage
from skimage.measure import find_contours, perimeter
from PIL import Image, ImageFilter


def _load(image):
    if isinstance(image, str):
        image = Image.open(image)
    elif isinstance(image, np.ndarray):
        if len(image.shape) > 2:
            image = np.sum(image, -1)
        image = Image.fromarray(image)
    if not hasattr(image, 'filename'):
        image.filename = None
    filename = image.filename
    image = image.convert('I')
    image.filename = filename
    return image

def _detect(image, sigma, threshold, zone=None, primary=None):
    if primary is None:
        smooth = ndimage.filters.gaussian_filter(image, sigma)
        smooth = np.asarray(smooth, dtype=np.float)
        confluency = (smooth**2).sum() / smooth.sum()
    else:
        smooth, confluency = primary['smooth'], primary['confluency']
    binary = ndimage.binary_fill_holes(smooth < threshold * confluency)
    label, count = ndimage.label(binary)
    index = range(1, count+1)
    cms = ndimage.measurements.center_of_mass(binary, label, index)
    mass = ndimage.sum(binary, label, index)
    objects = sorted(zip(cms, mass, index), key=lambda x: x[1])
    for obj in reversed(objects):
        if zone:
            dist = np.linalg.norm(np.array(obj[0])-np.array(zone[0]))
            if dist > zone[1]:
                continue
        cm = obj[0]
        area = obj[1]
        woundzone = label==obj[2]
        edge, perimeter = _contour(woundzone)
        return {'filename': image.filename,
                'woundzone': woundzone,
                'area': area,
                'center_of_mass': cm, 
                'edge': edge,
                'perimeter': perimeter,   
                'image_area': np.prod(image.size),
                'smooth': smooth,
                'confluency': confluency,}

def _contour(wound):
    mask = np.zeros_like([s-1 for s in wound.shape])
    mask = np.pad(mask, pad_width=1, mode='constant', constant_values=1)
    mask = np.pad(mask, pad_width=1, mode='constant', constant_values=0)
    wound = np.pad(wound, pad_width=1, mode='constant', constant_values=0)
    contours = find_contours(wound, level=.5)
    if len(contours) > 1:
        raise ValueError('more than one wound contour were detected')
    x, y = np.transpose(contours[0]-1)
    stucco = np.sum(wound[mask]) 
    return (x, y) , perimeter(wound) - stucco
