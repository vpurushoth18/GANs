# helper functions for saving sample data and models

# import data loading libraries
import os
import pdb
import pickle
import argparse

import warnings
warnings.filterwarnings("ignore")

# import torch
import torch

# numpy & image saving imports
import numpy as np
import imageio.v2 as imageio  # ✅ use imageio instead of scipy.misc

def checkpoint(iteration, G_XtoY, G_YtoX, D_X, D_Y, checkpoint_dir='checkpoints_cyclegan'):
    """Saves the parameters of both generators G_YtoX, G_XtoY and discriminators D_X, D_Y."""
    G_XtoY_path = os.path.join(checkpoint_dir, 'G_XtoY.pkl')
    G_YtoX_path = os.path.join(checkpoint_dir, 'G_YtoX.pkl')
    D_X_path = os.path.join(checkpoint_dir, 'D_X.pkl')
    D_Y_path = os.path.join(checkpoint_dir, 'D_Y.pkl')
    torch.save(G_XtoY.state_dict(), G_XtoY_path)
    torch.save(G_YtoX.state_dict(), G_YtoX_path)
    torch.save(D_X.state_dict(), D_X_path)
    torch.save(D_Y.state_dict(), D_Y_path)

def merge_images(sources, targets, batch_size=16):
    """Creates a grid consisting of source-target image pairs."""
    _, _, h, w = sources.shape
    row = int(np.sqrt(batch_size))
    merged = np.zeros([3, row*h, row*w*2])
    for idx, (s, t) in enumerate(zip(sources, targets)):
        i = idx // row
        j = idx % row
        merged[:, i*h:(i+1)*h, (j*2)*w:(j*2+1)*w] = s
        merged[:, i*h:(i+1)*h, (j*2+1)*w:(j*2+2)*w] = t
    merged = merged.transpose(1, 2, 0)
    return merged

# def to_data(x):
#     """Converts tensor to uint8 numpy array."""
#     if torch.cuda.is_available():
#         x = x.cpu()
#     x = x.data.numpy()
#     x = ((x + 1) * 255 / 2).astype(np.uint8)
#     return x

def to_data(x):
    """Converts tensor to uint8 numpy array with shape (N, C, H, W)."""
    if torch.is_tensor(x):
        x = x.detach().cpu().float()
    x = x.numpy()
    x = np.clip((x + 1) * 127.5, 0, 255)  # map [-1, 1] to [0, 255]
    x = x.astype(np.uint8)
    return x

# def save_samples(iteration, fixed_Y, fixed_X, G_YtoX, G_XtoY, batch_size=16, sample_dir='samples_cyclegan'):

#     """Saves samples from both generators X->Y and Y->X."""
#     os.makedirs(sample_dir, exist_ok=True)
#     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#     fake_X = G_YtoX(fixed_Y.to(device))
#     fake_Y = G_XtoY(fixed_X.to(device))
    
#     X, fake_X = to_data(fixed_X), to_data(fake_X)
#     Y, fake_Y = to_data(fixed_Y), to_data(fake_Y)

#     merged = merge_images(X, fake_Y, batch_size)
#     path = os.path.join(sample_dir, 'sample-{:06d}-X-Y.png'.format(iteration))
#     imageio.imwrite(path, merged)  # ✅ updated
#     print('Saved {}'.format(path))

#     merged = merge_images(Y, fake_X, batch_size)
#     path = os.path.join(sample_dir, 'sample-{:06d}-Y-X.png'.format(iteration))
#     imageio.imwrite(path, merged)  # ✅ updated
#     print('Saved {}'.format(path))

def save_samples(iteration, fixed_Y, fixed_X, G_YtoX, G_XtoY, batch_size=16, sample_dir='samples_cyclegan'):
    os.makedirs(sample_dir, exist_ok=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    G_XtoY.eval()
    G_YtoX.eval()
    with torch.no_grad():
        fake_X = G_YtoX(fixed_Y.to(device))
        fake_Y = G_XtoY(fixed_X.to(device))

    X, fake_X = to_data(fixed_X), to_data(fake_X)
    Y, fake_Y = to_data(fixed_Y), to_data(fake_Y)

    merged = merge_images(X, fake_Y, batch_size)
    path = os.path.join(sample_dir, 'sample-{:06d}-X-Y.png'.format(iteration))
    imageio.imwrite(path, merged)
    print('Saved {}'.format(path))

    merged = merge_images(Y, fake_X, batch_size)
    path = os.path.join(sample_dir, 'sample-{:06d}-Y-X.png'.format(iteration))
    imageio.imwrite(path, merged)
    print('Saved {}'.format(path))

    G_XtoY.train()
    G_YtoX.train()

