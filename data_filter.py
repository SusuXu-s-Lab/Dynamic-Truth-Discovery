import pandas as pd
import argparse

def calculate_statistics(file_path):
    # Load the updated data with final_score
    updated_df_with_independence_timeslot = pd.read_csv(file_path)

    # Calculate the mean and various percentiles of the final_score
    mean_final_score = updated_df_with_independence_timeslot['final_score'].mean()
    quantile_75_final_score = updated_df_with_independence_timeslot['final_score'].quantile(0.75)
    quantile_85_final_score = updated_df_with_independence_timeslot['final_score'].quantile(0.85)
    quantile_90_final_score = updated_df_with_independence_timeslot['final_score'].quantile(0.90)
    quantile_95_final_score = updated_df_with_independence_timeslot['final_score'].quantile(0.95)
    quantile_99_final_score = updated_df_with_independence_timeslot['final_score'].quantile(0.985)

    print("Mean final Score:", mean_final_score)
    print("75th Percentile final Score:", quantile_75_final_score)
    print("85th Percentile final Score:", quantile_85_final_score)
    print("90th Percentile final Score:", quantile_90_final_score)
    print("95th Percentile final Score:", quantile_95_final_score)
    print("99th Percentile final Score:", quantile_99_final_score)

    return {
        'mean': mean_final_score,
        '75th': quantile_75_final_score,
        '85th': quantile_85_final_score,
        '90th': quantile_90_final_score,
        '95th': quantile_95_final_score,
        '99th': quantile_99_final_score
    }

def filter_data(file_path, output_file_path, score_threshold, death_threshold=1000000):
    # Load the updated dataset with the final score
    data = pd.read_csv(file_path)

    # Filter the data to keep only rows where the final score is greater than the specified threshold and deaths do not exceed the threshold
    filtered_data = data[(data['final_score'] > score_threshold) & (data['deaths'] <= death_threshold)]

    # Save the filtered dataset to a new CSV file
    filtered_data.to_csv(output_file_path, index=False)
    print(f"Filtered data saved to {output_file_path}")

def main():
    parser = argparse.ArgumentParser(description='Calculate statistics and filter Twitter data based on final scores.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output CSV file for filtered data')
    args = parser.parse_args()

    # Calculate statistics and print them
    stats = calculate_statistics(args.input)

    # Ask the user to input the desired score threshold for filtering
    percentile_input = input("Enter the desired percentile for filtering (e.g., '75th', '85th', '90th', '95th', '99th'): ")

    # Validate the input percentile and get the corresponding score threshold
    if percentile_input in stats:
        score_threshold = stats[percentile_input]
    else:
        print("Invalid percentile. Please enter one of the calculated percentiles.")
        return

    # Filter data based on the specified threshold and save to output file
    filter_data(args.input, args.output, score_threshold)

if __name__ == "__main__":
    main()
