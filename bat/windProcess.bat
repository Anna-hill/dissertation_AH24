G:\LAStools\bin\lasmerge.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\raw_las\*.las -o Z:\s2559258\dissertation_AH24\data\wind_river\als_merged.las

G:\LAStools\bin\lastile.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\als_merged.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\als_tiled -tile_size 500 -buffer 30 -cores 8

G:\LAStools\bin\lasnoise.exe -i Z:\s2559258\dissertation_AH24\data\wind_river\als_tiled\*.las -odir Z:\s2559258\dissertation_AH24\data\wind_river\als_cleaned -step_xy 4 -step_z 0.5 -isolated 3 -remove_noise -cores 8
