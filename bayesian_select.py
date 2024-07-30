import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def apply_staircase_rule(data):
    data_sorted = data.sort_values(by='time_slot')
    max_deaths = -np.inf
    filtered_deaths = []
    for deaths in data_sorted['true_value']:
        if deaths >= max_deaths:
            max_deaths = deaths
            filtered_deaths.append(deaths)
        else:
            filtered_deaths.append(max_deaths)
    data_sorted['true_value'] = filtered_deaths
    return data_sorted

def load_and_process_data(csv_file, sigma_prior):
    # Load data
    data = pd.read_csv(csv_file)

    # Convert time_gap to integer time slots
    data['time_slot'] = data['time_gap'].apply(np.floor).astype(int)

    # Initialize variables
    first_valid_time_slot = None
    mu_prior = None

    # Sort and find the first time slot with data
    time_slots = sorted(data['time_slot'].unique())

    for t in time_slots:
        current_data = data[data['time_slot'] == t]['deaths']
        if not current_data.empty:
            mode_values = current_data.mode()
            if not mode_values.empty:
                mu_prior = mode_values[0]  # Use the first mode if available
            else:
                mu_prior = current_data.mean()  # Use mean if no mode
            first_valid_time_slot = t
            break

    if mu_prior is None:
        raise ValueError("No data available in any time slot.")

    # Placeholder to store true values
    true_values = {'time_slot': [first_valid_time_slot], 'true_value': [int(np.ceil(mu_prior))]}

    # Continue with the Bayesian updating for subsequent time slots
    for t in time_slots:
        if t <= first_valid_time_slot:
            continue  # Skip time slots before the first valid time slot
        current_data = data[data['time_slot'] == t]['deaths']
        
        if not current_data.empty:
            mu_data = current_data.mean()
            sigma_data = current_data.std() if len(current_data) > 1 else sigma_prior
        
            # Bayesian updating
            weight_prior = sigma_data**2 if sigma_data > 0 else sigma_prior**2
            weight_data = sigma_prior**2
            mu_new = (weight_prior * mu_data + weight_data * mu_prior) / (weight_prior + weight_data)
            sigma_new = np.sqrt((weight_prior * weight_data) / (weight_prior + weight_data))
            
            # Determine the mode value for the decision rule
            mode_value = current_data.mode().iloc[0] if not current_data.mode().empty else mu_prior

            # Define the target range for selecting true value based on 10% of the mode value
            target_range = [mu_new - 0.1 * mode_value, mu_new + 0.1 * mode_value]
            valid_values = current_data[(current_data >= target_range[0]) & (current_data <= target_range[1])]
            
            # Select the maximum value within the 10% mode value range
            if not valid_values.empty:
                true_value = valid_values.max()
            else:
                true_value = mu_new  # Use the predicted mean if no values are in the range
            
            # Constraint: If true value is greater than mode + 65% of the mode, use mode value
            if true_value > mode_value + 0.65 * mode_value:
                true_value = mode_value
        else:
            true_value = mu_prior  # Use the last valid mu_prior if current data is empty
        
        # Apply +1 integer policy by rounding up
        true_value = int(np.ceil(true_value))

        # Update prior for next iteration
        mu_prior = mu_new
        sigma_prior = sigma_new
        
        # Store the true value
        true_values['time_slot'].append(t)
        true_values['true_value'].append(true_value)

    # Apply staircase rule to the processed data
    true_values = apply_staircase_rule(pd.DataFrame(true_values))

    return true_values

def save_results(true_values, output_file):
    true_values.to_csv(output_file, index=False)
    print(f"True values saved to {output_file}")

def plot_data(true_values, plot_file):
    plt.figure(figsize=(10, 6))
    plt.step(true_values['time_slot'], true_values['true_value'], where='post', label='True Values Over Time')
    plt.xlabel('Time Slot')
    plt.ylabel('True Value')
    plt.title('True Values vs. Time Slot')
    plt.legend()
    plt.savefig(plot_file)
    print(f"Plot saved to {plot_file}")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Process data from a CSV file, apply staircase rule, save the results, and plot.")
    parser.add_argument('--input_file', type=str, required=True, help='Input CSV file path')
    parser.add_argument('--output_file', type=str, required=True, help='Output CSV file path')
    parser.add_argument('--plot_file', type=str, required=True, help='Output plot file path (PNG format)')
    parser.add_argument('--sigma_prior', type=float, required=True, help='Prior sigma value, the combined G value from the PAGER system')
    
    args = parser.parse_args()

    # Process the data
    true_values = load_and_process_data(args.input_file, args.sigma_prior)
    
    # Save the results
    save_results(true_values, args.output_file)
    
    # Plot the data
    plot_data(true_values, args.plot_file)

if __name__ == "__main__":
    main()
