G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\Bonaly\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\Bonaly\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\nouragues\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\nouragues\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\paracou\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\paracou\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\robson_creek\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\robson_creek\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3
G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\sim_las\*.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3

G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\Bonaly\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\Bonaly\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\la_selva\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\la_selva\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\nouragues\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\nouragues\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\oak_ridge\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\paracou\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\paracou\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\robson_creek\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\robson_creek\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\sim_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\sim_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
