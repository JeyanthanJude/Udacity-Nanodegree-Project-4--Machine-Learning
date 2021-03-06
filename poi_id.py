#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi',
                 'salary',
                 'total_payments',
                 'bonus',
                 'bonus_salary_ratio',
                 'total_stock_value',
                 'exercised_stock_options',
                 'shared_receipt_with_poi',
                 #'from_this_person_to_poi',
                 #'from_poi_to_this_person',
                 'from_to_poi_ratio',
                 'from_this_person_to_poi_ratio',
                 'from_poi_to_this_person_ratio'] 

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers

data_dict.pop("TOTAL")
data_dict.pop("THE TRAVEL AGENCY IN THE PARK")

### Task 3: Create new feature(s)

# Bonus to salary ratio
for members, features in data_dict.iteritems():
    if features['bonus'] == "NaN" or features['salary'] == "NaN":
        features['bonus_salary_ratio'] = "NaN"
    else:
        features['bonus_salary_ratio'] = float(features['bonus']) / float(features['salary'])

# from_this_person_to_poi/from_messages
for members, features in data_dict.iteritems():
    if features['from_this_person_to_poi'] == "NaN" or features['from_messages'] == "NaN":
        features['from_this_person_to_poi_ratio'] = "NaN"
    else:
        features['from_this_person_to_poi_ratio'] = float(features['from_this_person_to_poi']) / float(features['from_messages'])

# from_poi_to_this_person/to_messages
for members, features in data_dict.iteritems():
    if features['from_poi_to_this_person'] == "NaN" or features['to_messages'] == "NaN":
        features['from_poi_to_this_person_ratio'] = "NaN"
    else:
        features['from_poi_to_this_person_ratio'] = float(features['from_poi_to_this_person']) / float(features['to_messages'])

# from_poi_to_this_person/from_this_person_to_poi
for members, features in data_dict.iteritems():
    if features['from_poi_to_this_person'] == 0 or features['from_poi_to_this_person'] == 'NaN' or features['from_this_person_to_poi'] == 0 or features['from_this_person_to_poi']=='NaN':
        features['from_to_poi_ratio'] = 'NaN'
    else:
        features['from_to_poi_ratio'] = float(features['from_poi_to_this_person']) / float(features['from_this_person_to_poi'])
        

### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline


scaler = MinMaxScaler()
best = SelectKBest()
dt = DecisionTreeClassifier()
svc = SVC()
pca = PCA()
rf  = RandomForestClassifier()

#Pipeline process
process = [
         # Preprocessing
         # ('min_max_scaler', scaler),
    
         # Feature selection
         ('feature_selection', best),
         
         # Dimentionality 
         #('Principal_component', pca),
         
         # Classifier
         ('decision_tree', dt)
         #'svc', svc)
        # ('random_forest',rf)

        ]
         
# Create pipeline
pipeline = Pipeline(process)    

#Parameters for gridsearch
parameters = dict(
                  feature_selection__k=[3,4,5,6,8,9],
                  #Principal_component__n_components=[2,3,4],
                  decision_tree__class_weight=[None, 'balanced'],
                  decision_tree__criterion=['entropy'],
                  decision_tree__max_depth=[None, 2, 3, 4,5],
                  decision_tree__min_samples_split=[2, 3, 4, 25]
                  #svc__C=[0.1, 1, 10, 100, 1000],
                  #svc__kernel=['rbf'],
                  #svc__gamma=[0.001, 0.0001]
                  #random_forest__n_estimators=[10,15,20],
                  #random_forest__max_depth=[None, 2, 3, 4],
                  #random_forest__min_samples_split=[2,5,10],
                  #random_forest__criterion =['gini', 'entropy']
                  )


### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)
    
# Grid Search     
grid = GridSearchCV(pipeline,param_grid=parameters,scoring="f1",error_score=0)

grid.fit(features_train, labels_train)
labels_predictions = grid.predict(features_test)

# Pick the classifier with the best tuned parameters
clf = grid.best_estimator_

print "\n", "The best parameters are: ", grid.best_params_, "\n"

print "\n","The selected features are :"
features_selected=[features_list[i+1] for i in clf.named_steps['feature_selection'].get_support(indices=True)]
scores = clf.named_steps['feature_selection'].scores_


# Metrics
report = classification_report( labels_test, labels_predictions )
print(report)    
    
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)