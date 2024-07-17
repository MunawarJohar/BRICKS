from dataclasses import dataclass, field
from typing import List, Union, Dict

@dataclass
class LimitEntry:
    source: str
    limits: List[Union[float, int]]
    description: List[str]
    DL: List[int]  # Damage Level indices

@dataclass
class ParameterLimits:
    epsilon: List[LimitEntry] = field(default_factory=list)

def epsilon_empirical_limits() -> ParameterLimits:
    return ParameterLimits(
        epsilon=[
            LimitEntry(
                source='Boscardin & Cording (1989)',
                limits=[0,0.5e-3, 0.75e-3, 1.5e-3, 3e-3, float('inf')],
                description=['Negligible damage', 'Very slight', 'Slight', 'Moderate to severe', 'Severe to very severe'],
                DL=[0, 1, 2, 3, 4]
            ),
            LimitEntry(
                source='Son and Cording (2005)',
                limits=[0,0.5e-3, 0.75e-3, 1.67e-3, 3.33e-3, float('inf')],
                description=['Negligible damage', 'Very slight', 'Slight', 'Moderate to severe', 'Severe to very severe'],
                DL=[0, 1, 2, 3, 4]
            ),
            LimitEntry(
                source='Burland et al. (1977)',
                limits=[0, 0.5e-3, float('inf')],
                description=['No visible cracks', 'Visible cracks'],
                DL=[0, 1]
            ),
            LimitEntry(
                source='Base et al. (1966) deduced by Burland and Wroth (1974)',
                limits=[0, 0.5e-3, float('inf')],
                description=['No visible cracks', 'Onset of visible cracking'],
                DL=[0, 1]
            ),
            LimitEntry(
                source='Burhouse (1969) deduced by Burland and Wroth (1974)',
                limits=[0,0.38e-3, float('inf')],
                description=['No visible cracks', 'Onset of visible cracking'],
                DL=[0, 1]
            ),
            LimitEntry(
                source='Mainstone (1971) Information taken from Son (2003)',
                limits=[0, 0.3e-3, float('inf')],
                description=['No visible cracking', 'Visible cracking'],
                DL=[0, 1]
            ),
        ]
    )