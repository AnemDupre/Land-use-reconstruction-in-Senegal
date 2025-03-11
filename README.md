# Reconstructing land-use evolutions in Senegal

This repository contains an adapted version of the dynamic simulation model of land-use changes in Sudano-sahelian countries of Africa (SALU) developped by Stéphenne and Lambin in 2001. Given the exogenous variables in \data, the proportion of the studied territory attributed to different land-uses is estimated.  The \data file contains the exogenous variables at the scale of Senegal, covering years 1961 to 2020, and of Senegal's Groundnut basin, covering years 1974 to 2017. A pdf description of input data and associated sources is provided in the \data folder

In addition, we provided the code used to analyse the sensitivity of our model to parameter values, using delta indices. Explored parameter ranges can be modified in the fetch.py file of the \code folder for further research. The \results file contains the figures obtained for 10 000 simulations at national and regional scale, as well as the sensitivity analysis heatmap.

Current version is v0.1.0 (doi: 10.5281/zenodo.13833512).
