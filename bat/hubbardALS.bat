G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\raw_las\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\als_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 3

G:\LAStools\bin\lasground_new.exe -i Z:\s2559258\dissertation_AH24\data\hubbard_brook\als_cleaned\*.las -odir Z:\s2559258\dissertation_AH24\data\hubbard_brook\als_ground -step 40 -offset 0.5 -spike 0.5  -cores 3
