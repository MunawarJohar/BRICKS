# Evaluation of masonry structures undergoing subsidence processes

Due to the Netherlands' topological and geological nature, many areas  suffer from poor soil resistance, this has led to subsidence induced settlements occurring throughout the Netherlands. Thousands of homes have seen their structural integrity compromised in the forms of cracks and distortions, which in some instances has led to the necessity to intervene in building’s foundation systems to prevent subsidence processes from compromising further the structure, whereas in many other extreme cases, the only feasible course of action involved the demolition of the building. Therefore, efficient yet precise damage prediction to masonry structures due to subsidence, has the potential to pre-emptively determine the vulnerability of structures to eventually surpass their serviceability limit state and allow for the engineering of countermeasures to be implemented at times when intervention is still economically feasible. Therefore the following repository is part of a research effort that aims to assess and develop different tools to be in the assessment and analysis of masonry structures.

In the Netherlands, it has been customary for engineering consultants to perform inspections in those buildings affected by subsidence phenomena. Their assessment and investigation eventually take the form of a foundation assessment report whose, report and posterior assessment usually include the archival information of the building (year of construction, major remodelations..), an extensive building damage documentation presented in the form of images indicating the severity and location of the damage sustained by the building, a  measurements campaign to quantify the distortions experienced by the building in a skew measurement levelling graph at different locations in the building. Lastly, a simple soil exploration campaign to understand the capacity of the underneath soil and the location typology and dimensions of the foundation relative to the underneath strata. The objective is to investigate and develop tools the necessary tools to make use such data to perform vulnerability assessments of such structures.

> <span style="font-size: larger;">Project Objective:</span> To develop and asses available methods in the evaluation of structural damage to masonry structures undergoing urban shallow subsidence<br>
> The development and analysis of analytical and numerical solutions, to preemptively determine the vulnerability of structures.

 <img src=".github\public_html\fig\buildingdamage.svg" alt="Masonry structure accommodating to a subsidence surface" style="object-fit: cover">|<img src=".github\public_html\fig\assessment_report\skew_measurements.png"> |
|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
|**Figure 1:** Masonry structure accommodating to a subsidence surface |**Figure 2:** Exemplary skew measurement diagram |


## Perform your own assessment

### 1. Instantiate your own `HOUSE` and calculate its characteristic values

From your building assessment report of self taken measurements you only require to define the basic geometry and continous layout of your building. With it is necessary to provide the subsidence measurements and their location continuously along the wall.

```python
walls = {
    'wall1':{"x": np.array([0, 0, 0]), "y": np.array([0, 3.5, 7]), "z": np.array([0, -72, -152]), 'phi': np.array([1/200,1/200]), 'height': 5000, 'thickness': 27},
    'wall2':{"x": np.array([0, 4.5, 8.9]), "y": np.array([7, 7, 7]), "z": np.array([-152, -163, -188]),  'phi': np.array([1/33,1/50]), 'height': 5000, 'thickness': 27},
    'wall3':{"x": np.array([8.9, 8.9]), "y": np.array([3.6, 7]), "z": np.array([-149, -188]), 'phi': np.array([0,0]), 'height': 5000, 'thickness': 27},
    'wall4':{"x": np.array([8.9, 10.8]), "y": np.array([3.6, 3.6]), "z": np.array([-149,-138]), 'phi': np.array([0,0]), 'height': 5000, 'thickness': 27},
    'wall5':{"x": np.array([10.8, 10.8]), "y": np.array([0, 3.6]), "z": np.array([-104, -138]), 'phi': np.array([1/77,1/67]), 'height': 5000, 'thickness': 27},
    'wall6':{"x": np.array([0, 5.2, 6.4, 8.9, 10.8]), "y": np.array([0, 0, 0, 0, 0]), "z": np.array([0, -42, -55, -75, -104]), 'phi': np.array([1/100,1/100]), 'height': 5000, 'thickness': 27},
}

ijsselsteinseweg = house(measurements = walls)
```
Estimate the Soil related intensity factors through the SRI method:

```python
ijsselsteinseweg.SRI()
```
which produces the following output,

|     | Smax | dSmax |       D/L |   drat |   omega |     phi |     beta |
|-----|------|-------|-----------|--------|---------|---------|----------|
| **0** |  152 |   152 | 21.714286 |  4.000 | 1.524776| 1.524776| 3.049552 |
| **1** |  188 |    36 |  4.044944 |  7.202 | 1.328434| 1.328434| 2.656867 |
| **2** |  188 |    39 | 11.470588 |  0.000 | 1.483837| 1.483837| 0.000000 |
| **3** |  149 |    11 |  5.789474 |  0.000 | 1.399757| 1.399757| 0.000000 |
| **4** |  138 |    34 |  9.444444 |  0.000 | 1.465307| 1.465307| 0.000000 |
| **5** |  104 |   104 |  9.629630 | 10.704 | 1.467321| 1.467321| 2.934642 |

**Table 1:** Settlement related intensity factors

Aproximate and reconstruct the displacement surface of the building by first interpolating the buildings displacement field `house.interpolate()` then fit your prefered charateristic soil displacement equation by default it makes use of `guassian_shape`:

```python
def gaussian_shape(x, s_vmax, x_inflection):
    gauss_func = s_vmax * exp(-x**2/ (2*x_inflection**2))
    return gauss_func
```
then use the `house.fit_function` method to estimate the nearby soil subsidence surface.

```python
ijsselsteinseweg.fit_function(i_guess = 1, tolerance = 1e-2, step = 1) # Fit gaussian shapes to walls
plots.subsidence(ijsselsteinseweg, building = False, soil= True, deformation= True)
```
The surface can the be visualised as follows,


<img src="public_html\_data\fig\subsidence_surface.png">

**Figure 5:** Visualised aproximated soil surface for Ijsselsteinseweg 77.

### 2. Perform your preliminary assessment of your building

The bricks module currently provides two main functionalities to assess a building, one is through a compilation of empirical methods i.e empirical correlations that have been determined by researchers linking the amount of damage expected in a building due to its current situation. And secondly the LTSM a elementary structural mechanical approach the displacement and strains of the building subject to a subsidence distribution.

### 2.1 Assesment against empirical methods

 Firstly it asseses the buildings vulnerability through a compilation of state-of-the-art limits gathered from different sources `empirical_limits.py` which are then evaluated through the Empirical methods 'EM()' function against a dictionary of SRI parameters. When making use of the 'house' class and having made use of the `SRI()` method the function can be called as follows, 

```python
ijsselsteinseweg.SRI(tolerance= 0.01) #Compute the SRI parameters
report = EM(ijsselsteinseweg.soil['sri'])

app = EM_plot(report)
app.run_server(port=8051, debug=False)
```
The output will be a report with the assessment state source and SRI parameter evaluated. As can be seen above the making use of `bricks.tools` the `EM_plot()` can be called which will help you visualise the assessments reports. An example of the above is the following,

<img src="public_html\_data\fig\EM_assess.png">

**Figure 6:** Visualisation matrix of results from different assessment methods

### 2.1 Assesment through Burland & Wroth (1974) -> `LTSM`

The second main available assessment method is the LTSM. This method was devised by Burland & Wroth (1974) and was then expanded by other researchers such as Boscardin & Cording (1989). This method schematises a building or wall as an equivalent masonry beam and a Timoschenko beam formulation from which the subsidence through is applied. From here onwards the hogging and sagging regions of the before estimated gaussian settlement troughs are calculated and the estimation of the building strains is performed. The following is an example of use of its relevant methods.

```python
limit_line = -1
eg_rat =  2.6  ## May vary # Calibrate

LTSM(ijsselsteinseweg, limit_line, eg_rat, save = True)
app = plots.LTSM_plot(ijsselsteinseweg)    

app.run_server(debug=False)
```

The produced plot when performing the evaluation is the following,

<img src="public_html\_data\fig\LTSM_assess.png">

**Figure 7:** Visualisation of LTSM

## Breakdown of the `bricks` module and the repository

Bricks is a in development module which aims to help engineers and homeowners in the netherlands be able to evaluate the vulnerability of their houses through accessible easy to use tools. The module has three main components.

1. **`house`** : A class which allows you to create an object of your own house and also provides the basic functionalities to process your building's soil and structural characteristic values relevant to the posterior analysis.
2. **`bricks.assessment`** : Sub-module that contains the state-of-the-art analysis techniques relevant to perform a pre-emptive assessment of your structure. The current available methods available 'assess.py' are the LTSM and a compilation of empirically determined thresholds of a structures KPI's. Although effective it is important to note some of these tools lack the precision of other FEM counterparts and aim to serve as tools for educated decision making for accessible vulnerability assessment or to determine the necessity of more precise assessment methods to be employed.
3. **`bricks.tools`**: Sub-module that contains primarily the tools to visualise the different assessment methods performed and to visualise the current state of your building.  

In addition the main directory contains `Ijsselsteinseweg 77.ipynb` a exemplary notebook which illustrates how to perform the assessment of your building and how to utilise the visualisation tools available from 'bricks'. This is carried out through analysis of a real world scenario.  
