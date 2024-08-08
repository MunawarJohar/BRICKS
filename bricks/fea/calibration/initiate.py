import torch
from sklearn.preprocessing import MinMaxScaler, StandardScaler


model_path = r'C:\Users\javie\Desktop\EMM\ML\2DW2O - EMS.dpf'
tb_path = r'C:\Users\javie\Desktop\EMM\ML\2DW2O_-_EMS_NLA.tb'

scalers = [StandardScaler(), StandardScaler(), StandardScaler()]
tl_bounds = (0.1, 1.0)  # Initiation
fe_bounds = (0.01, 0.1)
bounds = np.array([tl_bounds, fe_bounds])
loss_target = 3.33

WALL2 = WALL(model_path, tb_path, scalers, loss_target, bounds)
WALL2.fit_targets()

if method == 'OPT':
    best_params, best_loss = pure_minimization(WALL1, bounds)

if method == 'BOPT':
    n_samples = 10
    x_values = WALL2.generate_initial_samples(n_samples=n_samples)

    y_list = []  # Get first set of losses
    x_unscale = WALL2.perform_scaling('targets', 'descale', x_values)
    for x in x_unscale:
        scaled_losses = WALL2.loss_function(x)

    X_init_single = torch.tensor(x_values)
    Y_init_single = torch.tensor(np.array(scaled_losses)).reshape(-1, 1)

    # ----------------------------- Bayesian Optimization ---------------------------- #
    objective_function = WALL2.loss_function
    n_iter = 250
    batch_size = 10  # Batch size cannot be smaller than n_samples
    Nrestarts = 10  # Nrestarts cannot be smaller than n_samples

    X_init_single, Y_init_single = SingleBOPT(Y_init_single, X_init_single, n_iter, batch_size, bounds, Nrestarts, objective_function, WALL2)
