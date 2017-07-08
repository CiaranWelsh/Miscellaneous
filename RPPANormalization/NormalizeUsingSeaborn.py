# -*- coding: utf-8 -*-
import pandas
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import logging



FORMAT='	%(levelname)s:%(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO,stream=logging.StreamHandler)
#LOG=logging.getLogger()
PLOT_RFI_VS_RFI_CV=True
PLOT_NORMED=False

N_BOOT=10000
HK='a-Tubulin'


logging.info('PLOT_RFI_VS_RFI_CV set to: {}'.format(PLOT_RFI_VS_RFI_CV))
logging.info('PLOT_NORMED set to: {}'.format(PLOT_NORMED))



sns.set_style("whitegrid")

pandas.set_option('multi_sparse',True)
f=r"D:\OtherPeople\Neil\2017\06_June\raw_data.xlsx"
logging.info('File being analyzed is: {}'.format(f))



sns.set_context(context='poster',font_scale=2.5)
d=os.path.dirname(f)
bar_charts=os.path.join(os.path.dirname(f),'BarCharts')

if os.path.isdir(bar_charts)!=True:
    os.makedirs(bar_charts)

df=pandas.read_excel(f)
antibody_index=list( df['Analyte'])
antibody_index=[i.replace('/','_') for i in antibody_index]
antibody_index=[i.replace(' ','') for i in antibody_index]
antibody_index=[i.replace('_customer','') for i in antibody_index]
antibody_index=[i.replace('_Customer','') for i in antibody_index]
antibody_index=[i.replace('Customer_','') for i in antibody_index]
antibody_index=[i.replace('customer','') for i in antibody_index]

df['Analyte']=antibody_index
df.set_index(['Analyte', 'Replicate','Time'],inplace=True,drop=False)
df=pandas.DataFrame(df[['RFI','RFI CV','Analyte','Replicate','Time']])
antibodies=sorted(list(set(df.index.get_level_values(0))))
if HK not in antibodies:
    raise TypeError('{} is not in your antibody list'.format(HK))
time=sorted(list(set(df.index.get_level_values(2))))

#print df 
'''
first normalize data to housekeeping
'''
if PLOT_RFI_VS_RFI_CV:
    AP_plot_dirs=os.path.join(bar_charts,'PLOT_RFI_VS_RFI_CV')
    if os.path.isdir(AP_plot_dirs)!=True:
        os.mkdir(AP_plot_dirs)
    logging.info('Plotting graphs to visualize AP treatment')
    for i in antibodies:
        plt.figure()
        data=df.loc[i]
        x_tick = [data['Replicate'], data['Time']]
        N=data['Time'].shape[0]
        width=0.35
        ind=np.arange(N)
        fig,ax=plt.subplots()
        rects=ax.bar(ind,data['RFI'],width,yerr=data['RFI CV'])
        plt.title('{}\n(Error=RFI CV)'.format(i))
        plt.xlabel('Sample Number')
        plt.ylabel('RawData(AU)')
        fname=os.path.join(AP_plot_dirs,i+'.jpeg')
        plt.savefig(fname,dpi=300,bbox_inches='tight')
    logging.info('Graphs saved to:\n{}'.format(AP_plot_dirs))


if PLOT_NORMED:
    logging.info('Data assigned to Group AP have been removed')
    df.drop('AP',level=1,inplace=True)
    sns.set_context(context='poster',font_scale=2.3)
    hk= df.loc[HK]
    plot_dire=os.path.join(bar_charts,'{}Normalization'.format(HK))
    if os.path.isdir(plot_dire)!=True:
        os.mkdir(plot_dire)
        
    df_dct={}
    for i in antibodies:
        hk_norm= df.loc[i]['RFI']/hk['RFI']
        hk_norm= pandas.DataFrame(hk_norm)
        hk_norm.columns=['Signal Normed to {}'.format(HK)]
        hk_norm= pandas.concat([df.loc[i],hk_norm],axis=1)
        df_dct[i]=hk_norm
    
    for i in df_dct:
        plt.figure()
        sns.barplot(x='Time',y='Signal Normed to {}'.format(HK),data=df_dct[i],n_boot=N_BOOT)
        plt.legend(loc=(1,0.3))
        plt.title('{},n=3\n Errors=mean 95% confidence interval\n determined by {} bootstraps'.format(i,N_BOOT))
        fname=os.path.join(plot_dire,i+'.jpeg')
        plt.savefig(fname,dpi=150,bbox_inches='tight')
    logging.info('Data normalized to {} saved to {}'.format(HK,plot_dire))
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#if PLOT_AP:
#dire=bar_path_ind
#sns.set_context(context='talk',font_scale=2)
#for i in df_dct:
#    for j in df_dct[i].groupby(level=1):
#        if j[0]!=4:
#            plt.figure()
#            time= j[1].loc['Control'].index.get_level_values(1)
#            print time
#            control=j[1].loc['Control']['RFI']
#            treated=j[1].loc['Treated']['RFI']
#            N=len(time)
#            ind=np.arange(N)
#            width=0.35
#            fig, ax = plt.subplots()
#            rects1 = ax.bar(ind, control, width, color='r',label='C')#, yerr=men_std)
#            rects2 = ax.bar(ind+width,treated,width,color='k',label='T')
#            ax.set_xticks(ind + width / 2)
#            ax.set_xticklabels(list(time))
##            plt.plot(time,control,label=str(j[0])+'_C')
##            plt.plot(time,treated,label=str(j[0])+'_T')
#            plt.legend(loc=(1,0.3))
#            plt.title('Antibody: {}, Biological Repeat={},\n'.format(i,j[0]))
#            plt.xlabel('Time(min)')
#            plt.ylabel('Signal/a-Tubulin Signal')
#            fname=os.path.join(line_path_ind,i+'.jpeg')
#            plt.savefig(fname,bbox_inches='tight',dpi=150)
#        plt.plot( j[1].loc['Control']
#for i in df.groupby(level=[2,1]):





