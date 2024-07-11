G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\Bonaly\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\Bonaly\sim_las -utm 30U
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_las -utm 19N
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_las -utm 16N
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\nouragues\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\nouragues\sim_las -utm 22N
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_las -utm 16N
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\paracou\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\paracou\sim_las -utm 22N
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\robson_creek\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\robson_creek\sim_las -utm 55S -cores 6
G:\LAStools\bin\txt2las.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\pts_metric\*.pts -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_las -utm 10N

G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\Bonaly\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\Bonaly\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\nouragues\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\nouragues\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\paracou\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\paracou\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\robson_creek\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\robson_creek\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3