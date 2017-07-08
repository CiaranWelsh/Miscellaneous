import argparse
import os

import matplotlib.pyplot as plt
import pandas
import pysces
import shutil
#===================================================================================
#cmd line interface
parser = argparse.ArgumentParser(description='''IQM prep''')
parser.add_argument('Parent_project_file',help='Absolute path parent IQM project')
parser.add_argument('-i',help='Initialize IQM project and write parameter bounds template file',action='store_true')
parser.add_argument('-w',help='write IQM projects',action='store_true')
args = parser.parse_args()
#===================================================================================


'''
The current script contains two classes. One for initializing the project structure
and writing a parameter bound template file and another for writing the projects
with model specific information about parameter boundaries for optimization. 

The first time you run this script, use the -i flag to initialize the project. 
You'll then have to modify the parameter bounds template file so that each parameter 
is either 'Fixed' as in not estimated, 'Estimated' within a defined interval between  
lower and upper bounds and 'Independent' Pay attention to spelling and capital letters. 
Independent variabels are variabels that need to be set as local in IQM as they are estimated for
each model seperately. These include knockout variables, sucha s PR1 in the example.  

When the parameter bound file is complete, save and close it then run this script again 
but with the -w flag. This will write a separate IQMproject for each model, but with 
the same data

This program depends on the Python package Pysces to read SBML files

'''


class Prep_IQM_parameter_bounds(object):
    def __init__(self,project_dir):
        self.parent_project_dir=project_dir #path to parent project dir
        self.parent_models_path=self._get_parent_models_path() #path to parent models dir
        self.parent_experiments_path=self._get_parent_experiments_path()     #path to parent experiemnts dir
        self.all_parent_models_dirs=self._get_all_models_dir() #lists full path to all models in parent project
        self.all_parent_experiments=self._get_all_experiments()#lists full path of experiment directories in parent project

        self.pysces_model_info_list=self._sbml_list_2pysces()

    def _get_parent_models_path(self):
        '''
        i.e.D:\MPhil\Model_Building\Models\TGFB\Vilar2006\SBML_sh_ver\demonstration\Demo_project5\models

        '''
        for i in os.listdir(self.parent_project_dir):
            if i.lower()=='models':
                models_path=os.path.join(self.parent_project_dir,i)
        return models_path
        
    def _get_parent_experiments_path(self):
        '''
        i.e.D:\MPhil\Model_Building\Models\TGFB\Vilar2006\SBML_sh_ver\demonstration\Demo_project5\experiments

        '''
        for i in os.listdir(self.parent_project_dir):
            if i.lower()=='experiments':
                experiments_path=os.path.join(self.parent_project_dir,i)
        return experiments_path

    def _get_all_models_dir(self):
        '''
        gets a list of all models in parent directory. 
        Removes any model with _model_map in the name. 
        
        i.e.'D:\\MPhil\\Model_Building\\Models\\TGFB\\Vilar2006\\SBML_sh_ver\\demonstration\\Demo_project5\\models\\demonstration_9']

        '''
        os.chdir(self.parent_models_path)
        all_models_dir=[]
        for i in os.listdir(self.parent_models_path):
            if i[-4:]=='.xml':
                if '_model_map' not in i:
                    all_models_dir.append(os.path.join(self.parent_models_path,i[:-4]))
        return all_models_dir
        
    def _get_all_experiments(self):
        '''
        gets a list of all models in parent directory. 
        Removes any model with _model_map in the name. 
        '''
        os.chdir(self.parent_experiments_path)
        exp_dirs=[]
        for i in os.listdir(self.parent_experiments_path):
            if os.path.isdir(i):
                exp_dirs.append(os.path.join(self.parent_experiments_path,i))
        return exp_dirs
        
        
    def sbml2pysces(self,model_xml):
        '''
        Use pysces to read the SBML file
        '''
        current_dir=os.getcwd()
        pysces_filename=os.path.join(current_dir,model_xml[-4]+'.psc')
        pysces.interface.convertSBML2PSC(model_xml,pscfile=pysces_filename)
        return pysces.model(pysces_filename)
        
    def _sbml_list_2pysces(self):
        '''
        converts all xml models in parent project to pysces model. 
        returns a list of tupples:  
        [(model_name, pysces model handle,species,parameters)]
        '''
        psc_models_list=[]
        for i in self.all_parent_models_dirs:
            [path,fle]=os.path.split(i)
            psc_model=self.sbml2pysces(i+'.xml')
            parameters=psc_model.showPar()
            species=psc_model.showSpecies()
            psc_models_list.append((fle,psc_model,species,parameters))
        return psc_models_list
        
    def get_model_parameters(self,model_xml):
        model=self.sbml2pysces(model_xml)
        return model.showPar()
        
    def get_model_species(self,model_xml):
        model=self.sbml2pysces(model_xml)
        return model.showSpecies() 
        
        
    def write_parameter_bounds_template(self):
        '''
        Writes a template csv file for telling the program which 
        parameters to estimate and the upper and lower bounds. 
        
        You must edit this file manually to reflect which parameters 
        you want to estimate. 
        
        You should also double check all the species are there and are correct 
        as sometimes I've witnessed some errors (an IC in the kinetic 
        parmaeters for example)
        
        Also - rename the empty parameters column to 'parameters'.
        
        And a variable can have one of three estimation settings: Estimated, 
        fixed or independent. Independant variables are for those which are experiment. 
        '''    
        parameters=[]
        species=[]
        parameters_dct={}
        species_dct={}
        for i in range(len(self.pysces_model_info_list)):
#            os.chdir(self.child_project_dirs[i])
            parameters.append(self.pysces_model_info_list[i][3])
            species.append(self.pysces_model_info_list[i][2])
        
        for i in species:
            species_dct.update(i)
        for i in parameters:
            parameters_dct.update(i)
        parameters_df=pandas.DataFrame.from_dict(parameters_dct,orient='index')    
#            print parameters_df
        parameters_df['Lower_bound']=1e-6
        parameters_df['Upper_bound']=1e4
        parameters_df['Estimation_setting']='Estimated' 
        parameters_df['Variable_type']='Kinetic_parameter'
        parameters_df.rename(columns={0:'Initial_value'},inplace=True)
        parameters_df.index.name='Parameters'
#            #Do same with Species ICs
        species_df=pandas.DataFrame.from_dict(species_dct,orient='index')
        species_df['Lower_bound']=1
        species_df['Upper_bound']=1e4
        species_df['Estimation_setting']='Estimated'
        species_df['Variable_type']='Species_IC'
        species_df.rename(columns={0:'Initial_value'},inplace=True)
        species_df.index.name='Parameters'
        data_df= pandas.concat([parameters_df,species_df])
        if not os.path.isfile(os.path.join(self.parent_project_dir,'parameter_bounds.csv')):
            data_df.to_csv(os.path.join(self.parent_project_dir,'parameter_bounds.csv'))
        return data_df  

    def parameter_bounds_file_exists(self):
        pattern=re.compile('parameter_bounds.csv')
        for i in os.listdir(self.parent_project_dir):
            print i
            if re.findall(pattern,i):
                return True

    
class Prep_IQM_write_projects(Prep_IQM_parameter_bounds):
    def __init__(self,project_dir):
        super(Prep_IQM_write_projects,self).__init__(project_dir)
        self.parent_project_dir=project_dir #path to parent project dir
#        self.data_dct=self._read_experimental_data()
        self.child_project_dirs=self._create_subprojects_dirs() #directory to all child projects        
        
        self.child_experiments_dir=self._create_experiments_dir() # lists full path to all experiments in all child project
        self._copy_experimental_files()
        self.child_models_dir=self._list_child_models_dirs() # list of child models abs path
        self._write_parameter_bounds_file()
#        self._write_parameter_bounds_template()
#        if self.parameter_bounds_file_exists():
#            self._write_parameter_bounds_file()
         #create subdirectories 'models' and experiemtns and then move the correct model into the right folder. 
    
    def read_parameter_bounds_template(self):
        os.chdir(self.parent_project_dir)
        param_bounds=pandas.read_csv(os.path.join(os.getcwd(),'parameter_bounds.csv'))
        #filter out all fixed parameters
#        filtered_df= param_bounds[(param_bounds.Estimation_setting=='Estimated') | (param_bounds.Estimation_setting=='Independent')]
        return param_bounds
    
    
    def filter_parameter_bounds_file(self,model_xml):
        '''
        takes a model and filteres a parameter bounds file based on the species 
        and ICs in that model. 
        '''
        species=self.get_model_species(model_xml) #get the species dct from this mode
        parameters=self.get_model_parameters(model_xml)#get parameter dct from this 
        param_info=self.read_parameter_bounds_template()
        estimated_species=[]
        estimated_params=[]
        for i in species.keys():
            print '\n'
            for j in param_info[param_info.columns[0]]:
#                print i,j
                if i==j:
                    estimated_species.append(i)
        for i in parameters.keys():
            print '\n'
            for j in param_info[param_info.columns[0]]:
#                print i,j
                if i==j:
                    estimated_params.append(i)
        param_list= estimated_params+estimated_species
        #now filtered_param_info contains only those parameters from model i and 
        #estimated in the parameter boudns file
        filtered_param_info= param_info[param_info['Parameters'].isin(param_list)] 
        return filtered_param_info#.drop(['Estimation_setting'],1)
    
    
    def filter_parameter_bounds_file_all(self):
#        return self.filter_parameter_bounds_file(self.all_parent_models_dirs[0]+'.xml')
        for i in self.all_parent_models_dirs:
            print self.filter_parameter_bounds_file(i+'.xml')
            
    
    def _create_subprojects_dirs(self):
        '''
        create the nested IQM project structure: one project for each model.returns list of subdirectories. one for each projects
        
        '''
        [path,fle]=os.path.split(self.parent_project_dir) #split the parent project dir
        os.chdir(path) #change to parent project dir
        IQM_project_dir=os.path.join(path,fle+'_IQM_project') #create sub project dir
        if not os.path.isdir(IQM_project_dir):
            os.mkdir(IQM_project_dir)
        os.chdir(IQM_project_dir)            
#        #create sub project directories 
        subproject_dirs=[]
        for i in self.all_parent_models_dirs:
            #split dir nito path and file
            [path,fle]=os.path.split(i)
            #create new path
            sub_project_dir=os.path.join(IQM_project_dir,fle)
            subproject_dirs.append(sub_project_dir)
            if not os.path.isdir(sub_project_dir):
                os.makedirs(sub_project_dir)
            os.chdir(sub_project_dir)   
            models_dir=os.path.join(sub_project_dir,'models')
            exp_dir=os.path.join(sub_project_dir,'experiments')
            if not os.path.isdir(models_dir):
                os.mkdir(models_dir)
            if not os.path.isdir(exp_dir):
                os.mkdir(exp_dir)
            shutil.copy(i+'.xml',models_dir)
        return subproject_dirs
        
        
        
    def _create_experiments_dir(self):
        '''
        create the correct folders for experiments in the child project directories        
        '''
#        print self.child_project_dirs
        dire_lst=[]
        for i in self.all_parent_experiments:
            [path,fle]=os.path.split(i)
            for j in self.child_project_dirs:
                os.chdir(j)
                for k in os.listdir(j):
                    if k.lower()=='experiments':
                        dire=os.path.join(os.getcwd(),k) #all child experiment folders 
                        os.chdir(dire)
                        dire_lst.append(os.path.join(dire,fle))
                        if not os.path.isdir(os.path.join(dire,fle)):
                            os.mkdir(os.path.join(dire,fle))
        return dire_lst

    
    def _read_experimental_data(self):
        '''
        Reads data stored in parent experiments directory and returns a nested dictionary
        of the form: dct[experiemnt][model]=data. 
        
        experiment=experient file name. Must be csv. Do not have more than one 
        csv file in a directory
        model=model file name. can be any number of models with any of the species
        that are defined in the data
        data= the data from each experiment split up for each model so that 
        the file only contains the species that are contained in that speific model
        '''
        expt_dct={}
        for i in self.all_parent_experiments:
            os.chdir(i)
            exp_files= os.listdir(os.getcwd())
            for j in exp_files:
                if j[-4:]=='.csv':
                    [exp_path,exp_fle]=os.path.split(j)
                    expt_dct[exp_fle]={}
#                    print expt_dct.keys()
                    data_dfs=pandas.read_csv(os.path.join(i,j))
                    for k in self.all_models_dirs:
                        [mod_path,mod_fle]=os.path.split(k)
                        species_dct= self.get_model_species(k+'.xml')
                        species_dct['time']=0
                        expt_dct[exp_fle][mod_fle]= data_dfs[species_dct.keys()]
        return expt_dct
        
        
    def _copy_experimental_files(self):
        for i in self.child_experiments_dir:
            [ipath,ifle]=os.path.split(i)
            for j in self.all_parent_experiments:
                for k in os.listdir(j):
                    [path,fle]=os.path.split(j)
                    if ifle == fle:
                        shutil.copy(os.path.join(j,k),os.path.join(i,k))


    def _write_parameter_bounds_file(self):
        '''
        writes filtered parameter bounds file to xlsx for reading by matlab
        returns a dict of df's containing appropiate parameters bounds for each model
        '''
        df_dct={}
        for i in  self.child_models_dir:
            os.chdir(os.path.dirname(i))
            [path,fle]=os.path.split(i)
            df=self.filter_parameter_bounds_file(i)
            df_dct[fle[:-4]]=df
            df.to_excel(os.path.join(os.path.dirname(os.path.dirname(i)),fle[:-4]+'_parameter_bounds.xlsx'))
        return df_dct
        
    def parameter_bounds_file_exists(self):
        pattern=re.compile('parameter_bounds.csv')
        for i in os.listdir(self.project_dir):
            print i
            if re.findall(pattern,i):
                return True
                
    def _list_child_models_dirs(self):
        child_models_dir=[]
        for i in self.child_project_dirs:
            os.chdir(i)
            for j in os.listdir(i):
                if j.lower()=='models':
                    for k in os.listdir(os.path.join(i,j)):
                        if k[-4:]=='.xml':
                            child_models_dir.append(os.path.join(i,j,k))
        return child_models_dir                
                
                
                
                

#=================================================================================


'''
The below code uses the above classes and makes the script available for use 
in the command line. 
'''




if args.i:
    IQM_pb=Prep_IQM_parameter_bounds(args.Parent_project_file)
    IQM_pb.write_parameter_bounds_template()
print 'Now go to your parent project directory and make the appropiate changes to the parameter_bounds.csv file.'

if args.w:
    IQM=Prep_IQM_write_projects(args.Parent_project_file)
    
