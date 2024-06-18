# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:17:24 2024

@author: anem
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_all_lu(list_lu_values, path_results=None):
    categories = ["crop", "past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
    
    ranges = [[0, 1.5*10**7],
              [0, 1.6*10**7],
              [0, 3.2*10**6],
              [0, 2.5*10**6],
              [0, 1.1*10**7],
              [0, 6.5*10**6],
              [0, 1.6*10**7]   
        ]
    
    medianprops = dict(linewidth=3, color='r')#, markeredgecolor='red')
    
    for c, values in enumerate(list_lu_values[:7]):
        lu_values = values.copy()
        fig, ax = plt.subplots(figsize =(9, 4))
        lu_values.reset_index(inplace=True)
        lu_values.set_index('year', inplace=True)
        lu_values.drop("index", axis=1, inplace=True)
        year = list(set(lu_values.index[:]))
        
        for count, column in enumerate(lu_values.columns[:]):
            
            lu_values.rename({column: f'{count}'})
            #plt.plot(year, lu_values.iloc[:, count])
        

        for i, y in enumerate(year) :
            if i!=0:
                series = lu_values.iloc[i]
                ax.boxplot(series, positions=[y],
                           showfliers=False,
                           #showmeans=True,
                           medianprops=medianprops)
                #ax.scatter([y]*len(series), series)

        if c==0:
            ax.scatter([1975, 2000, 2013], [3260000, 3290000, 4110000], 
                       color="b", label="cropland values from litterature")
        ax.set_ylim(ranges[c])
        
        #changing ticks
        ticks = ax.get_xticks()
        new_ticks = np.delete(ticks, np.where(ticks%2 == 1))
        ax.set_xticks(new_ticks)
        
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{categories[c]} (ha)')

        fig.set_dpi(600)
        plt.xticks(rotation=30)
        if path_results!=None:
            save_path = path_results + categories[c] + "no_scatter.svg"
            fig.savefig(save_path, bbox_inches='tight', format='svg')
        #♥ax.set_xlim([year[0], year[-1]])
        plt.show()
