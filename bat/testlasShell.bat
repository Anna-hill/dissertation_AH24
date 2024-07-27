G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\test\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\test\sim_las -utm 16N
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\test\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\test\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\test\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\test\sim_ground400505 -step 40 -offset 0.5 -spike 0.5  -cores 3





