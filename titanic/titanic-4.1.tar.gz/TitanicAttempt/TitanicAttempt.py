import pandas as pd
from sklearn.ensemble import RandomForestClassifier as RFC

def Read_Files(FileName):
    """
    Accepts file name string, reads in file, then converts and returns pd.DataFrame type
    """
    DataFrame=pd.read_csv(FileName)
    return DataFrame


def Feature_Engineering(DataFrame,train):
    """
    Accepts string for DataFrame file and training set with creates and returns new pd.DataFrame, with important features extracted and in a useable form
    """
    DataFrame= Read_Files(DataFrame)
    titles=DataFrame['Name'].apply(lambda x: x.split(',')[1].split(' ')[1])
    title_mapping = {"the":5, "Mr.": 1, "Miss.": 2, "Mrs.": 3, "Master.": 4, "Dr.": 5, "Rev.": 6, "Major.": 7, "Col.": 7, "Mlle.": 2, "Mme.": 3, "Don.": 9, "Lady.": 10, "Countess.": 10, "Jonkheer.": 10, "Sir.": 9, "Capt.": 7, "Ms.": 2, "Dona.": 10}
    for k,v in title_mapping.items():
        titles[titles == k] = v
    DataFrame["Title"] = titles

    DataFrame['NameLen']=DataFrame['Name'].apply(lambda x: len(x))
    DataFrame['FamSize']=DataFrame['SibSp']+DataFrame['Parch']
    DataFrame['Has_Cabin'] = DataFrame["Cabin"].apply(lambda x: 0 if type(x) == float else 1)
    cabins=DataFrame['Cabin'].apply(lambda x:   str(x)[0])
    cabin_mapping={'A':3,'B':5,'C':5,'D':4,'E':4,'F':3,'G':2,'T':1,'n':10}
    for k,v in cabin_mapping.items():
        cabins[cabins==k]=v
    DataFrame['Cabin']=cabins  
    del DataFrame['Parch']
    del DataFrame['SibSp']
    del DataFrame['PassengerId']

    pclass = pd.get_dummies( DataFrame.Pclass , prefix='Pclass' )
    sex = pd.get_dummies(DataFrame.Sex)
    embarked = pd.get_dummies(DataFrame.Embarked, prefix='Embarked')
    DataFrame=pd.concat([DataFrame,pclass,sex,embarked],axis=1)
    del DataFrame['Pclass']
    del DataFrame['Name']
    del DataFrame['Ticket']
    del DataFrame['Sex']
    del DataFrame['Embarked']
    
    DataFrame['Fare'].fillna(train['Fare'].median(), inplace = True)
        # Mapping Fare
    DataFrame.loc[ DataFrame['Fare'] <= 7.91, 'Fare'] 						        = 0
    DataFrame.loc[(DataFrame['Fare'] > 7.91) & (DataFrame['Fare'] <= 14.454), 'Fare'] = 1
    DataFrame.loc[(DataFrame['Fare'] > 14.454) & (DataFrame['Fare'] <= 31), 'Fare']   = 2
    DataFrame.loc[ DataFrame['Fare'] > 31, 'Fare'] 							        = 3
    DataFrame['Fare'] = DataFrame['Fare'].astype(int)
    DataFrame['Age'].fillna(train['Age'].median(), inplace = True)

    return DataFrame


def Create_Random_Forest(train):
    """
    Accepts string filename for train and uses to create and return sklearn.ensemble.Random_Forest_Classifier fitted to training set.
    ~78.4% accuracy 
    """
    trainDF=pd.read_csv(train)
    train=Feature_Engineering(train,trainDF)
    RF = RFC(min_samples_split=10, n_estimators= 700, criterion= 'gini', max_depth=None)
    RF.fit(train.iloc[:, 1:], train.iloc[:, 0])
    return RF


def Produce_Predictions(FileName,train,test):
    """
    Accepts string FileName
    Uses Random Forest to create predictions on who survived.
    returns nothing, creates csv file named from parameter FileName in which predictions are contained for testing set.
    """
    TestFileName=test
    TrainFileName=train
    trainDF=pd.read_csv(train)
    train=Feature_Engineering(train,trainDF)
    test=Feature_Engineering(test,trainDF)
    MLA=Create_Random_Forest(TrainFileName)
    predictions = MLA.predict(test)
    predictions = pd.DataFrame(predictions, columns=['Survived'])
    test = pd.read_csv(TestFileName)
    predictions = pd.concat((test.iloc[:, 0], predictions), axis = 1)
    predictions.to_csv(FileName, sep=",", index = False)
    #~ 75% :)
    
    
if __name__=="__main__":
    Produce_Predictions('TestRun.csv') # pragma: no cover
