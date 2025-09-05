import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path

class WeatherAnalyzer:
    def __init__(self, data_folder="temperatures"):
        """
        Initialize the weather analyzer for monthly temperature data
        
        Args:
            data_folder (str): Path to the folder containing CSV files
        """
        self.data_folder = data_folder
        self.all_data = pd.DataFrame()
        self.season_mapping = {
            'December': 'Summer', 'January': 'Summer', 'February': 'Summer',
            'March': 'Autumn', 'April': 'Autumn', 'May': 'Autumn',
            'June': 'Winter', 'July': 'Winter', 'August': 'Winter',
            'September': 'Spring', 'October': 'Spring', 'November': 'Spring'
        }
        
    def load_all_data(self):
        """Load and combine all CSV files from the temperatures folder"""
        print(f"Loading monthly temperature data from {self.data_folder} folder...")
        
        # Get all CSV files in the temperatures folder
        csv_pattern = os.path.join(self.data_folder, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.data_folder} folder")
        
        all_dataframes = []
        
        for file_path in csv_files:
            print(f"Processing {os.path.basename(file_path)}...")
            try:
                # Extract year from filename
                filename = os.path.basename(file_path)
                # Try to extract year from filename like "stations_group_1990.csv"
                try:
                    year = int(filename.split('_')[-1].replace('.csv', ''))
                except:
                    print(f"Warning: Could not extract year from {filename}, skipping...")
                    continue
                
                # Read CSV file
                df = pd.read_csv(file_path)
                
                print(f"  Columns found: {list(df.columns)}")
                print(f"  Number of stations: {len(df)}")
                
                # Check for required columns
                station_col = None
                if 'STATION_NAME' in df.columns:
                    station_col = 'STATION_NAME'
                elif 'Station' in df.columns:
                    station_col = 'Station'
                elif 'station' in df.columns:
                    station_col = 'station'
                else:
                    print(f"  Warning: No station name column found, skipping...")
                    continue
                
                # Define month columns
                month_columns = ['January', 'February', 'March', 'April', 'May', 'June',
                               'July', 'August', 'September', 'October', 'November', 'December']
                
                # Check which month columns exist
                available_months = [col for col in month_columns if col in df.columns]
                
                if not available_months:
                    print(f"  Warning: No month columns found, skipping...")
                    continue
                
                print(f"  Available months: {available_months}")
                
                # Reshape data from wide to long format
                # Create a list to store all temperature records
                records = []
                
                for _, row in df.iterrows():
                    station_name = row[station_col]
                    
                    for month in available_months:
                        temp_value = row[month]
                        
                        # Skip if temperature is NaN or invalid
                        if pd.isna(temp_value):
                            continue
                        
                        # Convert to numeric
                        try:
                            temp_numeric = float(temp_value)
                        except:
                            continue
                        
                        # Create a record for this station-month-year combination
                        records.append({
                            'Station': station_name,
                            'Year': year,
                            'Month': month,
                            'Temperature': temp_numeric,
                            'Season': self.season_mapping[month]
                        })
                
                if records:
                    df_reshaped = pd.DataFrame(records)
                    all_dataframes.append(df_reshaped)
                    print(f"  Successfully processed {len(records)} temperature records")
                else:
                    print(f"  No valid temperature data found")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        
        if not all_dataframes:
            raise ValueError("No valid data files could be processed")
        
        # Combine all dataframes
        self.all_data = pd.concat(all_dataframes, ignore_index=True)
        
        print(f"\nData loading complete!")
        print(f"Total temperature records: {len(self.all_data):,}")
        print(f"Unique stations: {self.all_data['Station'].nunique()}")
        print(f"Years covered: {sorted(self.all_data['Year'].unique())}")
        print(f"Temperature range: {self.all_data['Temperature'].min():.1f}°C to {self.all_data['Temperature'].max():.1f}°C")
        
        # Show some sample data
        print(f"\nSample data:")
        print(self.all_data.head(10))
        
    def calculate_seasonal_averages(self):
        """Calculate average temperature for each season across all stations and years"""
        print("\nCalculating seasonal averages...")
        
        # Group by season and calculate mean temperature
        seasonal_avg = self.all_data.groupby('Season')['Temperature'].mean()
        
        # Order seasons logically (Summer, Autumn, Winter, Spring)
        season_order = ['Summer', 'Autumn', 'Winter', 'Spring']
        seasonal_avg = seasonal_avg.reindex(season_order)
        
        # Save to file
        with open('average_temp.txt', 'w') as f:
            f.write("Seasonal Average Temperatures (All Stations, All Years)\n")
            f.write("=" * 55 + "\n")
            for season, temp in seasonal_avg.items():
                f.write(f"{season}: {temp:.1f}°C\n")
        
        print("Seasonal averages saved to 'average_temp.txt'")
        return seasonal_avg
    
    def find_largest_temperature_range(self):
        """Find station(s) with the largest temperature range"""
        print("\nCalculating temperature ranges by station...")
        
        # Group by station and calculate min, max, and range
        station_stats = self.all_data.groupby('Station')['Temperature'].agg(['min', 'max']).reset_index()
        station_stats['Range'] = station_stats['max'] - station_stats['min']
        
        # Sort by range to see the results
        station_stats = station_stats.sort_values('Range', ascending=False)
        
        # Find the maximum range
        max_range = station_stats['Range'].max()
        stations_with_max_range = station_stats[station_stats['Range'] == max_range]
        
        # Save to file
        with open('largest_temp_range_station.txt', 'w') as f:
            f.write("Station(s) with Largest Temperature Range\n")
            f.write("=" * 40 + "\n")
            for _, row in stations_with_max_range.iterrows():
                f.write(f"Station {row['Station']}: Range {row['Range']:.1f}°C "
                       f"(Max: {row['max']:.1f}°C, Min: {row['min']:.1f}°C)\n")
        
        print(f"Temperature range analysis saved to 'largest_temp_range_station.txt'")
        return stations_with_max_range
    
    def analyze_temperature_stability(self):
        """Find stations with most stable and most variable temperatures"""
        print("\nAnalyzing temperature stability...")
        
        # Calculate standard deviation for each station
        station_std = self.all_data.groupby('Station')['Temperature'].std().reset_index()
        station_std.columns = ['Station', 'StdDev']
        
        # Remove stations with NaN std dev (only one data point)
        station_std = station_std.dropna()
        
        if len(station_std) == 0:
            print("Warning: No stations with sufficient data for stability analysis")
            return None, None
        
        # Find most stable (minimum std dev) and most variable (maximum std dev)
        min_std = station_std['StdDev'].min()
        max_std = station_std['StdDev'].max()
        
        most_stable = station_std[station_std['StdDev'] == min_std]
        most_variable = station_std[station_std['StdDev'] == max_std]
        
        # Save to file
        with open('temperature_stability_stations.txt', 'w') as f:
            f.write("Temperature Stability Analysis\n")
            f.write("=" * 30 + "\n\n")
            
            f.write("Most Stable Station(s):\n")
            for _, row in most_stable.iterrows():
                f.write(f"Most Stable: Station {row['Station']}: StdDev {row['StdDev']:.1f}°C\n")
            
            f.write("\nMost Variable Station(s):\n")
            for _, row in most_variable.iterrows():
                f.write(f"Most Variable: Station {row['Station']}: StdDev {row['StdDev']:.1f}°C\n")
        
        print("Temperature stability analysis saved to 'temperature_stability_stations.txt'")
        return most_stable, most_variable
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\nGenerating summary report...")
        
        with open('analysis_summary.txt', 'w') as f:
            f.write("AUSTRALIAN WEATHER STATION TEMPERATURE ANALYSIS SUMMARY\n")
            f.write("=" * 55 + "\n\n")
            
            f.write(f"Analysis Period: {self.all_data['Year'].min()} to {self.all_data['Year'].max()}\n")
            f.write(f"Total Records Analyzed: {len(self.all_data):,}\n")
            f.write(f"Number of Weather Stations: {self.all_data['Station'].nunique()}\n")
            f.write(f"Years Covered: {sorted(self.all_data['Year'].unique())}\n\n")
            
            # Overall statistics
            f.write("OVERALL TEMPERATURE STATISTICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Overall Mean Temperature: {self.all_data['Temperature'].mean():.1f}°C\n")
            f.write(f"Overall Standard Deviation: {self.all_data['Temperature'].std():.1f}°C\n")
            f.write(f"Absolute Maximum: {self.all_data['Temperature'].max():.1f}°C\n")
            f.write(f"Absolute Minimum: {self.all_data['Temperature'].min():.1f}°C\n")
            f.write(f"Overall Range: {self.all_data['Temperature'].max() - self.all_data['Temperature'].min():.1f}°C\n\n")
            
            # Monthly statistics
            f.write("MONTHLY AVERAGE TEMPERATURES\n")
            f.write("-" * 28 + "\n")
            monthly_avg = self.all_data.groupby('Month')['Temperature'].mean()
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            monthly_avg = monthly_avg.reindex(month_order)
            for month, temp in monthly_avg.items():
                f.write(f"{month:>10}: {temp:.1f}°C\n")
            
            f.write("\n")
            
            # Station list
            f.write("WEATHER STATIONS INCLUDED\n")
            f.write("-" * 25 + "\n")
            stations = sorted(self.all_data['Station'].unique())
            for i, station in enumerate(stations, 1):
                f.write(f"{i:2d}. {station}\n")
        
        print("Summary report saved to 'analysis_summary.txt'")
    
    def run_complete_analysis(self):
        """Run all analysis functions"""
        print("Starting Australian Weather Station Temperature Analysis")
        print("(Monthly Data Format)")
        print("=" * 60)
        
        try:
            # Load all data
            self.load_all_data()
            
            # Perform all analyses
            seasonal_averages = self.calculate_seasonal_averages()
            temp_ranges = self.find_largest_temperature_range()
            stable_stations, variable_stations = self.analyze_temperature_stability()
            
            # Generate summary report
            self.generate_summary_report()
            
            print("\n" + "=" * 60)
            print("ANALYSIS COMPLETE!")
            print("=" * 60)
            print("\nOutput files created:")
            print("• average_temp.txt - Seasonal temperature averages")
            print("• largest_temp_range_station.txt - Stations with largest temperature ranges")
            print("• temperature_stability_stations.txt - Most stable and variable stations")
            print("• analysis_summary.txt - Complete analysis summary")
            
            # Display key results
            print("\nKEY RESULTS PREVIEW:")
            print("-" * 20)
            print("Seasonal Averages:")
            for season, temp in seasonal_averages.items():
                print(f"  {season}: {temp:.1f}°C")
            
            print(f"\nLargest Temperature Range:")
            for _, row in temp_ranges.iterrows():
                print(f"  Station {row['Station']}: {row['Range']:.1f}°C")
                
            if stable_stations is not None and variable_stations is not None:
                print(f"\nMost Stable Station:")
                for _, row in stable_stations.iterrows():
                    print(f"  Station {row['Station']}: StdDev {row['StdDev']:.1f}°C")
                    
                print(f"\nMost Variable Station:")
                for _, row in variable_stations.iterrows():
                    print(f"  Station {row['Station']}: StdDev {row['StdDev']:.1f}°C")
                
        except Exception as e:
            print(f"\nError during analysis: {str(e)}")
            print("Please check that:")
            print("1. The 'temperatures' folder exists")
            print("2. CSV files are present in the folder")
            print("3. CSV files contain columns: STATION_NAME and monthly temperature columns")


def main():
    """Main function to run the weather analysis"""
    # Create analyzer instance
    analyzer = WeatherAnalyzer()
    
    # Run complete analysis
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()