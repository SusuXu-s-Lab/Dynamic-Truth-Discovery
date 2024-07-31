import pandas as pd
import ast
import re
import argparse

def load_and_preprocess_csv(file_path, start_time):
    df = pd.read_csv(file_path)
    df = df[['created_at', 'text', 'lang', 'deaths', 'death_score', 'public_metrics_like_count',
             'author_public_metrics_followers_count', 'author_public_metrics_following_count', 'author_verified']]
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['time_gap'] = (df['created_at'] - start_time).dt.total_seconds() / 3600
    df = df.sort_values(by='time_gap')
    df['time_gap'] = df['time_gap'].map(lambda x: f"{x:.5f}")
    df = df[['time_gap', 'text', 'lang', 'deaths', 'death_score', 'public_metrics_like_count',
             'author_public_metrics_followers_count', 'author_public_metrics_following_count', 'author_verified']]
    return df

def calculate_mean_of_highest_confidences(data):
    highest_confidences = []
    for key in data:
        confidences = data[key].values()
        highest_confidence = max(confidences)
        highest_confidences.append(highest_confidence)
    mean_confidence = sum(highest_confidences) / len(highest_confidences) if highest_confidences else 0
    return mean_confidence

def process_row(row):
    data = ast.literal_eval(row['death_score'])
    return calculate_mean_of_highest_confidences(data)

def remove_url(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def normalize_counts(group):
    group['clean_text'] = group['text'].apply(remove_url)
    duplicate_counts = group['clean_text'].value_counts()
    group['duplicate_count'] = group['clean_text'].apply(lambda x: duplicate_counts[x])
    max_count = group['duplicate_count'].max()
    group['inverted_count'] = max_count - group['duplicate_count'] + 1
    min_inverted = group['inverted_count'].min()
    max_inverted = group['inverted_count'].max()
    group['normalized_count'] = 0.99 * (group['inverted_count'] - min_inverted) / (max_inverted - min_inverted) + 0.01
    return group

def append_normalized_duplicate_counts(df, text_column='text', time_gap_column='time_gap'):
    df[time_gap_column] = pd.to_numeric(df[time_gap_column])  # Ensure time_gap is numeric
    df['time_slot'] = df[time_gap_column].astype(int)
    df = df.groupby('time_slot').apply(normalize_counts)
    df.rename(columns={'normalized_count': 'independence_score'}, inplace=True)
    df.drop(columns=['clean_text', 'duplicate_count', 'inverted_count', 'time_slot'], inplace=True)
    return df

def calculate_user_scores(df):
    df['adjusted_followers_count'] = df['author_public_metrics_followers_count'].fillna(0) + 1
    df['adjusted_following_count'] = df['author_public_metrics_following_count'].fillna(0) + 1
    df['follower_following_ratio'] = df['adjusted_followers_count'] / df['adjusted_following_count']
    df['ratio_score'] = df['follower_following_ratio'].apply(lambda x: 1 if x > 1 else 0.01)
    df['verified_score'] = df['author_verified'].fillna('FALSE').apply(lambda x: 1 if x == True else 0.01)
    return df

def calculate_final_score(df):
    df['final_score'] = (df['death_confidence'] * df['independence_score'] * df['verified_score'] * df['ratio_score']) ** (1/4)
    return df

def main():
    parser = argparse.ArgumentParser(description='Process Twitter data for death scores.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output CSV file')
    args = parser.parse_args()

    start_time = pd.to_datetime("2023-02-06 01:17:35", utc=True)
    df = load_and_preprocess_csv(args.input, start_time)
    df['death_confidence'] = df.apply(process_row, axis=1)
    df = append_normalized_duplicate_counts(df, 'text', 'time_gap')
    df = calculate_user_scores(df)
    df = calculate_final_score(df)
    df.to_csv(args.output, index=False)
    print("Processing complete. The output file is saved at:", args.output)

if __name__ == "__main__":
    main()
