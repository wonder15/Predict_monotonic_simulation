# Predict_monotonic_simulation
This script ingests an excel sheet with ROI in WHOLE NUMBER FORMAT (E.G. 5% = 5) assuming that ROI is in column H. By bootstrapping reconstruction confidence intervals are then created for the data. Given ROI is relative, confidence intervals on the ROI only provide the simulated results of a fixed, homogenous bet amount.

To conserve memory, the population is iterated through batch sizes of 200mb to bootstrap 10,000 samples of size n = 1000 determine the simulated efficacy of prediction categories. 
