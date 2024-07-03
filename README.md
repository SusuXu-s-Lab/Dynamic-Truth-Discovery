# Dynamic-Truth-Discovery

## Usage
### Score Calulation
The ```score_calculation.py``` is the fprogram to calculate the aggregated score (confidence score, independence score ,and user score) for social media posts. This program only calculated the score for each data points, without physical constraints and filter scheme.

To run this code:
```bash
python score_calculation.py --input input_file_name.csv --output output_file_name.csv
```

### Data filter
The ```data_filter.py``` is the program to filter out the data points with high score (high probability to be true).  This program is firstly to calcualte the quantiles of the final score and then filter the data based on the chosen quatile. The quatiles contains (50%, 75%, 85%, 90%, and 99% quantile). The 99% quantile performs better from the emperical practice. *Note:Smaller quantile may filter out the data points aheand of the ground truth time line, but it also come with more noise.*

To run this code:
```bash
# the input file is the output file from the score calculation
python data_filter.py --input input_file_name.csv --output output_file_name.csv
```
