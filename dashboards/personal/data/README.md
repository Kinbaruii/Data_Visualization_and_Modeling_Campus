# Your dataset

# Capital Bikeshare dashboard data

Source: UCI Machine Learning Repository, Bike Sharing dataset
https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset

Dataset creators: Hadi Fanaee-T and João Gama.

Files:
- day.csv: original daily dataset, containing 731 records from 2011–2012.
- Readme.txt: original data dictionary, including feature definitions and normalization details.

Each row represents one day of system-wide Capital Bikeshare rentals in Washington, D.C.

Dashboard features:
- dteday: date.
- workingday: 1 means neither a weekend nor a holiday; 0 means weekend or holiday.
- temp: normalized temperature on the source scale, not degrees Celsius.
- cnt: total daily rentals, including casual and registered rentals; not unique riders.

The dashboard creates year, day-type labels, and calendar-month features on a working copy. It retains all original records. Monthly values are mean daily rentals, calculated using the observed days in each selected month.

These historical observations do not establish causation or describe current demand.
