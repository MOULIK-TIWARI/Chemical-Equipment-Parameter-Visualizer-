# Requirements Document

## Introduction

This document specifies the requirements for a hybrid application that provides data visualization and analytics for chemical equipment. The system consists of a Django REST API backend that serves both a React web frontend and a PyQt5 desktop frontend. Users can upload CSV files containing equipment data, view analytics and visualizations, access historical datasets, and generate PDF reports.

## Glossary

- **System**: The Chemical Equipment Analytics Application (both web and desktop frontends plus Django backend)
- **Web Frontend**: The React.js-based web application interface
- **Desktop Frontend**: The PyQt5-based desktop application interface
- **Backend API**: The Django REST Framework API service
- **CSV File**: Comma-separated values file containing equipment data with columns: Equipment Name, Type, Flowrate, Pressure, Temperature
- **Dataset**: A collection of equipment records uploaded via CSV file
- **Summary Statistics**: Aggregated metrics including total count, averages, and type distribution
- **History**: The last 5 uploaded datasets stored in the database
- **PDF Report**: A generated document containing dataset summary and visualizations
- **User**: An authenticated person using either the web or desktop application

## Requirements

### Requirement 1

**User Story:** As a user, I want to upload a CSV file containing chemical equipment data from both web and desktop interfaces, so that I can analyze the equipment information.

#### Acceptance Criteria

1. WHEN the User selects a CSV file through the Web Frontend upload interface, THE System SHALL transmit the file to the Backend API for processing
2. WHEN the User selects a CSV file through the Desktop Frontend upload interface, THE System SHALL transmit the file to the Backend API for processing
3. WHEN the Backend API receives a CSV file, THE System SHALL validate that the file contains the required columns: Equipment Name, Type, Flowrate, Pressure, and Temperature
4. IF the uploaded CSV file is missing required columns, THEN THE System SHALL return an error message indicating which columns are missing
5. WHEN the Backend API successfully validates a CSV file, THE System SHALL parse the data using Pandas and store the dataset in the SQLite database

### Requirement 2

**User Story:** As a user, I want to view summary statistics of the uploaded equipment data, so that I can quickly understand the dataset characteristics.

#### Acceptance Criteria

1. WHEN the Backend API processes a dataset, THE System SHALL calculate the total count of equipment records
2. WHEN the Backend API processes a dataset, THE System SHALL calculate the average values for Flowrate, Pressure, and Temperature fields
3. WHEN the Backend API processes a dataset, THE System SHALL calculate the distribution of equipment by Type
4. WHEN the Web Frontend requests summary statistics, THE Backend API SHALL return the calculated metrics in JSON format
5. WHEN the Desktop Frontend requests summary statistics, THE Backend API SHALL return the calculated metrics in JSON format

### Requirement 3

**User Story:** As a user, I want to visualize equipment data through charts and tables, so that I can better understand patterns and distributions in the data.

#### Acceptance Criteria

1. WHEN the Web Frontend receives dataset information, THE System SHALL display the equipment data in a tabular format
2. WHEN the Web Frontend receives summary statistics, THE System SHALL render charts using Chart.js library
3. WHEN the Desktop Frontend receives dataset information, THE System SHALL display the equipment data in a tabular format
4. WHEN the Desktop Frontend receives summary statistics, THE System SHALL render charts using Matplotlib library
5. THE System SHALL display at minimum a distribution chart showing equipment counts by Type

### Requirement 4

**User Story:** As a user, I want to access my previously uploaded datasets, so that I can review historical equipment data without re-uploading files.

#### Acceptance Criteria

1. WHEN the Backend API successfully stores a new dataset, THE System SHALL maintain a history of the last 5 uploaded datasets in the SQLite database
2. WHEN the number of stored datasets exceeds 5, THE System SHALL remove the oldest dataset from the database
3. WHEN the User requests the dataset history through the Web Frontend, THE Backend API SHALL return a list of the stored datasets with their summary information
4. WHEN the User requests the dataset history through the Desktop Frontend, THE Backend API SHALL return a list of the stored datasets with their summary information
5. WHEN the User selects a historical dataset, THE System SHALL display the full data and visualizations for that dataset

### Requirement 5

**User Story:** As a user, I want to generate a PDF report of the equipment analysis, so that I can share or archive the results.

#### Acceptance Criteria

1. WHEN the User requests a PDF report through the Web Frontend, THE Backend API SHALL generate a PDF document containing the dataset summary statistics
2. WHEN the User requests a PDF report through the Desktop Frontend, THE Backend API SHALL generate a PDF document containing the dataset summary statistics
3. WHEN the Backend API generates a PDF report, THE System SHALL include visualizations of the equipment data distribution
4. WHEN the PDF generation is complete, THE System SHALL provide the PDF file for download to the User
5. THE System SHALL include the upload timestamp and dataset identifier in the PDF report

### Requirement 6

**User Story:** As a system administrator, I want users to authenticate before accessing the application, so that equipment data remains secure and access is controlled.

#### Acceptance Criteria

1. WHEN a User attempts to access protected endpoints on the Backend API, THE System SHALL require valid authentication credentials
2. WHEN a User provides valid credentials through the Web Frontend, THE System SHALL grant access to upload and view data
3. WHEN a User provides valid credentials through the Desktop Frontend, THE System SHALL grant access to upload and view data
4. IF a User provides invalid credentials, THEN THE System SHALL deny access and return an authentication error message
5. WHEN a User successfully authenticates, THE System SHALL maintain the session for subsequent API requests

### Requirement 7

**User Story:** As a developer, I want a sample CSV file available for testing, so that I can demonstrate and validate the application functionality without creating test data.

#### Acceptance Criteria

1. THE System SHALL include a sample CSV file named sample_equipment_data.csv in the project repository
2. THE sample CSV file SHALL contain valid equipment data with all required columns: Equipment Name, Type, Flowrate, Pressure, and Temperature
3. THE sample CSV file SHALL contain at minimum 10 equipment records for meaningful visualization
4. WHEN the sample CSV file is uploaded, THE System SHALL process it successfully without errors
5. THE sample CSV file SHALL include multiple equipment types to demonstrate distribution analysis
