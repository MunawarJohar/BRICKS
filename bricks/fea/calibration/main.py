## Notes

# Because the software interpreter used to run this script does not support dynamic imports, all necessary functions and classes
# from external modules have been defined within this script. This approach ensures that the script can be executed independently,
# without relying on external files or packages that may not be accessible during runtime.

from .wall import *

# ---------------------------------------------------------------------------- #
#                                    SCRIPT                                    #
# ---------------------------------------------------------------------------- #
model_path = r'C:\Users\javie\Desktop\Demo\2DW2O - TS.dpf'
tb_path = r'C:\Users\javie\Desktop\Demo\2DW2O_-_TS_NLA.tb'
scalers = [MinMaxScaler(), MinMaxScaler(), MinMaxScaler()]
target = 3.5, # Psi Wall2 Outer
tl_bounds = (0.25, 0.4) # Initiation
fe_bounds = (0.01, 0.05)
bounds = np.array([tl_bounds, fe_bounds])
loss_target = 3.5

WALL1 = WALL(model_path,
                tb_path,
                scalers,
                loss_target, # Psi Wall2 Outer
                bounds)
WALL1.fit_targets()

n_samples = 1
x_values = WALL1.generate_initial_samples(n_samples=n_samples)

y_list = [] # Get first set of lossess
for x in x_values:
    LOSS = WALL1.loss_function(x)
    y_list.append(LOSS)

X_init_t = torch.tensor(x_values)
Y_init_t = torch.tensor(y_list).reshape(-1, 1)

# ----------------------------- Bayesian Optimization ---------------------------- #
objective_function = WALL1.loss_function
n_iter = 10
batch_size = 15
Nrestats = 10

X_init_single , Y_init_single = SingleBOPT(Y_init_t, X_init_t, n_iter, batch_size, bounds, Nrestats, objective_function)