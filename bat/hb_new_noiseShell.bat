G:\LAStools\bin\txt2las.exe -i P:\dissertation\dissertation_AH24\data\hubbard_brook\pts_metric\*.pts -odir P:\dissertation\dissertation_AH24\data\hubbard_brook\sim_las -utm 19N -cores 8
G:\LAStools\bin\lasnoise.exe -i P:\dissertation\dissertation_AH24\data\hubbard_brook\sim_las\*.las -odir P:\dissertation\dissertation_AH24\data\hubbard_brook\sim_cleaned -step_xy 4 -step_z 5 -isolated 3 -remove_noise -cores 8
G:\LAStools\bin\lasground_new.exe -i P:\dissertation\dissertation_AH24\data\hubbard_brook\sim_cleaned\*.las -odir P:\dissertation\dissertation_AH24\data\hubbard_brook\sim_ground40051 -step 40 -offset 0.5 -spike 1  -cores 8