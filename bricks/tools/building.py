
height = 5
nwalls = len(walls)

fig = go.Figure()

for i in range(len(walls)):
    i +=1
    z = np.empty((2,len(walls)))
    if i == nwalls:
        wall1 = walls[f'wall{i}']
        wall2 = walls[f'wall1']
    else:
        wall1 = walls[f'wall{i}']
        wall2 = walls[f'wall{i}']

    x = np.concatenate([walls[f'wall{i}']['x'], walls[f'wall{i}']['x'][::-1]])    
    x = np.vstack([x,x])
    y = np.concatenate([walls[f'wall{i}']['y'], walls[f'wall{i}']['y'][::-1]])
    y = np.vstack([y,y])
    z[0,:] = np.full((1,len(walls)), fill_value= 0)
    z[1,:] = np.full((1,len(walls)), fill_value=height)
    fig.add_trace(go.Surface(x=x,
                             y=y,
                             z=z,
                             colorscale=[[0, 'rgba(0,0,255,0.5)'], [1, 'rgba(0,0,255,0.5)']],
                             showscale=False))

x_bounds = []
y_bounds = []
for i in range(len(walls)):
    i +=1
    z = np.empty((2,len(walls)))
    if i == nwalls:
        wall1 = walls[f'wall{i}']
        wall2 = walls[f'wall1']
    else:
        wall1 = walls[f'wall{i}']
        wall2 = walls[f'wall{i}']

x_bounds = np.array([(wall['x'].min(), wall['x'].max()) for wall in walls.values()]).flatten()
y_bounds = np.array([(wall['y'].min(), wall['y'].max()) for wall in walls.values()]).flatten()
z0 = np.zeros(x_bounds.shape)
z1 = np.full(x_bounds.shape, height)
for z in [z0,z1]:
    fig.add_trace(go.Surface(x=x_bounds,
                             y=y_bounds,
                             z=z,
                             colorscale=[[0, 'rgba(0,0,255,0.5)'], [1, 'rgba(0,0,255,0.5)']], 
                             showscale=False))


fig.update_layout(
    scene=dict(
        xaxis=dict(title='X [m]', color='black'),
        yaxis=dict(title='Y [m]', color='black'),
        zaxis=dict(title='Z [m]', color='black'),
        aspectmode="auto",
    ),
    title='Building Walls with Shaded Sides',
    template='plotly_white',
    margin=dict(t=100, b=30),
    height=600,
    width=800,
)


fig.show()
