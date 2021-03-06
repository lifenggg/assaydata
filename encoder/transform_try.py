import os
import numpy as np
import dA
import cPickle
import gzip
import sys

from scipy.sparse import csr_matrix

'''
def get_sampled(a, b, sample_rate = 0.01):

    # random seed
    np.random.seed(42)

    # non-zero features
    m = np.array(np.sum(a, axis=0))
    

    # sample from all the features
    d = np.random.binomial(size = m.shape[0], n = 1, p = sample_rate )


    e = np.logical_or(d>0, m>0)

    # which feature
    sampled_index = []


    for i in range(a.shape[1]):
        if e[i] != 0:
            sampled_index.append(i)

    a_sampled = a[:,sampled_index]
    b_sampled = b[:,sampled_index]
    return [a_sampled, b_sampled]

'''


# from the svm_rank input file get the feature matrix
def file2matrix(file_path):
    with open(file_path) as f:
    # this is to store spase  CSR array
        row = []
        col = []
        data = []
        i = 0
        ret_left = []
        ret_right = []

        for line in f:
            entry = line[:-2].split(' ')
            entry_len = len(entry)

            # store the left part
            ret_left.append(entry[0] + ' ' +  entry[1])
            ret_right.append(entry[-1])

            # store the feature matrix
            for j in range(2, entry_len-1): # the last col is the cid name
                pair = entry[j].split(':')
                row.append(i)
                col.append(int(pair[0])-1)
                data.append(int(pair[1]))
            i += 1

    f.close()

    ret_matrix = csr_matrix( (data, (row, col))).toarray()


    return (ret_matrix, ret_left, ret_right)




    # get the numpy array

    # use picke to dump the numpy array

    # return the path of the pickle

def matrix2file(matrix_x, matrix_left, matrix_right ,file_path):
    #s_matrix_x = csr_matrix(matrix_x)
    #print s_matrix_x

    row_prev = -1

    all_rows = []

    num_row = 0
    num_col = 0
    for row in matrix_x:
        buffer = ''
        num_col = 0
        for col in row:

            '''
            if col > 0.5:
                buffer += str(num_col+1) + ':1 '
            '''
            buffer += str(num_col+1) + ':' + '{:<6.3f}'.format(col)

            num_col += 1

        all_rows.append(buffer)
        num_row += 1

    #print all_rows

    f = open(file_path, 'w')
    num_row = 0
    for row in all_rows:
        buffer = matrix_left[num_row] + ' ' + all_rows[num_row] + matrix_right[num_row]
        print >> f, buffer
        num_row += 1
    f.close()








# use the degnosing autocoder to transform the train and test data
def do_transform(train_path, test_path, new_train_path, new_test_path, pickle_path, model_path, pecent_encode,my_training_epochs, mysample_mathod, encode_function):
    # left is the left part besides the feature matrix
    matrix_train, train_left, train_right= file2matrix(train_path)
    matrix_test, test_left, test_right = file2matrix(test_path)





    dim_in = max(matrix_train.shape[1], matrix_test.shape[1])
    extra_col = 0

    # the dimension of two sparse matrix may be different
    if dim_in > matrix_train.shape[1]:
        extra_col = dim_in - matrix_train.shape[1]
        matrix_train = np.hstack((matrix_train, np.zeros((matrix_train.shape[0], extra_col), dtype=int)))

    if dim_in > matrix_test.shape[1]:
        extra_col = dim_in - matrix_test.shape[1]
        matrix_test = np.hstack((matrix_test, np.zeros((matrix_test.shape[0], extra_col), dtype= int)))
        
    #[matrix_train_sampled, matrix_test_sampled] = get_sampled(matrix_train, matrix_test, 0.01)


    # save the trainset and test set (which will be used by dA module)
    f = gzip.open(pickle_path, 'w')
    cPickle.dump([matrix_train, matrix_test], f)
    f.close()


    dim_out = int(dim_in*pecent_encode)
    print 'before sampling', matrix_train.shape, matrix_test.shape, 'mapped to dim_out = ', dim_out

    matrix_train_new, matrix_test_new = dA.test_dA(0, dim_in, dim_out, learning_rate=0.1, training_epochs=my_training_epochs,dataset=pickle_path, batch_size=10, output_path=model_path, sample_method=mysample_mathod, encode_function=encode_function)

    matrix2file(matrix_train_new, train_left, train_right, new_train_path)
    matrix2file(matrix_test_new, test_left, test_right, new_test_path)
    print 'encoded file written'



'''
if __name__ == '__main__':
    assay_directory = '../alldata'
    pecent_encode = 0.01
    for file_name in os.listdir(assay_directory):
        for current_fold in range(5):
            mycase = file_name +'_' + str(current_fold)
            train_path = '../traindata/' + mycase +'.train'
            test_path = '../testdata/' + mycase +'.test'

            new_train_path = '../traindata_new/' + mycase +'.train'
            new_test_path = '../testdata_new/' + mycase +'.test'

            pickle_path = '../data/' + mycase +'.pkl.gz'  # this is for dA module

            model_path = '../W_b/' +mycase +'.pkl.gz' # this is the encode 's W and b
            print train_path, test_path, new_train_path, new_test_path

            do_transform(train_path, test_path, new_train_path, new_test_path, pickle_path, model_path, pecent_encode)
'''


## this part is for parameter tuning


if __name__ == '__main__':
    #assay_directory = '../alldata'

    assay_name = '733.csv.out.2'
    current_fold = '0'
    #percent_encode = 0.01
    percent_encode = 0.01
    training_epochs = 100
    sample_method = 0 # 0 for sample using nz and same size of zero. 1 for only nz features, 2 not sampling
    encode_function = 0 # 0 for use sigmoid


    # try one instance
    for arg in sys.argv[1:]:


        if arg.startswith('-a='):
            assay_name = arg[len('-a='):]

        if arg.startswith('-f='):
            current_qfold = arg[len('-f='):]


        if arg.startswith('-p='):
            percent_encode = float(arg[len('-p='):])

        if arg.startswith('-t='):
            training_epochs = int(arg[len('-t='):])

        if arg.startswith('-s='):
            sample_method = int(arg[len('-s='):])

        if arg.startswith('-e='):
            encode_function = int(arg[len('-e='):])





    mycase = assay_name +'_' + str(current_fold)
    train_path = '../traindata/' + mycase +'.train'
    test_path = '../testdata/' + mycase +'.test'

    if sample_method == 0:
        mycase_more = mycase + '_pct_' + str(percent_encode) + '_epochs_' + str(training_epochs)
        print 'sample from all non-zeros and same size of zeros'
    elif sample_method == 1:
        mycase_more = mycase + '_pct_' + str(percent_encode) + '_epochs_' + str(training_epochs) + '_only_nz'
        print 'sample only non-zero values'
    elif sample_method == -1:
        mycase_more = mycase + '_pct_' + str(percent_encode) + '_epochs_' + str(training_epochs) + '_without_sampling'
        print 'do not sampling'


    if encode_function == 0:
        mycase_more += '_sigmoid'
        print 'use sigmoid function'
    elif encode_function == 1:
        mycase_more += '_tanh'
        print 'using tanh function'

    new_train_path = 'traindata_sampled_encoded_new/' + mycase_more +'.train'
    new_test_path = 'testdata_sampled_encoded_new/' + mycase_more + '.test'




    pickle_path = '/scratch/lifen/tmp/' + mycase_more +'_sampled_new.pkl.gz'  # this is for dA module

    model_path = '/scratch/lifen/dA_model/' +mycase_more # this is the encode 's W and b
    print train_path, test_path, new_train_path, new_test_path




    do_transform(train_path, test_path, new_train_path, new_test_path, pickle_path, model_path, percent_encode, training_epochs, sample_method, encode_function)


'''
def test():
    matrix_train, train_left , train_right= file2matrix('../traindata/test.train')
    print matrix_train
    print train_left
    print train_right

    matrix2file(matrix_train, train_left, train_right , '../traindata_new/test.train')
'''
