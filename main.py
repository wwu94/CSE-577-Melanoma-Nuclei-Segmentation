#### Main

#load the data (features) and perform PCA - Meredith
def loadFeature(input, windowSizeArray):
    # not implemented
    return

#load the data and split, call loadFeature(...) - Shima
def loadData(image_address, mask_address):
    # not implemented
    return

# Split into training and test set
[X_train, Y_train , X_test , Y_test] = dataset_split(X,Y,0.8)              

# Fit a simple decision tree first
base_tree = DecisionTreeClassifier(max_depth = 1, random_state = 1)


#errors and predictions before adaboost
base_tree.fit(X_train,Y_train)
pred_train = base_tree.predict(X_train)
pred_test = base_tree.predict(X_test)
    
error_train= sum(pred_train != Y_train) / float(Y_train.shape[0])
error_test = sum(pred_test != Y_test) / float(Y_test.shape[0])

training_pred = []
testing_pred = []
train_err_M = []
test_err_M = []

training_pred.append(pred_train)
testing_pred.append(pred_test)
train_err_M.append(error_train)
test_err_M.append(error_test)
    

M = 100     #Number of iterations for adaboost     
for i in range(1, M, 10):    
    [pred_train , pred_test , error_train , 
     error_test ] = Adaboost(X_train , Y_train , X_test, Y_test, i, base_tree)

    training_pred.append(pred_train)
    testing_pred.append(pred_test)
    train_err_M.append(error_train)
    test_err_M.append(error_test)
    

iRange=np.arange(1, M+10, 10)
trainERR,= plt.plot(iRange,train_err_M,'g')
testERR,= plt.plot(iRange,test_err_M,'r')

plt.xlabel('iterations')
plt.ylabel('Errors')
plt.legend([trainERR,testERR], ["Training error","testing error"])
plt.show()     
