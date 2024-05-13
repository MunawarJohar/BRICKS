class Node:
    ndof = 0
    nn   = 0
    
    def clear():
        Node.ndof = 0
        Node.nn = 0
        
    def __init__ (self, x, y):  
        self.x     = x
        self.y     = y
        self.p     = np.zeros(3)

        self.dofs  = [Node.ndof, Node.ndof+1, Node.ndof+2]

        Node.ndof += 3
        Node.nn   += 1

    def add_load (self, p):  
        self.p += p

class Element:
    '''
    Class which initialises objects and these objects functionalities. The variables models & loads include the  models and distributed loads the FEM class supports.
    '''
    ne = 0

    def clear():
        Element.ne = 0
        
    def __init__ (self, nodes, model):
        # ------------------------- OBJECT ATRRIBUTES ------------------------ #
        self.model = model
        self.nodes = nodes
        self.load = None 

        # ---------------------------- PROCESSING ---------------------------- #
        self.L = np.sqrt((nodes[1].x - nodes[0].x)**2.0 + (nodes[1].y - nodes[0].y)**2.0)

        dx = nodes[1].x - nodes[0].x
        dy = nodes[1].y - nodes[0].y

        self.cos = dx / self.L
        self.sin = dy / self.L

        R = np.zeros ((6,6))

        R[0,0] = R[1,1] = R[3,3] = R[4,4] = self.cos
        R[0,1] = R[3,4] = -self.sin
        R[1,0] = R[4,3] =  self.sin
        R[2,2] = R[5,5] = 1.0
        
        self.R  = R
        self.Rt = np.transpose(R)
        
        self.q = np.zeros(2)

        Element.ne += 1
        
    def set_section (self, props):
        if 'EA' in props:
            self.EA = props['EA']
        else:
            self.EA = 1.e20
        if 'EI' in props:
            self.EI = props['EI']
        else:
            self.EI = 1.e20
        if 'GA_eff' in props:
            self.GA_eff = props['GA_eff']
        else:
            self.GA_eff = 1.e20

    def _assert_methods(self):
        # ------------------------- COMPATIBLE MODELS ------------------------ #
        models = {'EB','TS'}
        loads = {'constant','sinusoidal'}
        # --------------------- FEM SOLVER VERIFICATIONS --------------------- #
        assert self.model in models, \
        "Model Incompatible with FEM solver"
        assert self.load in loads, \
        "Unsupported distributed load"

    def global_dofs  (self):
        return np.hstack ((self.nodes[0].dofs, self.nodes[1].dofs))
    
    # -------------------- MODEL SELECTION AND IDENTIFIER -------------------- #
    def stiffness_eb(self):
        k = np.zeros ((6, 6))

        EA = self.EA
        EI = self.EI
        L = self.L

        # Extension contribution
        k[0,0] = k[3,3] = EA/L
        k[3,0] = k[0,3] = -EA/L

        # Bending contribution
        k[1,1] = k[4,4] =  12.0 * EI / L / L / L
        k[1,4] = k[4,1] = -12.0 * EI / L / L / L
        k[1,2] = k[2,1] = k[1,5] = k[5,1] = -6.0 * EI / L / L
        k[2,4] = k[4,2] = k[4,5] = k[5,4] = 6.0 * EI / L / L
        k[2,2] = k[5,5] = 4.0 * EI / L
        k[2,5] = k[5,2] = 2.0 * EI / L

        return np.matmul ( np.matmul ( self.Rt, k ), self.R )

    def stiffness_ts(self):
        
        k = np.zeros ((6, 6))

        EA = self.EA
        EI = self.EI
        GA_EFF = self.GA_eff
        L = self.L
        # Calculation for beta coefficient
        beta = (12*EI)/(GA_EFF*L**2)

        # Extension contribution
        k[0,0] = k[3,3] = EA/L
        k[3,0] = k[0,3] = -EA/L

        # Timoshenko contribution

        k[1,1] = k[4,4] =  (12.0 * EI) / ((L**3)*(beta+1))
        k[1,4] = k[4,1] = (-12 * EI) / ((L**3)*(beta+1)) 
        k[1,2] = k[2,1] = k[1,5] = k[5,1] = (-6.0 * EI) / ((L**2)*(beta+1))

        k[2,4] = k[4,2] = k[4,5] = k[5,4] = (6.0 * EI) / (L**2*(beta+1))
        k[2,2] = k[5,5] = (EI*(beta+4)) / (L*(beta+1))
        k[2,5] = k[5,2] = (EI*(-beta+2)) / (L*(beta+1))

        return np.matmul ( np.matmul ( self.Rt, k ), self.R )
    
    def model_selection(self):
        '''
        Class function to run adequate element model. Variable must be called as a string and supports the following models [EB,TS].
        '''
        if self.model == 'EB':
            return self.stiffness_eb() 
        if self.model == 'TS':
            return self.stiffness_ts()
        self._assert_methods()
    # --------------------- ELEMENT LOAD FUNCTIONALITIES --------------------- #
    def add_distributed_load (self, q:float ,load_type:str):

        l = self.L
        self.load = load_type
        self.q = np.array( q )

        if self.load == 'constant':

            el = [ 0.5*q[0]*l,
                   0.5*q[1]*l,
                  -1.0/12.0*q[1]*l*l,
                   0.5*q[0]*l,
                   0.5*q[1]*l,
                    1.0/12.0*q[1]*l*l ]
        
        if self.load == 'sinusoidal':

            el = [0.5*q[0]*l,
                    l * q[1]/ np.pi ,
                    -2 * l ** 2 * q[1]/ np.pi ** 3,
                    0.5*q[0]*l,
                    l * q[1]/ np.pi ,
                    2 * l ** 2 * q[1]/ np.pi ** 3 ]
         
        self._assert_methods() #Assertion verf
        
        eg = np.matmul ( self.Rt, np.array ( el ) )

        self.nodes[0].add_load ( eg[0:3] )
        self.nodes[1].add_load ( eg[3:6] )

    # ------------------------------------------------------------------------ #
    #                       POST PROCESSING AND ANALYSIS                       #
    # ------------------------------------------------------------------------ #
    # ---------------------------- BENDING MOMENTS --------------------------- #
    def bending_moments (self,u_global:float,num_points=2):
    
        l = self.L
        q = self.q[1]
        EI= self.EI
        GA_EFF = self.GA_eff

        beta = (12*EI)/(GA_EFF*l**2)

        xi = np.linspace ( 0.0, l, num_points )
        M  = np.zeros(num_points)

        ul = np.matmul ( self.R, u_global )

        if self.load in ['constant', None]:

            if self.model == 'EB':            
                M = ( -l**5.0*q +
                6.0 * l**4.0*q*xi -
                6.0*q*xi*xi*l**3.0 -
                48.0*(ul[2] + ul[5]/2.0)*EI*l**2.0 +
                72.0*EI*((ul[2]+ul[5])*xi+ul[1]-ul[4])*l -
                144.0*xi*EI*(ul[1]-ul[4]) ) / 12.0 / l**3.0

            if self.model == 'TS':
                M = (-q*(beta+1)*l**5 +
                 6*q*xi*(beta+1)*l**4 -
                 6*q*xi**2*(beta+1)*l**3 -
                 12*((ul[2] - ul[5])*beta +
                 4*ul[2]+2*ul[5])*EI*l**2 +
                 72*((ul[2]+ul[5])*xi+ul[1]-ul[4])*EI*l -
                 144*xi*EI*(ul[1]-ul[4]))/l**3/(beta+1)/12

            if self.model not in {'EB','TS'}:
                raise Exception('Model Incompatible with FEM solver')
        
        if self.load == 'sinusoidal':

            if self.model == 'EB':            
                M = (q*l**5*np.sin(np.pi*xi/l)*np.pi -
                     4*((ul[2]+ul[5]/2)*l**2 +
                     ((-0.3e1/0.2e1*ul[2]-0.3e1/0.2e1*ul[5])*xi -
                      0.3e1/0.2e1*ul[1]+0.3e1/0.2e1*ul[4])*l +3*xi*(ul[1]-ul[4]))*EI*np.pi **3-2*l**5*q)/l**3/np.pi**3
                
            if self.model == 'TS':
                M = (l ** 5 * q * np.pi * (beta + 1) * np.sin(np.pi * xi / l) + (((ul[5] - ul[2]) * beta - 2 * ul[5] - 4 * ul[2]) * l ** 2 + ((6 * ul[5] + 6 * ul[2]) * xi + 6 * ul[1] - 6 * ul[4]) * l - 12 * xi * (ul[1] - ul[4])) * EI * np.pi ** 3 - 2 * l ** 5 * q * (beta + 1)) / l ** 3 / np.pi ** 3 / (beta + 1)

            if self.model not in {'EB','TS'}:
                raise Exception('Model Incompatible with FEM solver')

        return M

class Constrainer:
    def __init__ (self):
        self.cons_dofs = []
        self.cons_vals = []

    def fix_dof (self, node, dof, value=0):
        self.cons_dofs.append(node.dofs[dof])
        self.cons_vals.append(value)
 
    def fix_node (self, node):
        for dof in node.dofs:
            self.fix_dof (node, dof)      

    def full_disp (self,u_free):
        u_full = np.zeros(len(self.free_dofs) + len(self.cons_dofs))
        
        u_full[self.free_dofs] = u_free
        u_full[self.cons_dofs] = self.cons_vals
        
        return u_full
    
    def constrain (self, k, f):
        self.free_dofs = [i for i in range(len(f)) if i not in self.cons_dofs]
        
        Kff = k[np.ix_(self.free_dofs,self.free_dofs)]
        Kfc = k[np.ix_(self.free_dofs,self.cons_dofs)]
        Ff = f[self.free_dofs]

        return Kff, Ff - np.matmul(Kfc,self.cons_vals)
    
    def support_reactions (self,k,u_free,f):       
        Kcf = k[np.ix_(self.cons_dofs,self.free_dofs)]
        Kcc = k[np.ix_(self.cons_dofs,self.cons_dofs)]
        
        return np.matmul(Kcf,u_free) + np.matmul(Kcc,self.cons_vals) - f[self.cons_dofs]