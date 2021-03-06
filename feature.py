#### Functions

#from PIL import Image
import numpy as np
#import sys
#from itertools import islice
#import random
from sklearn.decomposition import PCA

from scipy.ndimage.filters import gaussian_laplace
from skimage.feature import structure_tensor_eigvals
from skimage.feature import structure_tensor
from skimage.feature import hessian_matrix
from skimage.feature import hessian_matrix_eigvals
from scipy.ndimage.filters import gaussian_gradient_magnitude
import time
# Caluculated pixel-related features with sliding window
# ---sum of pixel values
# ---range of pixel values
# ---variance of pixel values
# ---median of pixel values
def pixelFeature(input_image, w):
    # windows should be an array of window sizes: 3, 5, 9, 15, 19, 25
    if not input_image.size:
        print("Input Image is empty!")
        return
    features = np.zeros((input_image.shape[0], input_image.shape[1], 4 * input_image.shape[2]))
    
    # starting from the top
    (winW, winH) = (w, w)
    layer = input_image.shape[2]
    for (x, y, window) in sliding_window(input_image, (w, w)):
        # if the window size does not meet our desired window size, ignore
        if window.shape[0] != winH or window.shape[1] != winW:
            continue
        # perform feature extraction
        # Sum of a window of w * w pixels
        features[y, x, 0:layer] = sum(sum(window))
        # Dynamic range of a window of w * w pixels
        for i in xrange(0, layer):
            features[y, x, i + layer] = abs(np.amax(window[:, :, i]) - np.amin(window[:, :, i]))
            # Variance of a window of w * w pixels
        for i in xrange(0, layer):
            features[y, x, i + 2 * layer] = np.var(window[:, :, i])
        for i in xrange(0, layer):
            # Median of a window of w * w pixels
            features[y, x, i + 3 * layer] = np.median(window[:, :, i])
    return features


def sliding_window(image, windowSize):
    # slide a window across the image
    s = image.shape
    row = s[0]
    col = s[1]
    
    wX = windowSize[0]
    wY = windowSize[1]
    
    temp = image[0:wY/2, :]
    temp = np.flip(temp,axis=0)
    paddedImage = np.append(temp, image, axis=0)
    temp = image[row-wY/2:row, :]
    temp = np.flip(temp,axis=0)
    paddedImage = np.append(paddedImage, temp, axis=0)
    temp = paddedImage[:,0:wX/2]
    temp = np.flip(temp,axis=1)
    paddedImage = np.append(temp, paddedImage, axis=1)
    temp = paddedImage[:, col-wX/2:col]
    temp = np.flip(temp,axis=1)
    paddedImage = np.append(paddedImage, temp, axis=1)
    
    if not image.size:
        print("Input Image is empty!")
        return
    for y in xrange(0, image.shape[0], 1):
        for x in xrange(0, image.shape[1], 1):
            window = paddedImage[y:y + windowSize[1], x:x + windowSize[0]]
            yield (x, y, paddedImage[y:y + windowSize[1], x:x + windowSize[0]])
                
                


def adjacentHLFeatures(input_image, window1, window2):
    # 5 <= W1 <= 25
    # 1 <= W2 <= 8
    if not input_image.size:
        print("Input Image is empty!")
        return
    features = np.zeros((input_image.shape[0], input_image.shape[1], input_image.shape[2]))
    w1 = window1
    w2 = window2
    w12 = w1 + 2 * window2
    for (x2, y2, window2) in sliding_window(input_image, (w12, w12)):
#        if x2 == 1197 and y2 == 257:
#            print("hello")
        if window2.shape[0] == w12 and window2.shape[1] == w12:
            window1 = window2[w2:w2+w1, w2:w2+w1]
            features[y2, x2, 0:input_image.shape[2]] = sum(sum(window2)) - sum(sum(window1))
        else:
            print(x2,y2)
    return features


# Caluculated nonadjacent Haar-Like Features
def nonadjacentHLFeatures1(input_image, window1, window2, window3, norm = 1):
    # 5 <= W1 <= 25
    # 1 <= W2,W3,W4 <= 8
    # norm is normalization factor, default = 1
    
    if not input_image.size:
        print("Input Image is empty!")
        return
 
    features = np.zeros(input_image.shape)

    w1 = window1
    w2 = window2
    w3 = window3
    w12 = w1 + 2 * w2
    w123 = w1 + 2 * (w2 + w3)
    for (x123, y123, window123) in sliding_window(input_image, (w123, w123)):
        if window123.shape[0] == w123 and window123.shape[1] == w123:
            window12 = window123[w3:w3+w12, w3:w3+w12]
            window1 = window123[w3+w2:w3+w2+w1, w3+w2:w3+w2+w1]
            # HLNA(w1, w2, w3)
            features[y123, x123, 0:input_image.shape[2]] = sum(sum(window123))
            - sum(sum(window12)) - norm * sum(sum(window1))
        else:
            print("non2: ", (x123, y123))
    return features


# Caluculated nonadjacent Haar-Like Features 2
def nonadjacentHLFeatures2(input_image, window1, window2, window3, window4, norm = 1):
    # 5 <= W1 <= 25
    # 1 <= W2,W3,W4 <= 8
    # norm is normalization factor, default = 1
    
    if not input_image.size:
        print("Input Image is empty!")
        return

    features = np.zeros(input_image.shape)
    w1 = window1
    w2 = window2
    w3 = window3
    w4 = window4
    w12 = w1 + 2 * w2
    w123 = w1 + 2 * (w2 + w3)
    w1234 = w123 + 2 * w4
    for (x1234, y1234, window1234) in sliding_window(input_image, (w1234, w1234)):
        window123 = window1234[w4:w4+w123, w4:w4+w123]
        window12 = window1234[w3+w4:w3+w4+w12, w3+w4:w3+w4+w12]
        window1 = window1234[w2+w3+w4:w2+w3+w4+w1, w2+w3+w4:w2+w3+w4+w1]
        # HLNA2(w1, w2, w3, w4)

        features[y1234, x1234, 0:input_image.shape[2]] = sum(sum(window1234))
        - sum(sum(window123)) - norm * sum(sum(window12))
        - sum(sum(window1))
    return features

# Calculate line features using SIFT
def lineFeatures(input_image):
    
    return 0

# =============================================================================
# Calculate Features, concatenate them, return.
# - windowSizeArray could have length 1, 3, 4 or 5
#      - length 1: pixel feature
#      - length 3: pixel feature and adjacent Haar-like features
#      - length 4: adjacent Haar-like features, nonadjacent Haar like feature 2 and nonadjacent Haar like feature 1
#      - length 5: pixel feature, adjacent Haar-like features, nonadjacent Haar like feature 1
#                  and nonadjacent Haar like feature 2
#           
#      - [1:4]: Haar-like feature w1, w2, w3, w4
#           5 <= W1 <= 25
#           1 <= W2,W3,W4 <= 8
# - norm (optional) - normalization factor for nonadjacent Haar-like features (default is 1)
# Return: numpy.array of concatenated features; empty numpy array if wrong size is passed in
# =============================================================================
def computeFeature(input, windowSizeArray, norm = 1):
    if (len(windowSizeArray) == 1):
        return pixelFeature(input, windowSizeArray[0])
    elif (len(windowSizeArray) == 3): 
        pixelF = pixelFeature(input, windowSizeArray[0])
        adjacentHF = adjacentHLFeatures(input, windowSizeArray[1], windowSizeArray[2])
        return np.concatenate((pixelF, adjacentHF), axis = 2)
    elif (len(windowSizeArray) == 4):
        adjacentHLF = adjacentHLFeatures(input, windowSizeArray[0], windowSizeArray[1])
        nonadjacentHLF = nonadjacentHLFeatures1(input, windowSizeArray[0], 
                                            windowSizeArray[1], windowSizeArray[2], norm)
        nonadjacentHLF2 = nonadjacentHLFeatures2(input, windowSizeArray[0], windowSizeArray[1], 
                                             windowSizeArray[2], windowSizeArray[3], norm)
        return np.concatenate((pixelF,adjacentHLF, nonadjacentHLF, nonadjacentHLF2), axis = 2)
    elif (len(windowSizeArray) == 5):
        pixelF = pixelFeature(input, windowSizeArray[0])
        adjacentHLF = adjacentHLFeatures(input, windowSizeArray[1], windowSizeArray[2])
        nonadjacentHLF = nonadjacentHLFeatures1(input, windowSizeArray[1], 
                                            windowSizeArray[2], windowSizeArray[3], norm)
        nonadjacentHLF2 = nonadjacentHLFeatures2(input, windowSizeArray[1], windowSizeArray[2], 
                                             windowSizeArray[3], windowSizeArray[4], norm)
        return np.concatenate((pixelF,adjacentHLF, nonadjacentHLF, nonadjacentHLF2), axis = 2)
    else: 
        # Invalid Size, return empty array
        print("Not enough or too much window size provided. Returning empty np array")
        return np.array([]) 


# =============================================================================
# Reduce the number of features using PCA
# =============================================================================
def reduceFeatures(feature_train, Y_train, feature_validate, Y_validate, 
                   feature_test, Y_test):
    (pca, numComponents) = doPCA(feature_train, 0.99)
    pca_train = pca.transform(feature_train)
    pca_validate = pca.transform(feature_validate)
    pca_test = pca.transform(feature_test)
    return pca_train, Y_train, pca_validate, Y_validate, pca_test, Y_test

def reduceFeatureSimple(features):
    (pca, numComponents) = doPCA(features, 0.99)
    pca_train = pca.transform(features)
    return pca_train

# =============================================================================
# Perform PCA dimensionality reduction:
#   Increase number of components until reaching the threshold of explained
#   variance ratio
# =============================================================================
def doPCA(data, threshold):
    fTotal = data.shape[1]
    for i in xrange(1,fTotal):
        pca = PCA(n_components = i)
        pca.fit(data)
        if (sum(pca.explained_variance_ratio_) > threshold):
            return (pca, i)
    return (pca, fTotal)    

# =============================================================================
# Calculate pixel features using all possible window sizes
# Contatenate all the features together
# Save as csv
# =============================================================================
def computeAllPixelFeatures(Xdata, isTraining, path):
    path = path + '/pixelFeature'
    print("Computing: PixelFeatures")
    print("is Training? %r" %isTraining)
    start = time.time()
    
    pixelw = [2, 8, 14, 24]
    pixelF = np.zeros((Xdata.shape[0], Xdata.shape[1], 
                       Xdata.shape[2] * 4 * len(pixelw)))
    for i in xrange(len(pixelw)):
        f = pixelFeature(Xdata, pixelw[i])
        index = i * Xdata.shape[2] * 4
        pixelF[:,:,index: index + Xdata.shape[2] * 4] = f
    resized_pixelF = np.resize(pixelF, 
                             (pixelF.shape[0]*pixelF.shape[1], pixelF.shape[2]))
    end = time.time()
    if (isTraining):
        print("\nComputed: pixelFeature_Tr in %f seconds\n" %(end-start))
        path = path + '_Tr'
        np.savez_compressed(path, data = resized_pixelF)

        #np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/pixelFeature_Tr.csv", 
                   #resized_pixelF, delimiter=",")
    else: 
        print("\nComputed: pixelFeature_Ts in %f seconds\n" %(end-start))
        path = path + '_Ts'
        np.savez_compressed(path, data = resized_pixelF)
        
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/pixelFeature_Ts.csv", 
#                   resized_pixelF, delimiter=",")

# =============================================================================
# Calculate Haar like features using all possible window sizes
# Contatenate all the features together
   # 21*8 + 11*8*8 + 11*4*4*4 = 1576 features 
# Save as csv
# =============================================================================
def computeAllHaarlikeFeatures(Xdata, isTraining, path):
    path = path + '/HLFeatures'
    print("Computing: All Haar-like Features")
    print("is Training? %r" %isTraining)
    # 21*8 + 11*8*8 + 11*4*4*4 = 1576 features
    # Compute all adjacent Haar-like box feature
    
    print("Computing: adjacentHLFeature")
    start = time.time()
    
    w1 = range(4,26,4)
    w2 = range(1,9,3)
    adjacentHLF = np.zeros((Xdata.shape[0], Xdata.shape[1], 
                             Xdata.shape[2] * len(w1) * len(w2)))
    
    for i in xrange(len(w1)):
        for j in xrange(len(w2)):
            f = adjacentHLFeatures(Xdata, w1[i], w2[j])
            index = i * len(w2) * Xdata.shape[2] + j * Xdata.shape[2]
            adjacentHLF[:,:,index:index + Xdata.shape[2]] = f
    
    resized_adjacentHLF = np.resize(adjacentHLF, 
                             (adjacentHLF.shape[0]*adjacentHLF.shape[1], adjacentHLF.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed: adjacentHLFeature_Tr in %f seconds" %(end-start))
#        with open('adjacentHLFeature_Tr.pkl','wb') as outfile:
#            pickle.dump(resized_adjacentHLF, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/adjacentHLFeature_Tr.csv", 
#                   resized_adjacentHLF, delimiter=",")
    else:
        print("Computed: adjacentHLFeature_Ts in %f seconds" %(end-start))
#        with open('adjacentHLFeature_Ts.pkl','wb') as outfile:
#            pickle.dump(resized_adjacentHLF, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/adjacentHLFeature_Ts.csv", 
#                   resized_adjacentHLF, delimiter=",")

    # Compute all nonadjacent Haar-like feature 1
    w1 = range(4,26,4)
    w2 = range(1, 9, 3)
    w3 = range(1, 9, 2)
    print("Computing: Nonadjacent Haar-like feature 1")
    start = time.time()
    
    nonadjacentHLF1 = np.zeros((Xdata.shape[0], Xdata.shape[1], 
                                Xdata.shape[2] * len(w1) * len(w2) * len(w3)))
    for i in xrange(len(w1)):
        for j in xrange(len(w2)):
            for k in xrange(len(w3)):
                f = nonadjacentHLFeatures1(Xdata, w1[i], w2[j], w3[k])
                index = (i*len(w2)*len(w3)*Xdata.shape[2] + 
                         j*len(w3)*Xdata.shape[2] + k*Xdata.shape[2])
                nonadjacentHLF1[:,:,index:index + Xdata.shape[2]] = f
    
    resized_nonadjacentHLF1 = np.resize(nonadjacentHLF1, 
                             (nonadjacentHLF1.shape[0]*nonadjacentHLF1.shape[1], nonadjacentHLF1.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed:nonadjacentHLFeature1_Tr in %f seconds" %(end-start))
#        with open('nonadjacentHLFeature1_Tr.pkl','wb') as outfile:
#            pickle.dump(resized_nonadjacentHLF1, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/anondjacentHLFeature1_Tr.csv", 
#                   resized_nonadjacentHLF1, delimiter=",")
    else:
        print("Computed:nonadjacentHLFeature1_Ts in %f seconds" %(end-start))
#        with open('nonadjacentHLFeature1_Ts.pkl','wb') as outfile:
#            pickle.dump(resized_nonadjacentHLF1, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/anondjacentHLFeature1_Ts.csv", 
#                   resized_nonadjacentHLF1, delimiter=",")
    
#     Compute all nonadjacent Haar-like feature 2
    w1 = range(4,26,4)
    w2 = range(1, 9, 3)
    w3 = range(1, 9, 3)
    w4 = range(1, 9, 3)
    print("Computing: Nonadjacent Haar-like feature 2")
    start = time.time()
    nonadjacentHLF2 = np.zeros((Xdata.shape[0], Xdata.shape[1], 
                                Xdata.shape[2] * len(w1) * len(w2) * len(w3) * len(w4)))
    
    for i in xrange(len(w1)):
        for j in xrange(len(w2)):
            for k in xrange(len(w3)):
                for l in xrange(len(w4)):
                    f = nonadjacentHLFeatures2(Xdata, w1[i], w2[j], w3[k], w4[l])
                    index = (i*len(w2)*len(w3)*len(w4)*Xdata.shape[2] + 
                             j*len(w3)*len(w4)*Xdata.shape[2] + 
                             k*len(w4)*Xdata.shape[2] + l*Xdata.shape[2])
                    nonadjacentHLF2[:,:,index:index + Xdata.shape[2]] = f
    
    resized_nonadjacentHLF2 = np.resize(nonadjacentHLF2, 
                             (nonadjacentHLF2.shape[0]*nonadjacentHLF2.shape[1], nonadjacentHLF2.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed:nonadjacentHLFeature2_Tr in %f seconds" %(end-start))
        
#        with open('nonadjacentHLFeature2_Tr.pkl','wb') as outfile:
#            pickle.dump(resized_nonadjacentHLF2, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/nonadjacentHLFeature2_Tr.csv", 
#                   resized_nonadjacentHLF2, delimiter=",")
    else:
        print("Computed:nonadjacentHLFeature2_Ts in %f seconds" %(end-start))
        
#        with open('nonadjacentHLFeature2_Ts.pkl','wb') as outfile:
#            pickle.dump(resized_nonadjacentHLF2, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/nonadjacentHLFeature2_Ts.csv", 
#                   resized_nonadjacentHLF2, delimiter=",")
    
    resized_all = np.concatenate((resized_adjacentHLF, resized_nonadjacentHLF1, resized_nonadjacentHLF2), axis = 1)
    
    if (isTraining):
        print("\nFINISHED: Haar Like Features for Training data\n")
        path = path + '_Tr'
        np.savez_compressed(path, data = resized_all)
        
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/HLFeatures_Tr.csv", 
#                   resized_all, delimiter=",")
    else:
        print("\nFINISHED: Haar Like Features for Testing data\n")
        path = path + '_Ts'
        np.savez_compressed(path, data = resized_all)
        
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/HLFeatures_Ts.csv", 
#                   resized_all, delimiter=",")
    

def computeStructureFeatures(Xdata, isTraining, path):
    path = path + '/structFeatures'
    print("\nComputing: All Structure Features")
    print("is Training? %r" %isTraining)
    start = time.time()
    # Separate color channel
    RChannel = Xdata[:,:,0]
    GChannel = Xdata[:,:,1]
    BChannel = Xdata[:,:,2]
    # Calculate Laplacian of Gaussian (sigma = 1.6)
    print("Computing: Laplacian of Gaussian")
    gaussianLF_R = gaussian_laplace(RChannel, 1.6)
    gaussianLF_G = gaussian_laplace(GChannel, 1.6)
    gaussianLF_B = gaussian_laplace(BChannel, 1.6)
    gaussianLF = np.dstack((gaussianLF_R, gaussianLF_G, gaussianLF_B))
    gaussianLF = np.resize(gaussianLF, 
                             (gaussianLF.shape[0]*gaussianLF.shape[1], gaussianLF.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed: gaussianLapFeatures_Tr in %f seconds" %(end-start))
        
#        with open('gaussianLapFeatures_Tr.pkl','wb') as outfile:
#            pickle.dump(gaussianLF, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/gaussianLapFeatures_Tr.csv", 
#                   gaussianLF, delimiter=",")
    else:
        print("Computed: gaussianLapFeatures_Ts in %f seconds" %(end-start))
#        with open('gaussianLapFeatures_Ts.pkl','wb') as outfile:
#            pickle.dump(gaussianLF, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/gaussianLapFeatures_Ts.csv", 
#                   gaussianLF, delimiter=",")
        
    # Calculate eigenvalues of structure tensor  (sigma =1.6, 3.5)
    print("Computing: eigenvalues of structure tensor")
    start = time.time()
    
    Axx_R1, Axy_R1, Ayy_R1 = structure_tensor(RChannel, sigma = 1.6)
    larger_R1, smaller_R1 = structure_tensor_eigvals(Axx_R1, Axy_R1, Ayy_R1)
    Axx_R2, Axy_R2, Ayy_R2 = structure_tensor(RChannel, sigma = 3.5)
    larger_R2, smaller_R2 = structure_tensor_eigvals(Axx_R2, Axy_R2, Ayy_R2)
    Axx_G1, Axy_G1, Ayy_G1 = structure_tensor(GChannel, sigma = 1.6)
    larger_G1, smaller_G1 = structure_tensor_eigvals(Axx_G1, Axy_G1, Ayy_G1)
    Axx_G2, Axy_G2, Ayy_G2 = structure_tensor(GChannel, sigma = 3.5)
    larger_G2, smaller_G2 = structure_tensor_eigvals(Axx_G2, Axy_G2, Ayy_G2)
    Axx_B1, Axy_B1, Ayy_B1 = structure_tensor(BChannel, sigma = 1.6)
    larger_B1, smaller_B1 = structure_tensor_eigvals(Axx_B1, Axy_B1, Ayy_B1)
    Axx_B2, Axy_B2, Ayy_B2 = structure_tensor(BChannel, sigma = 3.5)
    larger_B2, smaller_B2 = structure_tensor_eigvals(Axx_B2, Axy_B2, Ayy_B2)
    eigenST = np.dstack((larger_R1, smaller_R1, larger_R2, smaller_R2, 
                              larger_G1, smaller_G1, larger_G2, smaller_G2, 
                              larger_B1, smaller_B1, larger_B2, smaller_B2))
    eigenST = np.resize(eigenST, 
                             (eigenST.shape[0]*eigenST.shape[1], eigenST.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed: eigenStructFeatures_Tr in %f seconds" %(end-start))
        
#        with open('eigenStructFeatures_Tr.pkl','wb') as outfile:
#            pickle.dump(eigenST, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/eigenStructFeatures_Tr.csv", 
#                   eigenST, delimiter=",")
    else:
        print ("Computed: eigenStructFeatures_Ts in %f seconds" %(end-start))        
#        with open('eigenStructFeatures_Ts.pkl','wb') as outfile:
#            pickle.dump(eigenST, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/eigenStructFeatures_Ts.csv", 
#                   eigenST, delimiter=",")
        
    # Calculate eigenvalues of Hessian matrix
    print("Computing: eigenvalues of Hessian matrix")
    start = time.time()
    Hrr_R1, Hrc_R1, Hcc_R1 = hessian_matrix(RChannel, sigma = 1.6, order='rc')
    larger_R1, smaller_R1 = hessian_matrix_eigvals(Hrr_R1, Hrc_R1, Hcc_R1)
    Hrr_R2, Hrc_R2, Hcc_R2 = hessian_matrix(RChannel, sigma = 3.5, order='rc')
    larger_R2, smaller_R2 = hessian_matrix_eigvals(Hrr_R2, Hrc_R2, Hcc_R2)
    Hrr_G1, Hrc_G1, Hcc_G1 = hessian_matrix(GChannel, sigma = 1.6, order='rc')
    larger_G1, smaller_G1 = hessian_matrix_eigvals(Hrr_G1, Hrc_G1, Hcc_G1)
    Hrr_G2, Hrc_G2, Hcc_G2 = hessian_matrix(GChannel, sigma = 3.5, order='rc')
    larger_G2, smaller_G2 = hessian_matrix_eigvals(Hrr_G2, Hrc_G2, Hcc_G2)
    Hrr_B1, Hrc_B1, Hcc_B1 = hessian_matrix(BChannel, sigma = 1.6, order='rc')
    larger_B1, smaller_B1 = hessian_matrix_eigvals(Hrr_B1, Hrc_B1, Hcc_B1)
    Hrr_B2, Hrc_B2, Hcc_B2 = hessian_matrix(BChannel, sigma = 3.5, order='rc')
    larger_B2, smaller_B2 = hessian_matrix_eigvals(Hrr_B2, Hrc_B2, Hcc_B2)
    eigenHess = np.dstack((larger_R1, smaller_R1, larger_R2, smaller_R2,
                                larger_G1, smaller_G1, larger_G2, smaller_G2,
                                larger_B1, smaller_B1, larger_B2, smaller_B2))
    eigenHess = np.resize(eigenHess, 
                             (eigenHess.shape[0]*eigenHess.shape[1], eigenHess.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed: eigenHessFeatures_Tr in %f seconds" % (end-start))
#        with open('eigenHessFeatures_Tr.pkl','wb') as outfile:
#            pickle.dump(eigenHess, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/eigenHessFeatures_Tr.csv", 
#                   eigenHess, delimiter=",")
    else:
        print("Computed: eigenHessFeatures_Ts in %f seconds" % (end-start))
#        with open('eigenHessFeatures_Ts.pkl','wb') as outfile:
#            pickle.dump(eigenHess, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/eigenHessFeatures_Ts.csv", 
#                   eigenHess, delimiter=",")
    
    # Calculate Gaussian gradient magnitude (sigma = 1.6)
    print("Computing: Gaussian gradient magnitude")
    start = time.time()
    gaussian_grad_R = gaussian_gradient_magnitude(RChannel, sigma = 1.6)
    gaussian_grad_G = gaussian_gradient_magnitude(GChannel, sigma = 1.6)
    gaussian_grad_B = gaussian_gradient_magnitude(BChannel, sigma = 1.6)
    gaussian_grad = np.dstack((gaussian_grad_R, gaussian_grad_G, 
                                    gaussian_grad_B))
    gaussian_grad = np.resize(gaussian_grad, 
                             (gaussian_grad.shape[0]*gaussian_grad.shape[1], 
                              gaussian_grad.shape[2]))
    end = time.time()
    if (isTraining):
        print("Computed: gaussianGradFeatures_Tr in %f seconds" % (end-start))
        
#        with open('gaussianGradFeatures_Tr.pkl','wb') as outfile:
#            pickle.dump(gaussian_grad, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/gaussianGradFeatures_Tr.csv", 
#                   gaussian_grad, delimiter=",")
    else:
        print("Computed: gaussianGradFeatures_Ts in %f seconds" % (end-start))
        
#        with open('gaussianGradFeatures_Ts.pkl','wb') as outfile:
#            pickle.dump(gaussian_grad, outfile, pickle.HIGHEST_PROTOCOL)
#        np.savetxt("/Users/wuwenjun/GitHub/CSE-577-Melanoma-Nuclei-Segmentation/gaussianGradFeatures_Ts.csv", 
#                   gaussian_grad, delimiter=",")
    
    All = np.concatenate((gaussianLF, eigenST, eigenHess, gaussian_grad),axis = 1)
    if (isTraining):
        path = path + '_Tr'
        np.savez_compressed(path, data = All)
        print("\nFINISHED: Structure Features for Training data\n")

    else:   
        path = path + '_Ts'
        np.savez_compressed(path, data = All)
        print("\nFINISHED: Structure Features for Testing data\n")
