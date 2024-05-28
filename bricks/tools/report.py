# ---------------------------------------------------------------------------- #
#                             Process and report df                            #
# ---------------------------------------------------------------------------- #
ijsselsteinseweg.dataframes['sri']

df = ijsselsteinseweg.dataframes['gf_params']
# Drop columns
df = df.drop(['x_gauss', 'length','height','limit_line'], axis=1)
df['ax'] = df['ax'].apply(lambda x: [min(x), max(x)])
df

df2 = ijsselsteinseweg.dataframes['LTSM-GF']
df2.drop(['e_bh', 'e_bs','e_sh','e_ss','e_h','lh_s','lh_h','dl_s','dl_h'], axis=1)

ijsselsteinseweg.dataframes['LTSM-MS']

rr = ijsselsteinseweg.dataframes['LTSM-MS']
rr.drop(['e_bh', 'e_bs','e_sh','e_ss','e_h','lh_s','lh_h','dl_s','dl_h'], axis=1)