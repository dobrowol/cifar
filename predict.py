"""Inference/predict code for CIFAR-100
model must be trained before inference, 
train_cifar10.py must be executed beforehand.
"""
from __future__ import print_function
import os
import argparse

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training, iterators, serializers, optimizers, Variable, cuda
from chainer.training import extensions

from CNNMedium import CNNMedium

CIFAR100_LABELS_LIST = [
    'apple', 'aquarium_fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 'beetle',
    'bicycle', 'bottle', 'bowl', 'boy', 'bridge', 'bus', 'butterfly', 'camel',
    'can', 'castle', 'caterpillar', 'cattle', 'chair', 'chimpanzee', 'clock',
    'cloud', 'cockroach', 'couch', 'crab', 'crocodile', 'cup', 'dinosaur',
    'dolphin', 'elephant', 'flatfish', 'forest', 'fox', 'girl', 'hamster',
    'house', 'kangaroo', 'keyboard', 'lamp', 'lawn_mower', 'leopard', 'lion',
    'lizard', 'lobster', 'man', 'maple_tree', 'motorcycle', 'mountain', 'mouse',
    'mushroom', 'oak_tree', 'orange', 'orchid', 'otter', 'palm_tree', 'pear',
    'pickup_truck', 'pine_tree', 'plain', 'plate', 'poppy', 'porcupine',
    'possum', 'rabbit', 'raccoon', 'ray', 'road', 'rocket', 'rose',
    'sea', 'seal', 'shark', 'shrew', 'skunk', 'skyscraper', 'snail', 'snake',
    'spider', 'squirrel', 'streetcar', 'sunflower', 'sweet_pepper', 'table',
    'tank', 'telephone', 'television', 'tiger', 'tractor', 'train', 'trout',
    'tulip', 'turtle', 'wardrobe', 'whale', 'willow_tree', 'wolf', 'woman',
    'worm'
]


def main():
    archs = {
        'cnnmedium': CNNMedium,
    }

    parser = argparse.ArgumentParser(description='Cifar-100 CNN predict code')
    parser.add_argument('--arch', '-a', choices=archs.keys(),
                        default='cnnmedium', help='Convnet architecture')
    #parser.add_argument('--batchsize', '-b', type=int, default=64,
    #                    help='Number of images in each mini-batch')
    parser.add_argument('--modelpath', '-m', default='result-cifar100-cnnsmall/cnnsmall-cifar100.model',
                        help='Model path to be loaded')
    parser.add_argument('--gpu', '-g', type=int, default=-1,
                        help='GPU ID (negative value indicates CPU)')
    args = parser.parse_args()

    print('GPU: {}'.format(args.gpu))
    #print('# Minibatch-size: {}'.format(args.batchsize))
    print('')

    # 1. Setup model
    class_num = 100
    model = archs[args.arch](n_out=class_num)
    classifier_model = L.Classifier(model)
    if args.gpu >= 0:
        chainer.cuda.get_device(args.gpu).use()  # Make a specified GPU current
        classifier_model.to_gpu()  # Copy the model to the GPU
    xp = np if args.gpu < 0 else cuda.cupy

    serializers.load_npz(args.modelpath, model)

    # 2. Load the CIFAR-10 dataset
    train, test = chainer.datasets.get_cifar100()

    basedir = 'images'
    plot_predict_cifar(os.path.join(basedir, 'cifar100_predict.png'), model,
                       train, 4, 5, scale=5., label_list=CIFAR100_LABELS_LIST)


def plot_predict_cifar(filepath, model, data, row, col,
                       scale=3., label_list=None):
    fig_width = data[0][0].shape[1] / 80 * row * scale
    fig_height = data[0][0].shape[2] / 80 * col * scale
    fig, axes = plt.subplots(row,
                             col,
                             figsize=(fig_height, fig_width))
    for i in range(row * col):
        # train[i][0] is i-th image data with size 32x32
        image, label_index = data[i]
        xp = cuda.cupy
        x = Variable(xp.asarray(image.reshape(1, 3, 32, 32)))    # test data
        #t = Variable(xp.asarray([test[i][1]]))  # labels
        y = model(x)                              # Inference result
        prediction = y.data.argmax(axis=1)
        image = image.transpose(1, 2, 0)
        print('Predicted {}-th image, prediction={}, actual={}'
              .format(i, prediction[0], label_index))
        r, c = divmod(i, col)
        axes[r][c].imshow(image)  # cmap='gray' is for black and white picture.
        if label_list is None:
            axes[r][c].set_title('Predict:{}, Answer: {}'
                                 .format(label_index, prediction[0]))
        else:
            pred = int(prediction[0])
            axes[r][c].set_title('Answer:{} {}\nPredict:{} {}'
                                 .format(label_index, label_list[label_index],
                                         pred, label_list[pred]))
        axes[r][c].axis('off')  # do not show axis value
    plt.tight_layout(pad=0.01)   # automatic padding between subplots
    plt.savefig(filepath)
    print('Result saved to {}'.format(filepath))


if __name__ == '__main__':
    main()

