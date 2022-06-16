import preprocess
import label
import maketestdata
import randomforest_test

if __name__ == '__main__':
    preprocess.preprocess('ReaquestTestSet10')
    label.labeling('test_data')
    maketestdata.make_test_data('test_data', 'ReaquestTestSet10', 'testdata')
    randomforest_test.predict('testdata/test_data.csv')
