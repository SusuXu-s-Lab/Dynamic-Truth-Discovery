# Dynamic-Truth-Discovery

## Usage
### Simple Version
After using `csvstack` to aggregate all results into one file, take this file name as the input file name, and run the following commands:

```bash
chmod +x run_all.sh
./run_all_steps.sh
```

After the execution finishes, run the following command to produce the plot:

```bash
python plot_pager.py
```

Follow the instructions to input the key values and the plot will be produced.

### Detailed Version

After using `csvstack` to aggregate all results into one file, proceed with the following steps:

#### Score Calculation
The `score_calculation.py` script calculates the aggregated scores (confidence score, independence score, and user score) for social media posts. This program calculates the scores for each data point without physical constraints and filter schemes.

To run this code:
```bash
python score_calculation.py --input input_file_name.csv --output output_file_name.csv
```

#### Data Filter
The `data_filter.py` script filters out the data points with high scores (high probability of being true). This program first calculates the quantiles of the final score and then filters the data based on the chosen quantile. The available quantiles are 50%, 75%, 85%, 90%, and 99%, with the 99% quantile performing better empirically.

*Note: Smaller quantiles may filter out data points ahead of the ground truth timeline but also come with more noise.*

To run this code:
```bash
# the input file is the output file from the score calculation
python data_filter.py --input input_file_name.csv --output output_file_name.csv
```

#### True Claim Select
The `bayesian_select.py` script implements bayesian updating from the PAGER system to predict the confidence interval of deaths in each time points. Thereby select trustworkthy death values to plot the **near-real-time staircase plot** from the crwodsourcing data.

To run this code:
```bash
# the input file is the output file from the data filter
python apply_constraint.py --input input_file_name.csv --output output_file_name.csv
```

#### Visualization with PAGER
The `plot_pager.py` script produces the PAGER system update comparison with the Bayesian updating from the filtered data. This code requires several major inputs, including the country name, the fatality numbers at certain time points, Smax value, and the CSV file from previous steps. This code can be directly run, and you should follow the instructions to input the values.

**Note: This code needs to be used after PAGER is successfully installed. Additionally, the XML files for the fatality estimation and economic loss estimation need to be up to date.**

To run this code:
```bash
python plot_pager.py
```


