from nltk import NaiveBayesClassifier, classify
import TurkishProcessor as tp
import EnglishProcessor as en
import Util as util 
import sys
from langid.langid import LanguageIdentifier, model

def run(classifier, setting, zemberek):
    while True:
        print("Enter email (type -q to exit): ")
        buffer = []
        run=True
        while run:
            line = sys.stdin.readline().rstrip('\n')
            if line == '-q':
                run = False
                print("Processing mail...")
            else:
                buffer.append(line)
        strr = ' '.join(buffer)
        identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        result = identifier.classify(strr)
        if result[0] == 'tr':
            print("TURKISH input!")
            if zemberek == True:
                features = util.extractFeaturesWZemberek(strr, setting, tp)
            else : 
                features = util.extractFeatures(strr, setting, tp)
        else :
            print("EN input!")
            features = util.extractFeatures(strr, setting, en)
            
        if (len(features) == 0):
            break
        print (classifier.classify(features))
        
def runSeparate(en_classifier, tr_classifier, setting, zemberek):
    while True:
        print("Enter email (type -q to exit): ")
        buffer = []
        run=True
        while run:
            line = sys.stdin.readline().rstrip('\n')
            if line == '-q':
                run = False
                print("Processing mail...")
            else:
                buffer.append(line)
        strr = ' '.join(buffer)
        identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        result = identifier.classify(strr)
        if result[0] == 'tr':
            print("TURKISH input!")
            if zemberek == True:
                features = util.extractFeaturesWZemberek(strr, setting, tp)
            else : 
                features = util.extractFeatures(strr, setting, tp)
            if (len(features) == 0):
                break
            print (tr_classifier.classify(features))
        else :
            print("EN input!")
            features = util.extractFeatures(strr, setting, en)
            if (len(features) == 0):
                break
            print (en_classifier.classify(features))
 
def train(features, samples_proportion):
    train_size = int(len(features) * samples_proportion)
    train_set, test_set = features[:train_size], features[train_size:]
    classifier = NaiveBayesClassifier.train(train_set)
    return train_set, test_set, classifier
 
if __name__ == "__main__":
        
    mode = ''
    if 'bow' in str(sys.argv):
        mode = 'bow'
        print('Bag of words model')
    
    zemberek = False
    if 'zemberek' in str(sys.argv):
        zemberek = True
        print('Extracting Turkish features with Zemberek!')
        
    separate = False
    if 'separate' in str(sys.argv):
        separate = True
        print('Using separate classifiers')
    
    allMails = []
    turkishMails = []
    englishMails = []
    spam_en = util.extractEmlMails('data/english/spamassassin/spam/')
    spam_en += util.extractEmlMails('data/english/spamassassin/spam_2/')
    ham_en = []
    ham_en += util.extractEmlMails('data/english/spamassassin/easy_ham/')
    ham_en += util.extractEmlMails('data/english/spamassassin/hard_ham/')
    spam_tr = tp.parseTurkishFiles('data/turkish/spam/training/')
    ham_tr = tp.parseTurkishFiles('data/turkish/ham/training/')

    englishMails = [(email, 'spam') for email in spam_en]
    englishMails += [(email, 'ham') for email in ham_en]
    
    turkishMails += [(email, 'ham') for email in ham_tr]
    turkishMails += [(email, 'spam') for email in spam_tr]
    
    allMails += turkishMails
    allMails += englishMails
    
    util.randomize(allMails)
    print ('TR Data size = spam: ' + str(len(spam_tr)) + ' ham: ' + str(len(ham_tr)) + ' total: ' + str(len(turkishMails)) + ' emails')
    print ('EN Data size = spam: ' + str(len(spam_en)) + ' ham: ' + str(len(ham_en)) + ' total: ' + str(len(englishMails)) + ' emails')
    print ('ALL Data size = spam: ' + str(len(spam_en) + len(spam_tr)) + ' ham: ' + str(len(ham_en)+len(ham_tr)) + ' total: ' + str(len(allMails)) + ' emails')
    
    all_features = []
    turkishFeatures = []
    if zemberek:
        turkishFeatures = [(util.extractFeaturesWZemberek(email, mode, tp), label) for (email, label) in turkishMails]
    else :
        turkishFeatures = [(util.extractFeatures(email, mode, tp), label) for (email, label) in turkishMails]
    
    englishFeatures = [(util.extractFeatures(email, mode, en), label) for (email, label) in englishMails]

    all_features += turkishFeatures
    all_features += englishFeatures
        
    if separate == False:
        train_set, test_set, classifier = train(all_features, 0.8)
        print ('Accuracy on the training set = ' + str(classify.accuracy(classifier, train_set)))
        print ('Accuracy of the test set = ' + str(classify.accuracy(classifier, test_set)))
        classifier.show_most_informative_features(30)
        run(classifier, mode, zemberek)
    else:
        tr_train_set, tr_test_set, tr_classifier = train(turkishFeatures, 0.8)
        en_train_set, en_test_set, en_classifier = train(englishFeatures, 0.8)
        print ('Accuracy on the TR training set = ' + str(classify.accuracy(tr_classifier, tr_train_set)))
        print ('Accuracy of the TR test set = ' + str(classify.accuracy(tr_classifier, tr_test_set)))
        tr_classifier.show_most_informative_features(30)
        print ('Accuracy on the ENG training set = ' + str(classify.accuracy(en_classifier, en_train_set)))
        print ('Accuracy of the ENG test set = ' + str(classify.accuracy(en_classifier, en_test_set)))
        en_classifier.show_most_informative_features(30)
        runSeparate(en_classifier, tr_classifier, mode, zemberek)

    
    