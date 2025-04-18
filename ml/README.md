# ml
This folder contains python files for 4 machine learning projects, authored by Tyler Gourley

NOTE: these .ipynb files were designed to be ran on Google Colab, not all packages used are included in the requirements.txt venv

**Project 1** kNN and Decision Trees
  kNN and Decision trees both performed pretty well
**Project 2** Linear Regression
  linear regression did not perform very well
  linear regression with polynomial features ran into the following problem:
  Modeling a higher degree polynomial requires combinatorially increasing features. In general, with 𝑛 original features and degree 𝑑, you get roughly (n+d)C(d) new features. For our dataset where we have 55 features per sample, to model a degree-3 polynomial, our dataset would have (58)C(3) = 30,856 features per sample (over 560 times larger than our original dataset). To solve this problem, we would need to in some way limit the number of features of our dataset. I have come up with some ideas to consolidate the features but still describe the data in a useful manner: use average and standard deviation of the features [2 features], take quartile scores (median, upper and lower quartiles, and maximum and minimum) [5 features], randomly drop 60% of the features (similar to dropout in a neural network) [33 features], and distribute the features in buckets based position (forwards, midfielders, and defenders) and take the average of each [3 features].
**Project 3** Bagging and Boosting
  
**Project 4** nueral networks