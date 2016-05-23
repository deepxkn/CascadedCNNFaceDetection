from keras.models import Sequential
import model_architecture
import time
import imageloader as il
import math
import sys
import imagepyramid
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
import preprocess_48net as net
import visualize_results as vr

model12FileName = str(sys.argv[1])
model48FileName = str(sys.argv[2])
windowSize = 24
windowSize48 = 48
scaleFactor = 2
stepSize = 24
T12 = 0.3 #threshold for it is passed to 48net
T48 = 0.3 #threshold for if it is a high label for the final evaluation

#================================================
# Preprocessing
#================================================

print("======Loading and Preprocessing...======")
start_time = time.time()

#If path to image passed as argument load and process that image, otherwise load from annotations(evaluation images)
if (len(sys.argv) > 3):
        imdb =[il.loadAndPreProcessSingle(str(sys.argv[3]), scaleFactor, (windowSize, windowSize))]
else:
    imdb = il.loadAndPreProcessIms('annotations_short.txt', scaleFactor, (windowSize,windowSize))

print("Image database: {0} images".format(len(imdb)))
[X, Y, W] = il.getCNNFormat(imdb, stepSize, windowSize)
print("finished preprocessing in {0}".format(time.time()-start_time))
print('X-shape')
print(X.shape)
print('Y-shape: ')
print(Y.shape)
print('W-shape')
print(W.shape)

print("=========================================")
#================================================
# 12 net
#================================================

print("\n\n============== 12Net ====================")
model12 = model_architecture.setUp12net(windowSize)
print("Loading model from: " + model12FileName)
model12.load_weights(model12FileName)

model48 = model_architecture.setUp48net(windowSize48)
print("Loading model from: " + model48FileName)
model12.load_weights(model12FileName)

# Get best predictions
predictions_12 = model12.predict(X, batch_size=16, verbose=1)
# Get top 10%
targets  = np.squeeze(predictions_12)
nb_top_targets = int(math.ceil(targets.shape[0]*0.1))
p_idx = np.argsort(targets)[-nb_top_targets:]
predictions_12 = predictions_12[p_idx,:]
Y = Y[p_idx,:]
X = X[p_idx,:, :, :]
W = W[p_idx, :, :]
print('X-shape')
print(X.shape)
print('Y-shape: ')
print(Y.shape)
print('W-shape')
print(W.shape)
print("=========================================")

#================================================
# 48 net
#================================================

print("\n\n============== 48Net ====================")
prevWindowSize = windowSize
[X_48, Y_48, W_48, windowSize, imdb_48] = net.preProcess48Net(imdb, X, predictions_12,W, prevWindowSize)
print("preprocessing in {0}".format(time.time()-start_time))
predictions_48 = model48.predict_on_batch(X_48)
print("prediction in {0} s".format(time.time()-start_time))
print("Number of predictions: {0}".format(predictions_48.shape))
## To map input to 48 with original image
i = np.argmax(np.squeeze(predictions_48))
y = Y_48[i,:]
w = W_48[i,0,:]
images = []
for i in range(0,len(W_48)):
    idx = W_48[i,0,3]
    images.append(imdb[idx].image)

images = np.squeeze(images)
X_48 = np.squeeze(X_48)
W_48 = np.squeeze(W_48)

title = "Top predicted face image from 48Net"
vr.visualizeResultNoSubImage(title,images, W_48)
