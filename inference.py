import torch
import torchvision
from torchvision.models import vgg11_bn
from torchvision import datasets, models, transforms
from PIL import Image
import os

from split_stitch import split_file

PATH_TO_STATE_DICT = 'RECONSTRUCTED_Trained_Model/model.statedict'
PATH_TO_MODEL = 'RECONSTRUCTED_Trained_Model/model.model'
PATH_TO_VALIDATION_IMAGES = 'VALIDATION_IMAGES/'

IMG_EXTENSIONS = ('.jpg', '.png', '.jpeg', '.bmp', '.gif', '.ppm')

CLASSES = ['shaver', 'smart-baby-bottle', 'toothbrush', 'wake-up-light']

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

print('Device is {} so it seems that cuda is '.format(device), end='')
if device.type != 'cpu':
    print('available. Using GPU for inference.')
else:
    print('not available. Using CPU for inference. This might take a bit longer.')

# stitch_file('Chunks_for_Trained_Model_model.statedict/', 'RECONSTRUCTED_Trained_Model/model.statedict')


print('Loading Model... Please be patient. Thanks!')
try:
    assert(False)
    model = vgg11_bn(pretrained=False)
    model.classifier[-1] = torch.nn.Linear(in_features=4096, out_features=4, bias=True)
    model.load_state_dict(torch.load(PATH_TO_STATE_DICT, map_location=device))
except:
    print('WARNING: Loading model from statedict failed. Attempting to load whole model directly instead.')
    model = torch.load(PATH_TO_MODEL, map_location=device)
model.eval()
print('Model loaded.\nDefining image transformations...')

loader = transforms.Compose([
    transforms.Resize(size=(260, 350)),
    transforms.CenterCrop(size=(250, 340)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print('Transforms defined.\nStarting inference now.\n'
      'Note that images will probably be loaded and evaluated in alphabetical order,'
      ' meaning that that an image named "IMG10.jpg" might be evaluated BEFORE one named "IMG9.jpg"')

output = ""
wrong=""
right=""
wrong_c=0
right_c=0
for filename in os.listdir(PATH_TO_VALIDATION_IMAGES):
    if not filename.lower().endswith(IMG_EXTENSIONS):
        print(
            '{} does not appear to be an image and will be skipped. If it is an image, please make sure it has one of '
            'the following file extensions: {}'.format(filename, IMG_EXTENSIONS))
        continue
    result_string = "{FILENAME} - ".format(FILENAME=filename)
    print(result_string, end='')

    try:
        img_og = Image.open(PATH_TO_VALIDATION_IMAGES + filename)
    except:
        print('WARNING: PIL failed to load {}. Skipping this file.'.format(filename))
        continue

    try:
        img = loader(img_og).float()
        img = img.unsqueeze(0)
        img = img.to(device)
        outputs = model(img)
    except:
        print('WARNING: Transforming {} failed. Skipping this file.'.format(filename))
        continue

    img = transforms.functional.hflip(img_og)
    img = loader(img).float()
    img = img.unsqueeze(0)
    img = img.to(device)
    outputs += model(img)

    img = transforms.functional.vflip(img_og)
    img = loader(img).float()
    img = img.unsqueeze(0)
    img = img.to(device)
    outputs += model(img)

    img = transforms.functional.vflip(img_og)
    img = transforms.functional.hflip(img)
    img = loader(img).float()
    img = img.unsqueeze(0)
    img = img.to(device)
    outputs += model(img)

    _, preds = torch.max(outputs, 1)
    predicted = CLASSES[preds]

    if not predicted in filename:
        wrong+=filename
        wrong+='\n'
        wrong_c +=1
    else:
        right+=filename
        right+='\n'
        right_c +=1

    result_string += "{CLASS}\n".format(CLASS=predicted)
    print("{CLASS}\n".format(CLASS=predicted), end='')

    output += result_string

print('Finished with all images.\nWriting results to "validation_output.txt".')

with open("validation_output.txt", "w") as output_file:
    output_file.write(output)

print('Output file created.\nScript Finished.')

print(right_c/(wrong_c+right_c)*100)

print(wrong)
print('++++++++++')
print(right)