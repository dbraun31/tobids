% Convert matlab table to csv

% Specify the paths to the 'mat' and 'csv' directories
mat_dir = 'mats/';
csv_dir = 'csvs/';

% List all .mat files in the 'mat' directory
mat_files = dir(fullfile(mat_dir, '*.mat'));

% Loop through each .mat file
for i = 1:numel(mat_files)
    % Load the .mat file
    mat_file = fullfile(mat_dir, mat_files(i).name);
    data = load(mat_file)
    
    % Define the name for the corresponding .csv file in the 'csv' directory
    [~, base_name, ~] = fileparts(mat_files(i).name);
    csv_file = fullfile(csv_dir, [base_name, '.csv']);
    
    % Save the table as a .csv file
    writetable(data.Results, csv_file);
    
    % Display a message to indicate the conversion
    fprintf('Converted and saved %s to %s\n', mat_files(i).name, csv_file);
end

