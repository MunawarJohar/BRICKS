def compute_damage_parameter(df, damage: dict = None) -> float:
    """
    Compute the damage parameter based on the given dataframe and damage dictionary.

    Parameters:
    - df: The dataframe containing the data.
    - damage: A dictionary containing the damage information.

    Returns:
    - The computed damage parameter.

    """
    n_c = 0
    c_w_n = []
    c_w_d = []
    el_size = damage['element_size']

    for elements in damage['EOI']:
        n_c += 1
        n_steps = len(df['Step nr.'].unique())
        n_el = find_nel(df, elements)
        l_c = el_size * n_el
        c_w_df = find_mean_cw(elements, df)
        c_w = c_w_df['Ecw1']
        c_w_n += [c_w**2 * l_c]
        c_w_d += [c_w * l_c]
        break
    c_w = sum(c_w_n) / sum(c_w_d) if len(c_w_d) != 0 else 0
    c_w_df['Ecw1'] = c_w

    psi = 2 * n_c**0.15 * c_w**0.3
    c_w_df['psi'] = psi
    c_w_df = c_w_df.fillna(0)
    c_w_df.drop(columns=['Ecw1'], inplace=True)
    return c_w_df

def eval_dl(psi):
    
    psi_thresholds = [1,1.5,2.5,3.5,float('inf')]
    dl = [0,1,2,3,4]
    for i,threshold in enumerate(psi_thresholds):
        if psi > threshold:
            continue
        else:
            break
    return dl[i]

def find_mean_cw(elements_of_interest,df):
    filtered_df = df[df['Element'].isin(elements_of_interest)]
    grouped = filtered_df.groupby(['Step nr.', 'Element'])['Ecw1'].mean().reset_index()
    final_avg = grouped.groupby('Step nr.')['Ecw1'].mean().reset_index()
    return final_avg

def find_max_cw(elements_of_interest,df):
    filtered_df = df[df['Element'].isin(elements_of_interest)]
    grouped = filtered_df.groupby(['Step nr.', 'Element'])['Ecw1'].max().reset_index()
    final_avg = grouped.groupby('Step nr.')['Ecw1'].max().reset_index()
    return final_avg

def find_nel(df,elements):
    filtered_df = df[df['Element'].isin(elements)]
    n_steps = len(df['Step nr.'].unique()) # Find Nsteps
    n_el = filtered_df.groupby('Step nr.')['Ecw1'].apply(lambda x: x.dropna().count())
    return n_el
