function output=run1estimation(project_dir)
%{
This script takes an IQM project and a parameter_bounds file and uses the 
optimization facilities within IQMTools to parameterize a single model. The
script first uses a global optimization algorithm (default is
simulated anealing, but this can easily be changed by commenting out the
appropiate bits of code) and then reoptimizes using a local algorithm to
hone in on the global minimum. 

This script is heavily based on the script that can be automatically generated
from the IQMparamestGUI. 

Thus far it is only tested on the one project and so probably need further
work to make it generalizable to all models with all kinds of data
(multiple independent variables for example, which would need to be 
local variables within IQM). 

%}


%%read project and parameter bounds  file
cd(project_dir);

% %read project
project=IQMprojectSB(project_dir);
project_opt=project;

% %find a file in project dir that has parameter_bounds.xlsx in the name
xlsx_dir=dir('*parameter_bounds.xlsx')

% %read the template file
parameter_bounds=readtable(xlsx_dir.name)



%copy so you don't loose original
parameter_bounds2=parameter_bounds



%% filter table to get correct format for IQM
% %First get all estimated parameters (IC's plus params) and those which are
% %experiment dependent 
fixed_index=find(strcmp(parameter_bounds2.Estimation_setting,'Fixed'))
%% 
%transpose to get horizontal vector
fixed_index=transpose(fixed_index)
parameter_bounds2([fixed_index],:)=[]
% % now get index of kinetic,  IC parmatres and independent
kinetic_parameter_index = find(strcmp(parameter_bounds2.Variable_type, 'Kinetic_parameter'))
IC_index=find(strcmp(parameter_bounds2.Variable_type, 'Species_IC'))
%% 
independent_index=find(strcmp(parameter_bounds2.Estimation_setting, 'Independent'))
%%
% % remove the independent index from kinetic parmater index
kinetic_parameter_index=kinetic_parameter_index(kinetic_parameter_index~=independent_index)

params_estimated=length(kinetic_parameter_index)+length(IC_index)+length(independent_index)


%%
% %get tables for initial guesses for use later
% params_initial_guess=table(parameter_bounds.Parameters(kinetic_parameter_index),parameter_bounds.Initial_guess(kinetic_parameter_index));
% IC_initial_guess=table(parameter_bounds.Parameters(IC_index),parameter_bounds.Initial_guess(IC_index));

% %create another table containing the parameter name and lower and upper
% %bounds for the estimation, then convert to cell array for IQM
param_table=table(parameter_bounds2.Parameters(kinetic_parameter_index),parameter_bounds2.Lower_bound(kinetic_parameter_index),parameter_bounds2.Upper_bound(kinetic_parameter_index))

param_cell=table2cell(param_table)

% %do the same for ICs
IC_table=table(parameter_bounds2.Parameters(IC_index),parameter_bounds2.Lower_bound(IC_index),parameter_bounds2.Upper_bound(IC_index));
IC_cell=table2cell(IC_table)

% %Get any independent variables 
independent_table=table(parameter_bounds2.Parameters(independent_index),parameter_bounds2.Lower_bound(independent_index),parameter_bounds2.Upper_bound(independent_index))
independent_cell=table2cell(independent_table)


%%compare measurements with experimental prior to optimization (uncomment)
% % IQMcomparemeasurements(project_opt)

%% select parameters/states to estimate and their bounds
% % input parameters to estimate and bounds
paramdata=param_cell
% % Local params to estimate. These are needed for independent variables such as K/O data
paramdatalocal = independent_cell
% % input ICs to estimate and bounds. 
icdata=IC_cell


%% DEFINE THE ESTIMATION INFORMATION (STRUCTURE)
estimation = [];

% Model and experiment settings
estimation.modelindex = 1;
estimation.experiments.indices = [1];
estimation.experiments.weight = [1];

% Optimization settings
estimation.optimization.method = 'simannealingIQM';                        
% Starting temperature:                            
OPTIONS.tempstart = 5000;                          
% Ending temperature before assuming T=0:          
OPTIONS.tempend = 0.1;                             
% Reduction factor for temperature:                
OPTIONS.tempfactor = 0.2;                          
% Number of iterations if T~=0:                    
OPTIONS.maxitertemp = 1000;                        
% Number of iterations if T==0:                    
OPTIONS.maxitertemp0 = 1000;                       
% Maximum time in minutes:                         
OPTIONS.maxtime = 500;         

% estimation.optimization.method='pswarmIQM';
% OPTIONS.maxiter=50000;
% OPTIONS.maxfunevals=100000
% OPTIONS.popsize=500;
% OPTIONS.logFlag=1;
% OPTIONS.CPTolerance=1e-16

% % Optimizer: isresIQM                                                  
% % Stochastic Ranking for Constrained Evolutionary Minimization (global)
% estimation.optimization.method='isresIQM';                                                 
% % Maximum number of generations:                                       
% OPTIONS.maxgen = 10000;                                                 
% % Maximum time in minutes:                                             
% OPTIONS.maxtime = 500;                                                 
                                                                       
                     
% Integrator settings
estimation.integrator.options.abstol = 1e-006;
estimation.integrator.options.reltol = 1e-006;
estimation.integrator.options.minstep = 0;
estimation.integrator.options.maxstep = Inf;
estimation.integrator.options.maxnumsteps = 1000;

% Flags
estimation.displayFlag = 2; % show iterations and final message
estimation.scalingFlag = 2; % scale by mean values
estimation.timescalingFlag = 0; % do not apply time-scaling
estimation.initialconditionsFlag = 1; % do use initial conditions from measurement data (if available)

% Always needed (do not change ... unless you know what you do)
estimation.parameters = paramdata;
estimation.parameterslocal = paramdatalocal;
estimation.initialconditions = icdata;

%% run estimation
output = IQMparameterestimation(project_opt,estimation);
% 
% %% now run again using a local optimizer
% Optimizer: simplexIQM                       
% Nelder-Mead nonlinear simplex (local)       
estimation.optimization.method = 'simplexIQM';                                 
% Maximum number of function evaluations:     
OPTIONS.maxfunevals = 5000000;                  
% Maximum number of iterations:               
OPTIONS.maxiter = 2000000;                      
% Termination tolerance on the function value:
OPTIONS.tolfun = 1e-25;                       
OPTIONS.maxtime=30

output = IQMparameterestimation(output.projectopt,estimation);
%%
% IQMcomparemeasurements(output.projectopt)
%{
The true parameters for the model are:
ka=1;
ki=0.333333
kr=0.0333333
PR1=8
PR2=4
alpha=1
KCD=0.0277778
KLID=0.25

%}


end









