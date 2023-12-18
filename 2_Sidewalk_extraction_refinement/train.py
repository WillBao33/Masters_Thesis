import os
import cv2
import pandas as pd
import random
import tqdm
#import seaborn as sns 
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import albumentations as A
import segmentation_models_pytorch as smp
import numpy as np
import segmentation_models_pytorch.utils.losses
from torchvision import transforms
torch.cuda.empty_cache()

DATA_DIR = "/home_2TB/william/Segmentation-Models/" # parent directory to dataset

x_train_dir = os.path.join(DATA_DIR, 'image/train') # train image set
y_train_dir = os.path.join(DATA_DIR, 'mask/train')  # train mask set

x_valid_dir = os.path.join(DATA_DIR, 'image/val')   # validation image set
y_valid_dir = os.path.join(DATA_DIR, 'mask/val')    # validation mask set

x_test_dir = os.path.join(DATA_DIR, 'image/test')   # test image set
y_test_dir = os.path.join(DATA_DIR, 'mask/test')    # test mask set
#print(len(os.listdir(x_valid_dir)))
class_dict = pd.read_csv("label_class_dict.csv")  # labels
class_names = class_dict['name'].tolist()
class_rgb_values = class_dict[['r','g','b']].values.tolist()
select_classes = ['background', 'sidewalk']
select_class_indices = [class_names.index(cls.lower()) for cls in select_classes]
select_class_rgb_values =  np.array(class_rgb_values)[select_class_indices]
def visualize(**images):
    """
    Plot images in one row
    """
    n_images = len(images)
    plt.figure(figsize=(20,8))
    for idx, (name, image) in enumerate(images.items()):
        plt.subplot(1, n_images, idx + 1)
        plt.xticks([]); 
        plt.yticks([])
        # get title from the parameter names
        plt.title(name.replace('_',' ').title(), fontsize=20)
        plt.imshow(image)
    plt.show()

def one_hot_encode(label, label_values):
    """
    Convert a segmentation image label array to one-hot format
    by replacing each pixel value with a vector of length num_classes
    # Arguments
        label: The 2D array segmentation image label
        label_values
        
    # Returns
        A 2D array with the same width and hieght as the input, but
        with a depth size of num_classes
    """
    semantic_map = []
    for colour in label_values:
        equality = np.equal(label, colour)
        class_map = np.all(equality, axis = -1)
        semantic_map.append(class_map)
    semantic_map = np.stack(semantic_map, axis=-1)

    return semantic_map

def reverse_one_hot(image):
    """
    Transform a 2D array in one-hot format (depth is num_classes),
    to a 2D array with only 1 channel, where each pixel value is
    the classified class key.
    # Arguments
        image: The one-hot format image 
        
    # Returns
        A 2D array with the same width and hieght as the input, but
        with a depth size of 1, where each pixel value is the classified 
        class key.
    """
    x = np.argmax(image, axis = -1)
    return x

def colour_code_segmentation(image, label_values):
    """
    Given a 1-channel array of class keys, colour code the segmentation results.
    # Arguments
        image: single channel array where each value represents the class key.
        label_values

    # Returns
        Colour coded image for segmentation visualization
    """
    colour_codes = np.array(label_values)
    x = colour_codes[image.astype(int)]

    return x

class BuildingsDataset(torch.utils.data.Dataset):

    """Sidewalk Dataset. Read images, apply augmentation and preprocessing transformations.
    
    Args:
        images_dir (str): path to images folder
        masks_dir (str): path to segmentation masks folder
        class_rgb_values (list): RGB values of select classes to extract from segmentation mask
        augmentation (albumentations.Compose): data transfromation pipeline 
            (e.g. flip, scale, etc.)
        preprocessing (albumentations.Compose): data preprocessing 
            (e.g. noralization, shape manipulation, etc.)
    
    """
    
    def __init__(
            self, 
            images_dir, 
            masks_dir, 
            class_rgb_values=None, 
            augmentation=None, 
            preprocessing=None,
    ):
        
        self.image_paths = [os.path.join(images_dir, image_id) for image_id in sorted(os.listdir(images_dir))]
        self.mask_paths = [os.path.join(masks_dir, image_id) for image_id in sorted(os.listdir(masks_dir))]

        self.class_rgb_values = class_rgb_values
        self.augmentation = augmentation
        self.preprocessing = preprocessing
    
    def __getitem__(self, i):
        
        # read images and masks
        image = cv2.cvtColor(cv2.imread(self.image_paths[i]), cv2.COLOR_BGR2RGB)
        mask = cv2.cvtColor(cv2.imread(self.mask_paths[i]), cv2.COLOR_BGR2RGB)
        
        # one-hot-encode the mask
        mask = one_hot_encode(mask, self.class_rgb_values).astype('float')
        
        # apply augmentations
        if self.augmentation:
            sample = self.augmentation(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']
        
        # apply preprocessing
        if self.preprocessing:
            sample = self.preprocessing(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']
            
        return image, mask
        
    def __len__(self):
        # return length of 
        return len(self.image_paths)
    
# dataset = BuildingsDataset(x_train_dir, y_train_dir, class_rgb_values=select_class_rgb_values)
# random_idx = random.randint(0, len(dataset)-1)
# image, mask = dataset[1]

# visualize(
#     original_image = image,
#     ground_truth_mask = colour_code_segmentation(reverse_one_hot(mask), select_class_rgb_values),
#     one_hot_encoded_mask = reverse_one_hot(mask)
# )

def get_training_augmentation():
    train_transform = [    
        #A.RandomCrop(height=256, width=256, always_apply=True),
        A.PadIfNeeded(min_height=896, min_width=1856,always_apply=True),
        # A.RandomBrightnessContrast(p=0.5),
        # A.HueSaturationValue(p=0.5),
        # A.RandomGamma(p=0.5),
        #A.Resize(height=224, width=224),
        A.Rotate(limit=35,p=1.0),
        
    ]
    return A.Compose(train_transform)

def get_validation_augmentation():   
    # Add sufficient padding to ensure image is divisible by 32
    test_transform = [
        A.PadIfNeeded(min_height=896, min_width=1856, always_apply=True),
        #A.Resize(height=224, width=224),
    ]
    return A.Compose(test_transform)

def to_tensor(x, **kwargs):
    return x.transpose(2, 0, 1).astype('float32')

def get_preprocessing(preprocessing_fn=None):
    """Construct preprocessing transform    
    Args:
        preprocessing_fn (callable): data normalization function 
            (can be specific for each pretrained neural network)
    Return:
        transform: albumentations.Compose
    """   
    _transform = []
    if preprocessing_fn:
        _transform.append(A.Lambda(image=preprocessing_fn))
    _transform.append(A.Lambda(image=to_tensor, mask=to_tensor))
        
    return A.Compose(_transform)

# augmented_dataset = BuildingsDataset(
#     x_train_dir, y_train_dir, 
#     augmentation=get_training_augmentation(),
#     class_rgb_values=select_class_rgb_values,
# )

#random_idx = random.randint(0, len(augmented_dataset)-1)

# Different augmentations on a random image/mask pair (256*256 crop)
# for i in range(3):
#     image, mask = augmented_dataset[random_idx]
#     visualize(
#         original_image = image,
#         ground_truth_mask = colour_code_segmentation(reverse_one_hot(mask), select_class_rgb_values),
#         one_hot_encoded_mask = reverse_one_hot(mask)
#     )

ENCODER = 'resnet152'
ENCODER_WEIGHTS = 'imagenet'
CLASSES = class_names
#ACTIVATION = 'softmax2d' # could be None for logits or 'softmax2d' for multiclass segmentation
ACTIVATION = 'sigmoid'

# create segmentation model with pretrained encoder
# model = smp.Unet(
#     encoder_name=ENCODER, 
#     encoder_weights=ENCODER_WEIGHTS, 
#     classes=len(CLASSES), 
#     activation=ACTIVATION,
# )

#model = smp.DeepLabV3Plus(encoder_name=ENCODER,encoder_weights=ENCODER_WEIGHTS,classes=len(CLASSES),activation=ACTIVATION)
model = smp.UnetPlusPlus(encoder_name=ENCODER,encoder_weights=ENCODER_WEIGHTS,classes=len(CLASSES),activation=ACTIVATION)
#model = smp.FPN(encoder_name=ENCODER,encoder_weights=ENCODER_WEIGHTS,classes=len(CLASSES),activation=ACTIVATION)
#model = smp.DeepLabV3(encoder_name=ENCODER,encoder_weights=ENCODER_WEIGHTS,classes=len(CLASSES),activation=ACTIVATION)
#model = smp.PSPNet(encoder_name=ENCODER,encoder_weights=ENCODER_WEIGHTS,classes=len(CLASSES),activation=ACTIVATION)
#model = smp.PAN(encoder_name=ENCODER,encoder_weights=ENCODER_WEIGHTS,classes=len(CLASSES),activation=ACTIVATION)
preprocessing_fn = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)

train_dataset = BuildingsDataset(
    x_train_dir, y_train_dir, 
    augmentation=get_training_augmentation(),
    preprocessing=get_preprocessing(preprocessing_fn),
    class_rgb_values=select_class_rgb_values,
)

valid_dataset = BuildingsDataset(
    x_valid_dir, y_valid_dir, 
    augmentation=get_validation_augmentation(), 
    preprocessing=get_preprocessing(preprocessing_fn),
    class_rgb_values=select_class_rgb_values,
)

# Get train and val data loaders
train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True, num_workers=12)
valid_loader = DataLoader(valid_dataset, batch_size=1, shuffle=False, num_workers=4)

TRAINING = True

# Set num of epochs
EPOCHS = 20

# Set device: `cuda` or `cpu`
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# define loss function
loss = smp.utils.losses.DiceLoss()

# define metrics
metrics = [
    smp.utils.metrics.IoU(threshold=0.5),
]

# define optimizer
optimizer = torch.optim.Adam([ 
    dict(params=model.parameters(), lr=0.0001,weight_decay=0.1),
])

# define learning rate scheduler (not used in this NB)
lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=1, T_mult=2, eta_min=5e-5,
)

# load best saved model checkpoint from previous commit (if present)
# if os.path.exists('/home_2TB/william/Segmentation-Models/pth/UNet++/best_model.pth'):
#     model = torch.load('/home_2TB/william/Segmentation-Models/pth/UNet++/best_model.pth', map_location=DEVICE)


train_epoch = smp.utils.train.TrainEpoch(
    model, 
    loss=loss, 
    metrics=metrics, 
    optimizer=optimizer,
    device=DEVICE,
    verbose=True,
)

valid_epoch = smp.utils.train.ValidEpoch(
    model, 
    loss=loss, 
    metrics=metrics, 
    device=DEVICE,
    verbose=True,
)

if TRAINING:

    best_iou_score = 0.0
    lowest_loss = 1.0
    train_logs_list, valid_logs_list = [], []

    for i in range(0, EPOCHS):

        # Perform training & validation
        print('\nEpoch: {}'.format(i))
        train_logs = train_epoch.run(train_loader)
        valid_logs = valid_epoch.run(valid_loader)
        train_logs_list.append(train_logs)
        valid_logs_list.append(valid_logs)

        # Save model if a better val dice loss is obtained
        if lowest_loss > valid_logs['dice_loss']:
            lowest_loss = valid_logs['dice_loss']
            torch.save(model, 'pth/paper/UNet++_no_aug_weight_dec/best_model.pth') # adjust the output path for trained model
            print('Model saved!')

        train_df = pd.DataFrame(train_logs_list)
        val_df = pd.DataFrame(valid_logs_list)
        train_df.to_csv('/home_2TB/william/Segmentation-Models/pth/paper/UNet++_no_aug_weight_dec/train_log.csv',index=False) # adjust the output log path
        val_df.to_csv('/home_2TB/william/Segmentation-Models/pth/paper/UNet++_no_aug_weight_dec/val_log.csv',index=False) # adjust the output log path

# codes below is for inferencing on the test dataset

# if os.path.exists('/home_2TB/william/Segmentation-Models/pth/TrivialAugWide/best_model.pth'):
#     best_model = torch.load('/home_2TB/william/Segmentation-Models/pth/TrivialAugWide/best_model.pth', map_location=DEVICE)
#     print('Loaded UNet++ model from this run.')

# test_dataset = BuildingsDataset(
#     x_test_dir, 
#     y_test_dir, 
#     augmentation=get_validation_augmentation(), 
#     preprocessing=get_preprocessing(preprocessing_fn),
#     class_rgb_values=select_class_rgb_values,
# )

# test_dataloader = DataLoader(test_dataset)

# # test dataset for visualization (without preprocessing transformations)
# test_dataset_vis = BuildingsDataset(
#     x_test_dir, y_test_dir, 
#     augmentation=get_validation_augmentation(),
#     class_rgb_values=select_class_rgb_values,
# )

# # get a random test image/mask index
# random_idx = random.randint(0, len(test_dataset_vis)-1)
# image, mask = test_dataset_vis[random_idx]


# sample_preds_folder = '/home_2TB/william/Segmentation-Models/pth/TrivialAugWide/prediction/'
# if not os.path.exists(sample_preds_folder):
#     os.makedirs(sample_preds_folder)

# for idx in range(len(test_dataset)):

#     image, gt_mask = test_dataset[idx]
#     image_vis = test_dataset_vis[idx][0].astype('uint8')
#     x_tensor = torch.from_numpy(image).to(DEVICE).unsqueeze(0)
#     # Predict test image
#     pred_mask = best_model(x_tensor)
#     pred_mask = pred_mask.detach().squeeze().cpu().numpy()
#     # Convert pred_mask from `CHW` format to `HWC` format
#     pred_mask = np.transpose(pred_mask,(1,2,0))
#     # Get prediction channel corresponding to building
#     pred_building_heatmap = pred_mask[:,:,select_classes.index('sidewalk')]
#     pred_mask = colour_code_segmentation(reverse_one_hot(pred_mask), select_class_rgb_values)
#     # Convert gt_mask from `CHW` format to `HWC` format
#     gt_mask = np.transpose(gt_mask,(1,2,0))
#     gt_mask = colour_code_segmentation(reverse_one_hot(gt_mask), select_class_rgb_values)
#     #cv2.imwrite(os.path.join(sample_preds_folder, f"sample_pred_{idx}.png"), np.hstack([image_vis, gt_mask, pred_mask])[:,:,::-1])
#     cv2.imwrite(os.path.join(sample_preds_folder, f"image_{idx}.png"),image_vis[:,:,::-1])
#     cv2.imwrite(os.path.join(sample_preds_folder, f"gt_{idx}.png"),gt_mask)
#     cv2.imwrite(os.path.join(sample_preds_folder, f"pred_{idx}.png"),pred_mask)
    
#     visualize(
#         original_image = image_vis,
#         ground_truth_mask = gt_mask,
#         predicted_mask = pred_mask,
#         predicted_building_heatmap = pred_building_heatmap
#     )
