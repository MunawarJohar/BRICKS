# Important Considerations when making use of FEA tools

All scripts have been written to work with Diana 10.8, up to now it is not  known that the scripts don´t  work with other DIANA verions. Moreover the processing of the tabulated data was done for 2D analysis and therefore its resiliance has not been tested in 3D analysis and elements.

## Considerations when using analysis.py

The analysis of tabulated data will only work with the following tabulated output options. They assumme there is no page separations and an infinite number of columns. Therefore set the output with the following conditions in properties.

- Device: TABULATED
- Combine output items: TRUE
- Tabula layout:    Number of lines per page = 0
                    Number of columns per page = 100000
                    Number of digits for analysis results = 4
                    Number of digits for point (Node) Coordinates = 4
                    Number of digits for the direction of the local axes = 4

- Output all variables through RESULT -> User selection (Variables outputted to Nodes and IntPnts need to be put in different outputs, in the end the results will be appended to the same file)
- Result -> User Selection -> Properties -> Options : Location Coordinates

Other considerations, 

- Plots and analysis have been made assuming SI Units except for length which has been outputted in mm
- The analysis do not output the units therefore these have to be checked before outputting any values

## Considerations when using plots.py
