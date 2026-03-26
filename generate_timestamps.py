from itertools import islice, product

import pandas as pd

# -----------------------------
# 1️⃣ Define date range
# -----------------------------
start_date = '2022-01-01'
end_date = '2030-12-31'

# Generate all dates
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Generate all hours
hours = range(24)

# -----------------------------
# 2️⃣ Generators for timestamp rows
# -----------------------------
def generate_day_rows():
    for base_date in dates:
        yield {
            "Timestamp_Day": base_date,
            "DateOnly": base_date.date(),
            "Month_Number": base_date.month,
            "Month_Name": base_date.strftime('%B'),
            "Year": base_date.year,
            "Day_Number": base_date.day,
            "Day_Display": base_date.strftime('%d')
        }


def generate_hour_rows():
    for base_date, hour in product(dates, hours):
        timestamp_hour = base_date + pd.Timedelta(hours=hour)
        yield {
            "Timestamp_Hour": timestamp_hour,
            "Timestamp_Day": base_date,
            "DateOnly": base_date.date(),
            "Month_Number": base_date.month,
            "Month_Name": base_date.strftime('%B'),
            "Year": base_date.year,
            "Day_Number": base_date.day,
            "Day_Display": base_date.strftime('%d'),
            "Hour_Number": hour,
            "Hour_Display": timestamp_hour.strftime('%H:%M')
        }

hour_rows_generator = generate_hour_rows()

# -----------------------------
# 3️⃣ Write day CSV
# -----------------------------
day_df = pd.DataFrame(generate_day_rows())
day_df.to_csv("timestamp_days.csv", index=False)

# -----------------------------
# 4️⃣ Write hour CSV in chunks
# -----------------------------
chunk_size = 1000000  # 1 million rows per chunk
first_chunk = True

while True:
    # Take next chunk from generator
    chunk_iter = list(islice(hour_rows_generator, chunk_size))
    if not chunk_iter:  # Generator exhausted
        break

    df_chunk = pd.DataFrame(chunk_iter)

    # Write chunk to CSV
    df_chunk.to_csv(
        "timestamp_hours.csv",
        index=False,
        mode='w' if first_chunk else 'a',
        header=first_chunk
    )
    first_chunk = False

print("Timestamp day and hour CSV generation completed!")