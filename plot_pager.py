from collections import OrderedDict
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import pandas as pd
import os.path
from pprint import PrettyPrinter
from losspager.models.emploss import EmpiricalLoss
from losspager.utils.country import Country

# Define BayesianLossEstimator class
class BayesianLossEstimator:
    def __init__(self, initial_loss_mean, initial_loss_variance, measurement_noise_variance, b0, b1, residual_std):
        self.current_loss_mean = initial_loss_mean
        self.current_loss_variance = initial_loss_variance
        self.measurement_noise_variance = measurement_noise_variance
        self.b0 = b0
        self.b1 = b1
        self.residual_std = residual_std
        self.total_loss_estimates = []
        self.loss_variances = []

    def calculate_projection_rate(self, Smax):
        log_a = self.b1 * Smax + self.b0
        return np.exp(log_a)

    def update_with_observation(self, observed_loss, observation_time, Smax):
        a = self.calculate_projection_rate(Smax)

        # Update projection rate distribution
        projection_rate_samples = np.random.normal(a, self.residual_std, 1000)

        # Avoid numerical issues with log(0) by clipping values
        loss_projection_model = lambda t, a: self.current_loss_mean * np.exp(a * t)

        projected_losses = np.array([loss_projection_model(observation_time, a) for a in projection_rate_samples])

        # Use log-transformation to stabilize likelihood calculations
        log_likelihoods = stats.norm.logpdf(np.log(observed_loss), np.log(np.maximum(1e-10, projected_losses)), np.sqrt(self.measurement_noise_variance))
        max_log_likelihood = np.max(log_likelihoods)
        likelihoods = np.exp(log_likelihoods - max_log_likelihood)

        likelihoods_sum = np.sum(likelihoods)

        if likelihoods_sum == 0 or np.isnan(likelihoods_sum):
            print(f"Warning: Sum of likelihoods is zero or NaN at time {observation_time} with observed loss {observed_loss}")
            return

        posterior_weights = likelihoods / likelihoods_sum
        updated_loss_mean = np.sum(posterior_weights * projected_losses)
        updated_loss_variance = np.sum(posterior_weights * (projected_losses - updated_loss_mean)**2)

        # Update current loss estimate ensuring it doesn't decrease
        self.current_loss_mean = max(self.current_loss_mean, updated_loss_mean)
        self.current_loss_variance = updated_loss_variance
        self.total_loss_estimates.append(self.current_loss_mean)
        self.loss_variances.append(self.current_loss_variance)
        print(f"Time: {observation_time}, Observed Loss: {observed_loss}, Projected Loss Mean: {updated_loss_mean}, Updated Loss Mean: {self.current_loss_mean}")

    def get_current_loss_estimate(self):
        return self.current_loss_mean, self.current_loss_variance

# Function to get ISO2 code from country name
def get_iso2_code(country, country_name):
    country_info = country.getCountry(country_name)
    return country_info['ISO2']

# Function to input fatalities for a specific time point
def input_fatalities(empfat, country_name1, iso2_country1, country_name2, iso2_country2, time_point):
    print(f"--- Input data for time point {time_point} hours ---")
    fatalities1 = int(input(f"Enter the number of fatalities for {country_name1}: "))
    fatalities2 = 0
    if country_name2 != "NONE":
        fatalities2 = int(input(f"Enter the number of fatalities for {country_name2}: "))

    # Define loss dictionary using ISO2 codes
    lossdict = {
        iso2_country1: fatalities1,
        'TotalFatalities': fatalities1 + fatalities2
    }
    if iso2_country2:
        lossdict[iso2_country2] = fatalities2

    # Calculate combined G value
    G = empfat.getCombinedG(lossdict)
    print(f'Combined G value for {time_point} hours = %.2f' % G)

    # Calculate probabilities
    probs = empfat.getProbabilities(lossdict, G)
    return OrderedDict(probs), G

def main():
    # Initialize PrettyPrinter
    pp = PrettyPrinter(indent=4)

    # Load country data
    country = Country()

    # User input for country names
    country_name1 = input("Enter the name of the first country: ")
    country_name2 = input("Enter the name of the second country (or 'NONE' if not applicable): ")

    # Get ISO2 codes
    iso2_country1 = get_iso2_code(country, country_name1)
    iso2_country2 = get_iso2_code(country, country_name2) if country_name2 != "NONE" else None

    # Define file paths of the fatality data
    fatfile = os.path.join(os.getcwd(), '.', 'losspager', 'data', 'fatality.xml')
    ecofile = os.path.join(os.getcwd(), '.', 'losspager', 'data', 'economy.xml')

    # Load empirical loss data
    empfat = EmpiricalLoss.fromXML(fatfile)
    empeco = EmpiricalLoss.fromXML(ecofile)

    # Dictionary to store data for each time point
    data = {}
    combined_G = 0

    # Input data for each time point, limited to 5
    for i in range(5):
        time_point = int(input(f"Enter time point {i+1} (in hours): "))
        if time_point in data:
            print(f"Time point {time_point} already entered. Please enter a different time point.")
            continue

        probs, G = input_fatalities(empfat, country_name1, iso2_country1, country_name2, iso2_country2, time_point)
        data[time_point] = probs
        combined_G = G  # Update combined G with the last calculated value

        if len(data) >= 5:
            break

    # Print final data
    pp.pprint(data)

    # Print country information for verification
    print(f"Country 1 ({country_name1}) info: ")
    pp.pprint(country.getCountry(country_name1))
    if country_name2 != "NONE":
        print(f"Country 2 ({country_name2}) info: ")
        pp.pprint(country.getCountry(country_name2))

    # Ask for CSV file name
    file_path = input("Enter the name of the CSV file (eg: input_file.csv) containing observation data: ")

    # Ask for Smax value with default
    Smax_input = input("Enter the value of Smax (default is 10): ")
    Smax = float(Smax_input) if Smax_input else 10.0

    # Initialize BayesianLossEstimator
    initial_loss_mean = 5  # Initial estimated loss from PAGER
    initial_loss_variance = combined_G  # Variance of initial loss estimate equals to combined G value
    measurement_noise_variance = 0.57  # Variance of measurement noise
    b0 = 5.545  # Intercept from the paper
    b1 = -0.634  # Slope from the paper
    residual_std = 0.414  # Residual standard deviation from the regression model

    loss_estimator = BayesianLossEstimator(initial_loss_mean, initial_loss_variance, measurement_noise_variance, b0, b1, residual_std)

    # Load the data from the provided CSV file
    data_csv = pd.read_csv(file_path)

    # Extract observation times and observed losses
    observation_times = data_csv['time_gap'].values
    observed_losses = data_csv['deaths'].values

    # Perform Bayesian updates with the observed data
    for t, loss in zip(observation_times, observed_losses):
        loss_estimator.update_with_observation(loss, t, Smax)
        current_loss_estimate, current_loss_variance = loss_estimator.get_current_loss_estimate()
        print(f"Time: {t}, Updated Loss Estimate: {current_loss_estimate:.2f}, Variance: {current_loss_variance:.2f}")

    # Prepare data for plotting
    fig, ax = plt.subplots(figsize=(14, 8))

    # Set bar width to a reasonable value
    bar_width = 1000

    # Replace data_bars with data from the previous code
    data_bars = data

    # Color mapping based on the uploaded image
    color_mapping = {
        '0-1': 'green',
        '1-10': 'yellowgreen',
        '10-100': 'yellow',
        '100-1000': 'orange',
        '1000-10000': 'red',
        '10000-100000': 'darkred',
        '100000-10000000': 'grey'
    }

    # Create a proxy artist for the legend
    proxy = plt.Line2D([0], [0], linestyle="none", c='gray', marker='s')

    for t, data_t in data_bars.items():
        labels = list(data_t.keys())
        values = list(data_t.values())
        y_positions = []
        for label in labels:
            lower, upper = label.split('-')
            y_positions.append((int(lower), int(upper)))
        for i in range(len(values)):
            lower, upper = y_positions[i]
            color = color_mapping[labels[i]]
            ax.barh((lower + upper) / 2, values[i] * 20, height=upper - lower, color=color, align='center', alpha=0.8, left=t, linewidth=bar_width)

    ax.set_yscale('log')
    ax.set_ylim(1, 1000000)
    ax.set_yticks([1, 10, 100, 1000, 10000, 100000, 1000000])
    ax.set_yticklabels(['$10^0$', '$10^1$', '$10^2$', '$10^3$', '$10^4$', '$10^5$', '> $10^5$'])
    ax.set_title('Earthquake Fatality Estimation from Crowdsourced Data based on LLMs')
    ax.set_xlabel('Time')
    ax.set_ylabel('Death Count Range (log scale)')

    # Set left boundary lines for each time point and add text for time points
    for t in data_bars.keys():
        ax.axvline(x=t, color='black', linestyle='--')
        ax.text(t, 0.5, f'{t}', color='red', verticalalignment='top', horizontalalignment='center', fontsize=10)

    # Convert loss means and observed losses to log scale for alignment
    log_loss_means = np.log10(loss_estimator.total_loss_estimates)
    log_observed_losses = np.log10(observed_losses)

    # Plot the total loss estimates over time as a staircase plot with log scale
    ax.step(observation_times, 10**log_loss_means, where='post', label='Estimated Fatalities (Log)', color='black', linewidth=3, linestyle='-')
    ax.step(observation_times, 10**log_observed_losses, where='post', label='Observed Fatalities (Log)', color='black', linewidth=3, linestyle=':')

    # Add the legend with the histogram label
    ax.legend([proxy, plt.Line2D([0], [0], color='black', linewidth=3, linestyle='-'), plt.Line2D([0], [0], color='black', linewidth=3, linestyle=':')],
              ['PAGER Histogram', 'Estimated Fatalities (Log)', 'Observed Fatalities (Log)'], loc='upper left')

    # Ask for PNG file name
    png_file_name = input("Enter the name of the PNG file (eg: output_file.png) to save the plot: ")
    plt.savefig(png_file_name)
    #plt.show()

if __name__ == "__main__":
    main()
