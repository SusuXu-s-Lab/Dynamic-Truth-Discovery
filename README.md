# Dynamic-Truth-Discovery
This repo is the Dynamic Truth Discovery method implement and visualization project. This project mainly serve to the Project [Hierarchical Earthquake Casualty Information Retrieval](https://github.com/SusuXu-s-Lab/Hierarchical-Earthquake-Casualty-Information-Retrieval/) and is detailed illustrated in the paper [Near-real-time Earthquake-induced Fatality Estimation using Crowdsourced Data and Large-Language Models](https://arxiv.org/abs/2312.03755). For more detailed information on this dynamic truth discovery algorithm only, please refer to our [technical report](path/to/your/file.pdf)

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
The `data_filter.py` script filters out the data points with high scores (high probability of being true). This program first calculates the quantiles of the final score and then filters the data based on the chosen quantile. The available quantiles are 50%, 75%, 85%, 90%, and 99%, with the 99% quantile performing the best empirically.

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
python bayesian_select.py --input_file input.csv --output_file output.csv --plot_file output.png --sigma_prior PAGER_Combined_G_value
```

#### Visualization with PAGER
The `plot_pager.py` script produces the PAGER system update comparison with the Bayesian updating from the filtered data. This code requires several major inputs, including the country name, the fatality numbers at certain time points, Smax value, and the CSV file from previous steps. This code can be directly run, and you should follow the instructions to input the values.

**Note: This code needs to be used after PAGER is successfully installed. Additionally, the XML files for the fatality estimation and economic loss estimation need to be up to date.**

To run this code:
```bash
python plot_pager.py
```

## Citation
We kindly request that you cite our paper if you find our code beneficial. Your acknowledgment is greatly appreciated.
```
@article{wang2023near,
  title={Near-real-time earthquake-induced fatality estimation using crowdsourced data and large-language models},
  author={Wang, Chenguang and Engler, Davis and Li, Xuechun and Hou, James and Wald, David J and Jaiswal, Kishor and Xu, Susu},
  journal={arXiv preprint arXiv:2312.03755},
  year={2023}
}
```


## Contact
Please feel free to email sxu83[AT]jh[DOT]edu or chenguang[DOT]wang[AT]stonybrook[DOT]edu for any questions or feedback



