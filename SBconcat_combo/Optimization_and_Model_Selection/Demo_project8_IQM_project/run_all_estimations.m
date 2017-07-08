function [result, model_selection_criteria]=run_all_estimations(project_dirs,number_obs) %full path to folder containing your projects
%{
This script takes the output folder from the python program 'prep_IQM.py'
as input then passes each project to the run1estimation.m script for
optimization. You must copy and paste the two scripts 'run1estimation.m' and
'run_all_estimations.m' into the folder containing all subprojects. 

This script also takes the number of total observations 
in your experimental data as input, but in future versions this 
will automatically be inferred. 

Output from this script includes a results scructure which contains
seperate IQM structures for each optimized project and a table that is
written to file for the model selection results. 


%}
%%
%number_obs = number of observations beting fit. 248 for vilar example
% project_dirs='D:\MPhil\Model_Building\Models\TGFB\Vilar2006\SBML_sh_ver\demonstration\Demo_project8_IQM_project'

% %list all files and fodlers in project_dirs
all_project_dirs=dir(project_dirs);

% % extract only the folders (removing the '.' and '..' which are always
% the first two
list_of_dirs = {all_project_dirs([all_project_dirs.isdir]).name};
list_of_dirs = list_of_dirs(3:end);

%iterate over the list of subdirectories (the child folders which are
%now prepared for estimation)
%%
model_names={}
for i=1:length(list_of_dirs),
% % print which project is currently being estimated
    strcat('Estimating project:    ',list_of_dirs(i))
% % name the fields for the results structure
%     field_name=strcat('Model',num2str(i));
    field_name=char(list_of_dirs(i))
    model_names{i+1}=field_name
% % run estimations using the run1estimation script and compile results into another structure 
    result.(field_name).estimation_result=struct(run1estimation(char(strcat(project_dirs,'\',list_of_dirs(i)))));
    % % get number of parameters estiamted in model i from parameter bounds
    xlsx_dir=dir('*parameter_bounds.xlsx');
    parameter_bounds=readtable(xlsx_dir.name)
    fixed_index=find(strcmp(parameter_bounds.Estimation_setting,'Fixed'))
    %transpose to get horizontal vector
    fixed_index=transpose(fixed_index)
    parameter_bounds([fixed_index],:)=[]
    kinetic_parameter_index = find(strcmp(parameter_bounds.Variable_type, 'Kinetic_parameter'))
    IC_index=find(strcmp(parameter_bounds.Variable_type, 'Species_IC'))
    independent_index=find(strcmp(parameter_bounds.Estimation_setting, 'Independent'))
    kinetic_parameter_index=kinetic_parameter_index(kinetic_parameter_index~=independent_index)
    params_estimated=length(kinetic_parameter_index)+length(IC_index)+length(independent_index)
    cd('..')
    result.(field_name).number_est_params=params_estimated % for independent 
   
end
%%

% 
model_names=fieldnames(result)
chisq=[];
num_est_params=[];
for i=1:length(model_names)
    kinetic_params=result.(model_names{i}).estimation_result.parameters;
    ICs=result.(model_names{i}).estimation_result.icnames;
    chisq=[chisq;result.(model_names{i}).estimation_result.FVALopt]
    num_est_params=[num_est_params;length(kinetic_params)+length(ICs)];
end
% 
% 

[~,~,chisq_rank]=unique(chisq);
model_selection_criteria=table(chisq,'RowNames',model_names)
model_selection_criteria.chisq_rank=chisq_rank
model_selection_criteria.Number_est_params=num_est_params

one=[];
two=[];
three=[];
aicRSS_vec=[];
for i=1:length(model_selection_criteria.chisq)
    %calculate each term of AIC separately to check the calculation
%     chisq.chisq(i)
    model_selection_criteria.chisq(i);
    model_selection_criteria.Number_est_params(i);
    d=model_selection_criteria.chisq(i)/number_obs;
    ln=log(d);
    first_term=number_obs*ln;
    one=[one; first_term];
    second_term=2*model_selection_criteria.Number_est_params(i);
    two=[two; second_term];
    numerator=2*model_selection_criteria.Number_est_params(i)*(model_selection_criteria.Number_est_params(i)+1);
    denominator=number_obs-model_selection_criteria.Number_est_params(i)-1;
    ratio=numerator/denominator;
    three=[three; ratio];
    aicRSS=first_term+second_term+ratio;
    aicRSS_vec=[aicRSS_vec;aicRSS]
%     
%     aicRSS_2nd_order_lst=[aicRSS_2nd_order_lst aicRSS_second_order];
end

% chisq.first_term=one;
% chisq.second_term=two;
% chisq.third_term=three;
model_selection_criteria.aicRSS=aicRSS_vec
[~,~,aic_rank]=unique(aicRSS_vec)
model_selection_criteria.aic_rank=aic_rank
model_selection_criteria

%    Calculating Akaike weights
delta_i=[];
exp_wi=[];
%delta_i is the relative liklihood value
%exp_wi = e^(-0.5*delta_i)

for i=model_selection_criteria.aicRSS
    delta_i=[delta_i ;i-min(model_selection_criteria.aicRSS)];
%     delta_i=[delta_i ;i-min(model_selection_criteria.aicRSS)]
end
relative_likelihoods=[];
for i=1:length(delta_i);
    relative_likelihoods=[relative_likelihoods;exp(-0.5*delta_i(i))];
end

weights=[]
tot_relative_likelihoods=sum(relative_likelihoods)
for i=relative_likelihoods
    weights=[weights;i/tot_relative_likelihoods]
end


model_selection_criteria.delta_i=delta_i
model_selection_criteria.relative_likelihood=relative_likelihoods

model_selection_criteria.weights=weights

writetable(model_selection_criteria,strcat(project_dirs,'\Model_Selection_Table.csv'),'WriteRowNames',1)

end







