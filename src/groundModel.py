""" Pseudocode for the planned ground-finding model"""

# imports
# define cmdargs for infile/outfile, settings

# new class for model

#    init class
#      run some methods automatically???

#    def readTiffs
#       Open geotiff
#       read into array (2D?)
#       extract values at point of footprint coords
#       How to deal with diff pixel sizes?
#       Potentially make plot as sanity check? or set as optional

#    def trainTest
#        split datasets 80/20 based on location?
#        by shape, possibly clip with shapefile?

#    def rfGround
#       decompose waveform into gaussians???
#       centre of lowest gaussian above noise is ground???
#       how to approach ground finding- is it that you find ground on easy waveforms first, then worry about difficult ones,
#       Or, run same alg on all??
#       Random forest
#       apply test/train split to dataset
#       plot variables to look at distribution
#            which are?????
#            shape of gaussian? but confused with dimensions. nd array against 1 pixel srtm, ndvi
#            canopy height metrics perhaps? but correlation with waveform shape!
#       print correlations
#       run random forest regressor
#       print coefficients, R2, rmse, bias
#       plot map of predictions
#       add linear regression to output - compare y_pred to y_test
#           print scores
#           plot prediction
#      find residuals

# main block
# def cmdargs
# run model?
