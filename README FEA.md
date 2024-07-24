# Important Considerations when making use of FEA tools

All scripts have been written to work with Diana 10.8, up to now it is not  known that the scripts don´t  work with other DIANA verions. Moreover the processing of the tabulated data was done for 2D analysis and therefore its resiliance has not been tested in 3D analysis and elements.

## Considerations when using fea.diana 

### Considerations when using tabulated.py

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

### Considerations when using compare_models and  from main.py based on tabulted.py and out.py

When running a individual model comparison the processing and plotting of the results require the following information based on the three main analysis forms available 

1. 'Mutual' = The comparison in displacements between different nodes in a model
2. 'Crack-width' = The crack width development of different cracks in the model, this requires the definition of the final crack pattern where the maximum crack-width will be displayed
3. 'Damage-level' = The damage parameter estimation for the model, where given the element size to calculate the crack length and the crack-widths the average crack-wdith is calculated by taking at a given load step the elements where a crack is already existing in a given element.

```python
analysis_info_TSRCM = {
    'Relative displacement': {
        'Node Nr': [22, 23]
    },
    'Mutual': {
        'Node Nr': [[22, 23], [22, 23]],
        'Reference': [['TDtY', 'TDtY'], ['TDtY', 'TDtX']]
    },
    'Crack width': {
        'EOI': [[177,178,179,435],
                [35, 166, 203, 387, 523, 684, 723, 867],
                [9, 206, 263, 612]],
    },
    'Damage level': { 
        'parameters': {
            'cracks': [{
                'EOI': [[177,178,179,435],
                        [35, 166, 203, 387, 523, 684, 723, 867],
                        [9, 206, 263, 612]],
                'element_size': 200,}]         
    }
}}

plot_settings = {
    'Relative displacement': {
        'traces': ['A - Experienced displacement\n[Node 22, Bottom-left]', 'B - Applied Displacement\n[Node 23, Top-left]'],
        'labels': ['Load factor $\lambda$', 'Displacement $u_y$ [mm]'],
        'titles': 'Displacements at locations of interest',
        'scientific': True
    },
    'Mutual': {
        'traces': ['${u_{y,B}}/{u_{y,A}}$ [TSCM]','${u_{x,B}}/{u_{y,A}}$ [TSCM]'],
        'labels': ['Displacement A [mm]', 'Displacement B [mm]'],
        'titles': 'Relative displacements at locations of interest',
        'scientific': False
    },
    'Crack width': {
        'traces': ['Crack 1','Crack 5','Crack 9'],
        'labels': ['Load factor $\lambda$', 'Crack Width $c_w$ [mm]'],
        'titles': 'Major crack Width development',
        'scientific': True
    },
    'Damage level': {
        'traces': ['$\psi$F'],
        'labels': ['Load factor $\lambda$', 'Damage Parameter $\psi$'],
        'titles': 'Damage level progression',
        'scientific': True
    }
}
```
4. In addition to the standard analysis (if defined) the function will also process the solution characteristics of the analysis where if interested different plots can be merged together when they do not provide to much relevant information. This is one through the merge_info dictionary. 

```python
merge_info = {
    'Titles': ['Force norm', 'Displacement norm'],
    'x_label': 'Load factor $\lambda$',
    'y_label': 'Disp \& Force Norm $|\Delta_f| |\Delta_u|$',
    'title': 'Combined Force and Displacement Norms'
}

dir = r'\path_to_models'
analyse_models(dir,analysis_info, plot_settings, merge = merge_info)

```

When running a cross model comparison you can use the following definitions

```python
data_TSCM = {
    'name': 'TSCM-O',
    'analysis_info': combined_info_TSRCM,
    'plot_settings': combined_settings_TSRCM,
    'dir': r'path\to\TSCM\model_data.tb'
}

data_EMMO = {
    'name': 'EMM - O',
    'analysis_info': combined_info_EMMS,
    'plot_settings': combined_settings_EMMS,
    'dir': r'path\to\EMM\model_data.tb'
}

plot_data_list = [data_TSCM, data_EMMO]
cfigs = compare_models(plot_data_list)
```

### Considerations when using report.py

The purpose of this file is to build the scripts that can then be called in Diana. This assumes that all analysis where run with the same analysis config and the reporting config also should be the same. If not these have be defined on a per case basis.

```python
base_path = r'C:\Users\javie\OneDrive - Delft University of Technology\Year 2\Q3 & Q4\CIEM0500 - MS Thesis Project\!content\Experimentation\Modelling\Models'

config = {
    'results': [
        {
            'component': 'TDtY',
            'result': 'Displacements',
            'type': 'Node',
            'limits': [-35, -28, -24, -20, -16, -12, -8, -4, 0]
        },
        {
            'component': 'E1',
            'result': 'Total Strains',
            'type': 'Element',
            'location': 'mappedintpnt',
            'limits': [-0.004, -0.002, 0, 0.001, 0.0025, 0.005, 0.0075, 0.01, 0.02, 0.08]
        },
        {
            'component': 'S1',
            'result': 'Cauchy Total Stresses',
            'type': 'Element',
            'location': 'mappedintpnt',
            'limits': [-3.5, -2, -1, -0.05, -0.01, 0, 0.01, 0.05, 1, 3, 61]
        },
        {
            'component': 'Ecw1',
            'result': 'Crack-widths',
            'type': 'Element',
            'location': 'mappedintpnt',
            'limits': [0, 1, 2, 3, 4, 5, 10, 15, 20]
        }
    ],
    'script': {
        'analysis': "NLA",
        'load_cases': ['Building', 'Sub Deformation'],
        'load_steps': [30, 720],
        'load_factors_init': [0.0330000, 0.00138800],
        'snapshots': 6,
        'view_settings': {
            'view_point': [0, 0, 25.0, 0, 1, 0, 5.2, 3.1, 5.5e-17, 19, 3.25],
            'legend_font_size': 34,
            'annotation_font_size': 28
        }
    }
}

setup_analysis(base_path, config)
```



