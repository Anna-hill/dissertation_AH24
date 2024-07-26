# dissertation_AH24

teastMetric is a text file from GEDIMetric, values set according to defeault command line example. needs edititng, but acts as an example


# Random forest inspiration repo?
https://github.com/euanmitchell/dissertation/blob/main/randomForestLaSelva.py?fbclid=IwZXh0bgNhZW0CMTAAAR3IsicGlxO0u7OIWCq35MwXTXyCzb2jJgESaRaVXzEb2mNHExP1gpjeoUQ_aem_ATb_y6Izy0lzdKaQKvLxPQaDP53R-VWldfGJ_uvXlyBY8qP6x-h8_AA1GzBH3MA8dZev_HfVS-GaodsUtGLl6WGD

testShell aims to perform automated processing to simulate waveforms

example command:

>> python3 src/testShell.py --studyarea all --noise -1 --pcount -1

python3 src/testShell.py --everywhere 1 --noise -1 --pcount 500

python3 src/testShell.py --everywhere 1 --noise 104 --pcount 149

python3 src/testShell.py --studyarea Bonaly --noise 104 --pcount 149

python3 src/testShell.py --studyarea hubbard_brook --noise -1 --pcount 149
python3 src/testShell.py --studyarea la_selva --noise -1 --pcount 149
python3 src/testShell.py --studyarea robson_creek --noise -1 --pcount 149
python3 src/testShell.py --studyarea test --noise -1 --pcount 149


python3 src/dtmShell.py --studyarea all --lassettings 400505
python3 src/dtmShell.py --studyarea Bonaly
python3 src/dtmShell.py --studyarea test
python3 src/dtmShell.py --studyarea hubbard_brook --lassettings 400505 --interpolate True
python3 src/dtmShell.py --studyarea la_selva --lassettings 400505
python3 src/dtmShell.py --studyarea oak_ridge --lassettings 600501 --interpolate True



run 1: hansen vals
- exc. or
python3 src/testShell.py --everywhere 1 --noise -1 --pcount 115
python3 src/testShell.py --studyarea hubbard_brook --noise -1 --pcount -1
python3 src/testShell.py --studyarea nouragues --noise -1 --pcount 149
python3 src/testShell.py --studyarea test --noise -1 --pcount -1

# evening of 12/06

python3 src/testShell.py --everywhere 1 --noise -1 --pcount 149
python3 src/testShell.py --everywhere 1 --noise 149 --pcount 149

##########
how many shells is tooooo many:
python3 src/shellSquared.py --studyarea all --lassettings all



python3 src/analyseResults.py --studyarea la_selva --lassettings 400505 --interpolation _linear
python3 src/analyseResults.py --studyarea hubbard_brook --lassettings 400505 --interpolation _linear