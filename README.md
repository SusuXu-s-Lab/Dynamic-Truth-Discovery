# Dynamic-Truth-Discovery

## Usage
### Simple version
After using ```csvstack``` aggregate all result into one file. 
Take the this file name as the input file name, run the following command:

```bash
chmod +x run_all.sh
./run_all_steps.sh
```
After the excution finished, run the following command :
```bash
python plot_pager.py
```
Please input the key values following the instruction and the plot will be produced



### Detailed Version 

After using ```csvstack```aggregate all result into one file. 

#### Score Calulation
The ```score_calculation.py``` is the fprogram to calculate the aggregated score (confidence score, independence score ,and user score) for social media posts. This program only calculated the score for each data points, without physical constraints and filter scheme.

To run this code:
```bash
python score_calculation.py --input input_file_name.csv --output output_file_name.csv
```

#### Data filter
The ```data_filter.py``` is the program to filter out the data points with high score (high probability to be true).  This program is firstly to calcualte the quantiles of the final score and then filter the data based on the chosen quatile. The quatiles contains (50%, 75%, 85%, 90%, and 99% quantile). The 99% quantile performs better from the emperical practice. 

*Note:Smaller quantile may filter out the data points aheand of the ground truth time line, but it also come with more noise.*

To run this code:
```bash
# the input file is the output file from the score calculation
python data_filter.py --input input_file_name.csv --output output_file_name.csv
```

#### Physical Constraint
The ```apply_constraint.py``` is the program to implement the physical constraints (non-decrease constraints) on the data. This program takes the filtered data from last step as input, and further filter the data to make them follow the non-decrease constraints. This step is important to produce the step plot. 

*Note: the snapshot, i.e. step plot, is produced by this code*

To run this code:
```bash
# the input file is the output file from the data filter
python apply_constraint.py --input input_file_name.csv --output output_file_name.csv
```

#### Visualization with PAGER
The ```plot_pager.py``` is the program to produce the PAGER system updating compare with the bayesian updating from the data filtered out. This code consist of serveral major inputs, inlcuding country name, the fatality numbers on the certain time point, Smax value, and the CSV file from previous steps. This code can be directly runed and follow the instructions to input the values.

**Note: This code need to be used after the PAGER successfully installed. And the XML file for the fatality esitmation and economic loss estimation need to be up to date.**

To run this code:
```bash
python plot_pager.py
```
