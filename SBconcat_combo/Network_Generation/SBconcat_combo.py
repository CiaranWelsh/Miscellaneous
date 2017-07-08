import re
import os
import argparse
import itertools 
import string
import glob






'''
This script is intended to produce combinations of SBML files given a skeleton model and list of hypotheses.

You may need to install the python modules argparse and glob. Easiest way of 
doing this is to use PIP or easy_install. 

This script uses Prof. Darren Wilkinsons SBML shorthand representation of ODE models. 
The script 'mod2sbml.py' converts SBML shorthand to SBML while 'sbml2mod.py' 
converts the reverse process. For your convenience these are both included with SBconcat_combo 
in the same directory as your SBML shorthand model files. 

SBML versions which can be used are on this page: https://www.staff.ncl.ac.uk/d.j.wilkinson/software/sbml-sh/all.html  

When writing the SBML shorthand its tempting to copy and paste all parameter and
initial concentrations into all model hypotheses. Do not do this as the AIC criteria depends on the number of parameters, which will be the same for all models if you copy and paste!

This program uses pythons 'set' function to remove duplicated reactions. This means that if you 
intend to have a duplicate reaction then you need to describe this mathematically, not biochemically. 
For example, consider the reaction ' A -> Sink ' which is degraded at two rates, k1 and k2. In Copasi it is possible to have two reactions each with a different rate constant. When using SBconcat_combo.py, the duplicates will be removed. To circumvent this problem, add the rates together before being used in the rate law. i.e. volume * (k1+K2) * A,  since (k1+K2) * A = k1A+k2A. 

Always use fixed variables such as 'Synth' and 'Sink' for production and degradation reactions

Finally, when you run the program it automatically produces a 'model_map' which maps model number
to hypotheses included in that particular model. However, because this model map cannot be processed 
with 'mod2sbml.py' it returns an error. This is a small bug that I haven't had
time to fix, but all models should be converted to sbml. 

Any problems or bugs please email c.welsh2@newcastle.ac.uk
'''


#------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='''
SBML party
''')
parser.add_argument('skeleton_file',help='Absolute path of the SBML shorthand backbone network of your model')
parser.add_argument('output_directory',help='Name the output directory')
parser.add_argument('model_name',help='Name your models. Combinations enurmerate this name ')
parser.add_argument('SBML_version',help="Which version of sbml do you want. Default=2.4.1. Google 'SBML shorthand' for the other versions")
parser.add_argument('hypotheses',nargs='*',help="List of absolute paths for SBML shorthand text files (Can be any number of files)")
args = parser.parse_args()
#-----------------------------------------------------------------------------------------------

'''
The class SBconcat contains the tools for the job and the code below the class
actually uses the class whilst parsing variables from the command line
'''
class SBconcat():
    def __init__(self):
        pass
    
    def parse_SBshorthand(self,SBshorthand_file):
        '''
        Parses whole text file into python as one chunk of text. 
        '''
        with open(SBshorthand_file) as f:
            return f.read()
            
    def name_model(self,model_name,SBML_version='3.1.1.1'):
        '''
        When you find time extract the model names of each of the combinations and concatonate 
        them to sign post which model is which
        '''
        return '@model:{}={} \"{}\"'.format(SBML_version,model_name,model_name)

    def split_sections(self,SBshorthand_file):
        '''
        Takes a SBshorthand file and returns a dictionary of each of the sections. 
        Keys of the dictionary are the dividers.
        Values of dictionary are the content between dividers. 
        '''
        SBfile=self.parse_SBshorthand(SBshorthand_file)
        sections={}
        sections= dict(re.findall(r"(?:^|(?<=\n))(@\w+)([\s\S]*?)(?=\n[@][^@]\w+|$)",SBfile))
        return sections
        
    def concatonate_SBsection(self,SBfile1,SBfile2,divider):
        '''
        Takes two SB shorthand formatted text files 
        Returns concatonated string of reactions from both files
        '''
        SB1_dct=self.split_sections(SBfile1)
        SB2_dct=self.split_sections(SBfile2)
        SB1_component= SB1_dct[divider]
        SB2_component= SB2_dct[divider]
        SB1_component_list = SB1_component.split('\n')
        SB2_component_list = SB2_component.split('\n')
        section = list(set(SB1_component_list+SB2_component_list))
        for i in range(len(section)):
            if section[i] == '':
                loc=i
        section.pop(loc)
        return section
    
    def concatonate_SBreactions(self,SBfile1,SBfile2):
        '''
        takes output from concatonate_SBreactions as input
        returns a dictionary of reactions. The reaction definition line are keys
        and reaction and rate law line are values. This code also removes duplicates
        provided they are exact duplicates (including spaces)  
        '''
        SB1_dct=self.split_sections(SBfile1)
        SB2_dct=self.split_sections(SBfile2)
        SB1_component= SB1_dct['@reactions']
        SB2_component= SB2_dct['@reactions']
        SB1_component_list = SB1_component.split('\n')
        SB2_component_list = SB2_component.split('\n')
        reactions_str =SB1_component+SB2_component
        pattern=re.compile('(@r.*\n)(.*\n.*)')
        matches=re.findall(pattern,reactions_str)
        reactions=[]
        for i in matches:
            reactions.append(i[1])
        reactions=list(set(reactions))
        new_reactions=[]
        for i in range(len(reactions)):
            ln='@r=v{} "v{}"\n'.format(str(i+1),str(i+1))
            new_reactions.append([ln,reactions[i]])
        return new_reactions


    def concat_SB2(self,file1,file2,out,model_name,SBML_ver,write_file=False):
        '''
        concatonate 2 sbml shorthand models
        This function uses the previous functions to concate two sbml shorthand files 
        'file1' and 'file2' and return it in python if 'write_file=False' default and to 'out.txt' 
        if 'write_file=True'
        
        This function is the class form of the script 'SBconcat.py' which can be used from the 
        command line
        '''
#        dire=os.path.dirname(file1)
#        os.chdir(dire)
        #List SBML shorthand dividers
        dividers=["@model", "@units", "@compartments", "@species", "@parameters", "@rules", "@reactions", "@events"]
        
        #list files
        files=[file1,file2]
        
        #Check which sections are in these files
        sections=[]
        for i in files:
            SBfile=self.parse_SBshorthand(i)
            for j in  dividers:
                pattern=re.compile(j)
                if re.findall(pattern,SBfile) == []:
                    continue
        #            print 'Section {} is not being used in {}'.format(j,i)
                else:
                    sections.append(j)
                    
        #ensure each section only appears once
        sections=list(set(sections))
        
        #initialize model with a name. Defult SBML version is 2.4.0. Can set this
        #to any of the other versions using the keywork SBML_version=<version>
        model= self.name_model(model_name,SBML_ver)
        
        #add the compartments tag
        model=model+'\n'+'@compartments'
        
        #Use concatonate_SBsection to collate the compartments section from the two models, 
        #whilst remembering to remove any duplicates
        compartments= self.concatonate_SBsection(file1,file2,'@compartments')
        for j in compartments:
            model=model+'\n'+j
        
        #add the species tag
        #Use concatonate_SBsection to collate the species section from the two models, 
        #whilst remembering to remove any duplicates
        model=model+'\n'+'@species'
        species= self.concatonate_SBsection(file1,file2,'@species')
        for j in species:
            model=model+'\n'+j
            
        #add the species tag
        #Use concatonate_SBsection to collate the species section from the two models, 
        #whilst remembering to remove any duplicates    
        model=model+'\n'+'@parameters'
        parameters= self.concatonate_SBsection(file1,file2,'@parameters')
        for j in parameters:
            model=model+'\n'+j
            
            
        #add the species tag
        #Use concatonate_SBsection to collate the species section from the two models, 
        #whilst remembering to remove any duplicates.
            #There mightnot be any rules in the models
        if '@rules' in sections:
            model=model+'\n'+'@rules'
            rules= self.concatonate_SBsection(file1,file2,'@rules')
            for j in rules:
                model=model+'\n'+j
        model=model+'\n'+'@reactions'
        
        #get the reactions. The format is a nested list
        reactions= self.concatonate_SBreactions(file1,file2) 
        
        '''
        SBML shorthand reactions are of the form:
            @r=v1 "v1"
            C -> C+D
            Cell * v2_k * C
        
        The regex used to identify these components recognize the top line as one group
        and the middle and bottom as a second group. These correspond to top and bottom
        respectively below. 
        '''
        top=[]
        bottom=[]
        
        for i in reactions:
            top.append(i[0].strip('\n'))
            bottom.append(i[1])
            
        for i in range(len(top)):
            model=model+'\n'+top[i]+'\n'+bottom[i]
        
        
        #add the species tag
        #Use concatonate_SBsection to collate the species section from the two models, 
        #whilst remembering to remove any duplicates
        #There might not be any events in the models
        if '@events' in sections:
            events= self.concatonate_SBsection(file1,file2,'@events')
            model=model+'\n'+sections[i]
            for j in events:
                model=model+'\n'+j
        
        if write_file==True:
            with open(out,'w') as f:
                f.write(model)
        return model
        
        
        
    def SBconcat_combos(self,files,outfile,model_name,SBML_ver):
        '''
        Takes a list of SBML shorthand files and name of an output file as input
        returns a concatonate SBML shorthand string. Also writes this model to outfile. 
        '''
        first = self.concat_SB2(files[0],files[1],outfile,model_name,SBML_ver,write_file=True)
        assert len(files)!=1 # need more than one file to concatonate
        if len(files)==2:
            return first
        else:
            for i in files:
                model = self.concat_SB2(outfile,i,outfile,model_name,SBML_ver,write_file=True)
        return model
        
        '''
        The above code is equivalent to the below code for a skeleton
        model and 4 hypotheses
        '''
    #    print '\n'+SBc.concat_SB2(out,files[2],out,write_file=True)
    #    print '\n'+SBc.concat_SB2(out,files[3],out,write_file=True)
    #    print '\n'+SBc.concat_SB2(out,files[4],out,write_file=True)
    #    for i in range(len(files[1:])):
    #        return SBc.concat_SB2(out,files[i],out,write_file=True)
        return model        
        
        
        
    def get_file_combinations(self,files):
        '''
        gets a list of tuples of all possible combinations
        of files that are more than 1 file name in length and
        include the first file (file[0])
        '''
        all_combinations=[]
        for i in xrange(1,len(files)+1):
            all_combinations.append(list(itertools.combinations(files,i)))
        relevant_combinations=[]
        for i in all_combinations:
            for j in i:
                if len(j)!=1 and files[0] in j:
                    relevant_combinations.append(j)
        print 'Number of combinations: {}'.format(len(relevant_combinations))
        return relevant_combinations        
        
        
    def combo_text2sbml(self,all_files,outfile,model_name,SBML_ver):
        '''
        all_files  = list of files to concatonate. First file in the list is
        the skeleton file, common to all models. 
        outfile=Name output. Doesn't need '.txtFiles are numbered 'outfile_x' where x=model index. 
        Also produces a 'model map' to help identifywhich file is which. 
        Puts everything into a directory called outfile
        '''
        #create some letters to keep track of files
        letters= string.uppercase[:len(all_files)]
        labeled_files=[]
        for i in range(len(all_files)):
            labeled_files.append([letters[i],all_files[i]])
            
        #get relevant file combinations. Do the same with  letters to keep track
        combinations_letters= self.get_file_combinations(letters)
        combinations_files= self.get_file_combinations(all_files)
        
        with open(outfile+'_model_map'+'.txt','w') as f:
            for i in range(len(combinations_letters)):
                f.write(str([i,combinations_letters[i]]))
        file_names=[]
        for i in range(len(combinations_files)):
            name=outfile+'_'+str(i)+'.txt'
            self.SBconcat_combos(combinations_files[i],name,model_name+'_'+str(i),SBML_ver) #concatonate lists of sbml models
            file_names.append([i,os.path.join(os.getcwd(),name)])#append file names
        return os.getcwd()    
        
    def convert_to_sbml(self,dire):
        os.chdir(dire)
        for i in glob.glob("*.txt"):
            try:
                sbml_sh=os.path.join(dire,i)
                os.system('python -m mod2sbml {} > {}.xml '.format(sbml_sh,sbml_sh[:-4]))        
            except:
                continue  

#=============================================================================

'''
This part of the program uses the SBconcat() to concatonate models
'''
            
SBc=SBconcat()


if len(args.hypotheses)==1:
    all_files=[args.skeleton_file]+[args.hypotheses]
else:
    all_files=[args.skeleton_file]+args.hypotheses


#Change to same directory as skeleton file
current_dir=os.path.dirname(all_files[0])
os.chdir(current_dir)
print os.getcwd()

#create a new directory 
new_dir=os.path.join(current_dir,args.output_directory)    
#create a new directory if it doesn't already exist
if os.path.isdir(new_dir) == False:
    os.mkdir(new_dir)

#change to new directory
os.chdir(new_dir)
#use combo_text2sbml to combine all sbml shorthand files
models_dir=SBc.combo_text2sbml(all_files,args.output_directory,args.model_name,args.SBML_version)
#Use mod2sbml.py to convert sb shorthand to sbml
SBc.convert_to_sbml(models_dir)







