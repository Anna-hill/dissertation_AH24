G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_las -utm 19N
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3

G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_las -utm 16N
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3

G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_las -utm UTM 16N
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3

G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_las -utm 10N
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
