# gtfs-hk
This repository aims to create gtfs file for the Hong Kong transportation sytem using the data from data.gov.hk.

It hopes to make use of the open source communitiy to generate the GTFS file that can have huge benefits in creating open source trip planning applications. 

# Command line interface
This package can be used through command line.

### To download mdb files
```python cli.py download-mdb```

This downloads all the Access database files to a sub folder called 'mdb'.

### To download pkl files
To be done. You may download them manually from the release page of this github repo.

### To convert mdb files to pkl files
```python cli.py process-mdb```

This converts the mdb files into pickle files, which has the pandas dataframe type.

### To generate GTFS zip file
```python cli.py gen-gtfs```

This takes all the pickle files and generates the GTFS zip file.

# License
The app is released under the GPL License and more information can be found in the LICENSE file.

# Contributions
gtfs-hk is a project to gather the community effort in standardizing the GTFS file for the Hong Kong transportation system.

Contributions are sincerely welcome!
