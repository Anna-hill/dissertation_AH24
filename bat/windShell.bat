G:\LAStools\bin\txt2las.exe -i P:\dissertation\dissertation_AH24\data\wind_river\pts_metric\*.pts -odir P:\dissertation\dissertation_AH24\data\wind_river\sim_las -utm 16N -cores 8
G:\LAStools\bin\lasnoise.exe -i P:\dissertation\dissertation_AH24\data\wind_river\sim_las\*.las -odir P:\dissertation\dissertation_AH24\data\wind_river\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 8

