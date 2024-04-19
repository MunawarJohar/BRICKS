# Evaluation of masonry structures undergoing subsidence processes

Due to the topological and geological nature of the Netherlands many areas around the country suffer from poor soil resistance which makes construction and engineering of structures increasingly difficult. Therefore, in thousands of cases around the country in different stages of a structure’s lifespan, the capacity required from the soil by structures has been insufficient. Moreover, masonry constitutes a nationally popular construction material in the Netherlands, particularly in the case of residential homes. Masonry structures are understood to be more prone to damage when they suffer changes in their structural equilibrium, this is commonly attributed to their hybrid composition and the plentiful locations for failure envelopes to develop along the discrete block interfaces in a masonry structure’s envelope. Therefore, throughout the Netherlands, thousands of homes have seen their structural integrity compromised by cracks and distortions through the introduced subsidence-led distortions. In some cases this has led to the necessity to intervene in the building’s foundation systems to prevent the effects of further subsidence effects, whereas in many other extreme cases demolition was deemed the only viable course of action. Therefore, efficient yet precise damage prediction to masonry structures due to subsidence has the potential to preemptively determine the vulnerability of structures and allow for the engineering of countermeasures to be implemented at times when intervention is still economically feasible. Therefore the tools in this repository aim to fulfil the following objective.

> <span style="font-size: larger;"><B>Project Objective:</B></span> To develop and asses available methods in the evaluation of structural damage to masonry structures undergoing urban shallow subsidence<br>
> The development and analysis of analytical and numerical solutions, to preemptively determine the vulnerability of structures.

|<img src="_data\fig\building_model.svg" alt="Building Numerical modelling scheme" style=object-fit: cover;"> | <img src="_data\fig\buildingdamage.svg" alt="Masonry structure accommodating to a subsidence surface" style=object-fit: cover;">|
|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
|**Figure 1:** Building Numerical modelling scheme | **Figure 2:** Masonry structure accommodating to a subsidence surface |

In the Netherlands, it has been customary for engineering consultants to perform inspections in those buildings affected by subsidence phenomena. Their assessment and investigation eventually take the form of a foundation assessment report. In this report the inspection and posterior assessment findings are presented, its contents usually include the archival information of the building (year of construction, major remodelations..). An extensive building damage documentation presented in the form of images indicating the severity and location of the damage sustained by the building, a  measurements campaign to quantify the distortions experienced by the building, usually taking the form of skew measurements at different locations in the building. Lastly, a simple soil exploration campaign to understand the capacity of the underneath soil and the location typology and dimensions of the foundation relative to the underneath strata.

|<img src="_data\fig\assessment_report\skew_measurements.png"> | <img src="_data\fig\assessment_report\soil_exploration.svg">|
|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
|**Figure 3:** Exemplary skew measurement diagram | **Figure 4:** Masonry structure accommodating to a subsidence surface |

## Perform your own assessment

### 1. Instantiate your own `HOUSE`

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

## Breakdown of the `bricks` module and the repository

Bricks is a in development module which aims to help engineers and homeowners in the netherlands be able to evaluate the vulnerability of their houses through accessible easy to use tools. The module has three main components.

1. **`house`** : A class which allows you to create an object of your own house and also provides the basic functionalities to process your building's soil and structural characteristic values relevant to the posterior analysis.
2. **`bricks.assessment`** : Sub-module that contains the state-of-the-art analysis techniques relevant to perform a pre-emptive assessment of your structure. The current available methods available 'assess.py' are the LTSM and a compilation of empirically determined thresholds of a structures KPI's. Although effective it is important to note some of these tools lack the precission of other FEM counterparts and aim to serve as tools for educated decision making for accessible vulnerability assessment or to determine the necessity of more precise assessment methods to be employed.
3. **`bricks.tools`**: Sub-module that contains primarily the tools to visualise the different assessment methods performed and to visualise the current state of your building.  

In addition the main directory contains `Ijsselsteinseweg 77.ipynb` a exemplary notebook which illustrates how to perform the assessment of your building and how to utilise the visualisation tools available from 'bricks'. This is carried out through analysis of a real world scenario.  
