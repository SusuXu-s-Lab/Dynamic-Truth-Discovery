import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main(input_file, output_file):
    # Load the data
    data = pd.read_csv(input_file)

    # Assuming 'time_gap' is the column to sort by and 'value' is the column to filter
    data_sorted = data.sort_values(by 'time_gap', ascending=True)

    # Filter the data: remove values smaller than the bigger values that occur later
    filtered_data = []
    max_value_so_far = float('-inf')

    for index, row in data_sorted.iterrows():
        if row['deaths'] > max_value_so_far:
            max_value_so_far = row['deaths']
            filtered_data.append(row)

    filtered_data_df = pd.DataFrame(filtered_data)

    # Save the filtered data
    filtered_data_df.to_csv(output_file, index=False)

    # Create the staircase plot
    plt.step(filtered_data_df['time_gap'], filtered_data_df['deaths'], where='post')
    plt.xlabel('Time Gap')
    plt.ylabel('Value')
    plt.title('Snapshot of the physical constraints applied')
    plt.grid(True)
    
    # Save the plot
    plt.savefig("snapshot.png")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and plot data from a CSV file.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output', type=str, required=True, help='Path to save the filtered CSV file.')

    args = parser.parse_args()

    main(args.input, args.output)
