%% EEG MINDWANDERING EXPERIENCE SAMPLING DATA PREPROCESSING PIPELINE
    % Authored by Christine Chesebrough (2023)
    
    % Written on MATLAB R20109b and EEGLAB 2023

% Requires the MATLAB Add-Ons (download from MathWorks with License)
    % Signal Processing Toolbox
    % Statistics and Machine Learning Toolbox

% Requires the following EEGLAB plugins:
    % Fileio
    % Fieldtrip
    % IC Label
    % Cleanline
    % MARA (ICA)
    % Carbon wire loop (CWL)

%% Initialize EEGLAB

if ~exist('EEG', 'var')
    eeglab;
end

%% INITIAL CLEANING STEPS

% define path to channel location file (make sure it's included in MATLAB
% path)
chanlocs= '/Users/christinechesebrough/Documents/MW_EEG_RS/BC-MR3-32.bvef';

% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save cleaned files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_cleaned';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.eeg'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end
    
    % Loop through EEG files in each subject folder
    for j = 1:length(eeg_files)
        eeg_file = fullfile(subject_folder, eeg_files(j).name);
        
     % Open EEG file using fileIO to read BrainVision files
        EEG = pop_fileio(eeg_file);

        % Resample recording to 1000 Hz
        EEG = pop_resample(EEG,1000);

        % Add channel locations from chanfile
        EEG = pop_chanedit(EEG, chanlocs,'lookup');

        % removing non-EEG channels for filtering (will be re-added later as necessary)
        channels_to_remove = 32:36;
        EEG = pop_select(EEG, 'nochannel', channels_to_remove);

        % band-pass filter from 1-55 Hz
        [EEG, com, b] = pop_eegfiltnew(EEG,1,55);

        % average reference
        EEG = pop_reref( EEG, []); 

        % cleanline (remove line noise) (optional)
        EEG = pop_cleanline(EEG,'chanlist',[1:length(EEG.chanlocs)],'ComputeSpectralPower', 1, ...
            'SignalType','Channels','VerboseOutput',1,...
            'SlidingWinLength',3, 'SlidingWinStep',2,...
            'LineAlpha',0.05); 
        
       % Save the cleaned EEG data to the subject's output folder
        [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
        output_filename = fullfile(output_subject_directory, [eeg_filename, '_cleaned', eeg_extension]);
        pop_saveset(EEG, output_filename);

    fprintf('Processed and saved: %s\n', output_filename);
        fprintf('Downsampled and saved: %s\n', output_filename);
    end
end


%% Automatic relabeling of events

% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_cleaned';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save relabeled files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_relabeled';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

newEventTypes = readcell('event_labels.csv'); 

% Load event labels from a CSV file
event_labels = readcell('event_labels.csv');
% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.set'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end
    
    % Loop through EEG files in the subject folder
    for j = 1:length(eeg_files)
        eeg_file = fullfile(subject_folder, eeg_files(j).name);
        
        % Open EEG file using fileIO to read BrainVision files
        EEG = pop_fileio(eeg_file);
        
        % Ensure that the number of event labels matches the number of events in the EEG dataset
        if length(event_labels) ~= length(EEG.event)
            warning('Number of event labels does not match the number of events in the EEG dataset.');
        else
            fprintf('Number of event labels matches the number of events in the EEG dataset.\n');
        end
        
        % Loop through each event and replace the event type
        for eventIndex = 1:length(EEG.event)
            EEG.event(eventIndex).type = event_labels{eventIndex};
        end
              
        % Save the relabeled EEG data to the subject's output folder
        [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
     
        output_filename = fullfile(output_subject_directory, [eeg_filename, '_relabeled', eeg_extension]);
        pop_saveset(EEG, output_filename);

        fprintf('Processed and saved: %s\n', output_filename);
    end
end


%% Concatenating across subject

% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_relabeled';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save concatenated files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_concat';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.set'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end
    
    % Initialize an empty EEG structure to store the concatenated data
    allEEG = [];
    
    % Loop through each .set file and load EEG data
    for j = 1:length(eeg_files)
        eeg_file = fullfile(subject_folder, eeg_files(j).name);
        
        % Open EEG file using fileIO to read BrainVision files
        EEG = pop_fileio(eeg_file);

        % Append EEG data to the existing data
        if isempty(allEEG)
            allEEG = EEG;
        else
            allEEG = pop_mergeset(allEEG, EEG);
        end
    end
    
    % Save the concatenated EEG data to the subject's output folder
        [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
        output_filename = fullfile(output_subject_directory, [eeg_filename, '_concat', eeg_extension]);
        pop_saveset(allEEG, output_filename);
        fprintf('Processed and saved: %s\n', output_filename);
end


% Clean up
eeglab redraw;

% Display a message
disp(['Concatenated data saved as ' outputFile]);


%% ICA (using RUNICA ALGO)

% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_concat';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save ICA processed files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_ICA';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.set'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end

    for j = 1:length(eeg_files)
    eeg_file = fullfile(subject_folder, eeg_files(j).name);

    % Open EEG file using fileIO to read BrainVision files
    EEG = pop_fileio(eeg_file);
    
    %run ICA
    EEG = pop_runica(EEG, 'icatype', 'runica');
    
% Save the ICA processed data to the subject's output folder
    [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
    output_filename = fullfile(output_subject_directory, [eeg_filename, '_ICA', eeg_extension]);
    pop_saveset(EEG, output_filename);
    fprintf('Processed and saved: %s\n', output_filename);
end

end   


%% Automatic component rejection using IC label

% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_ICA';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save component rejected files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_ICrej';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.set'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end

    for j = 1:length(eeg_files)
    eeg_file = fullfile(subject_folder, eeg_files(j).name);

    % Open EEG file using fileIO to read BrainVision files
    EEG = pop_fileio(eeg_file);

    for i = 1:numel(file_list)
        % Get the file name
        file_name = file_list(i).name;

        % Create the full file path
        full_file_path = fullfile(folder_path, file_name);

        % Display or process the file as needed
        fprintf('Processing file: %s\n', full_file_path);

        EEG = pop_loadset();
        EEG = eeg_checkset(EEG);

        log_ICLabelClsCount = zeros(1,7); % Total classified ICs
        log_ICLabelRejCount = zeros(1,8); % Total rejected ICs

        log_rejCorInd = [];
        log_rejCorCount = 0;

        % IC classes
        % 1: Brain
        % 2: Muscle
        % 3: Eye
        % 4: Heart
        % 5: Line Noise
        % 6: Channel Noise
        % 7: Other

        %               Min Max
        rejThreshold = [0   0;    %Brain
                        0.59 1;    %Muscle
                        0.59  1;    %Eye
                        0.59  1;    %Heart
                        0.59  1;    %Line noise
                        0.59  1;    %Channel noise
                        0.59 1];   %Other

        EEG = pop_iclabel(EEG, 'default');
        EEG = pop_icflag(EEG, rejThreshold);


        % Loop through each IC

        log_rejInd_ICL = num2str(find(EEG.reject.gcompreject)');
        log_rejCount_ICL = length(find(EEG.reject.gcompreject));

        %remove flagged ICs

        remCompsFinal = find(EEG.reject.gcompreject);
        EEG = pop_subcomp( EEG, remCompsFinal, 0);

        % Update EEG structure and save the updated dataset
        EEG = eeg_checkset(EEG);

        % Display a message indicating the rejected components
        fprintf('Rejected %d IC components.\n', length(reject_ICs));

        % save 
        % Extract the base filename without the file extension
        [~, base_filename, ~] = fileparts(file_name);

        % Define a new filename based on the original filename
        new_filename = [base_filename '_ICA_rej'];  % You can modify this naming scheme as needed

    
    % Save the new data to the subject's output folder
        [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
        output_filename = fullfile(output_subject_directory, [eeg_filename, '_ICrej', eeg_extension]);
        pop_saveset(EEG, output_filename);
        fprintf('Processed and saved: %s\n', output_filename);

    end   
    end

%% ICA rejection using MARA (USE INSTEAD OF IC-LABEL)

% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_ICA';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save component rejected files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_ICrej';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.set'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end

    for j = 1:length(eeg_files)
    eeg_file = fullfile(subject_folder, eeg_files(j).name);

    % Open EEG file using fileIO to read BrainVision files
    EEG = pop_fileio(eeg_file);

    for i = 1:numel(file_list)
        % Get the file name
        file_name = file_list(i).name;

        % Create the full file path
        full_file_path = fullfile(folder_path, file_name);

        % Display or process the file as needed
        fprintf('Processing file: %s\n', full_file_path);

        EEG = pop_loadset();
        EEG = eeg_checkset(EEG);

        MARAinput = [0,0,0,0,0];

        ALLEEG = EEG;
        CURRENTSET = 1;

        [~,EEG,~] = processMARA(ALLEEG, EEG, CURRENTSET, MARAinput);

        %remove flagged ICs

        remCompsFinal = find(EEG.reject.gcompreject);
        EEG = pop_subcomp( EEG, []);

        % Update EEG structure and save the updated dataset
        EEG = eeg_checkset(EEG);
    
   % Save the new data to the subject's output folder
        [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
        output_filename = fullfile(output_subject_directory, [eeg_filename, '_MARArej', eeg_extension]);
        pop_saveset(EEG, output_filename);
        fprintf('Processed and saved: %s\n', output_filename);

    end    
end   

  
%% %% Epoching

  
% define path to directory with raw data files
% Set the main directory where subject folders are located
main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_ICArej';

% Get a list of subject folders
subject_folders = dir(main_directory);
subject_folders = subject_folders([subject_folders.isdir]); % Keep only directories
subject_folders = subject_folders(~ismember({subject_folders.name}, {'.', '..'})); % Remove '.' and '..'

% Create a new main directory to save component rejected files
output_main_directory = '/Users/christinechesebrough/Documents/MW_EEG_dir/MW_EEG_Epoched';
if ~exist(output_main_directory, 'dir')
    mkdir(output_main_directory);
end

% Loop through subject folders
for i = 1:length(subject_folders)
    subject_folder = fullfile(main_directory, subject_folders(i).name);
    
    % Get a list of EEG files in the subject folder
    eeg_files = dir(fullfile(subject_folder, '*.set'));
    
    % Create a new folder for the subject in the output main directory
    output_subject_directory = fullfile(output_main_directory, subject_folders(i).name);
    if ~exist(output_subject_directory, 'dir')
        mkdir(output_subject_directory);
    end

    for j = 1:length(eeg_files)
    eeg_file = fullfile(subject_folder, eeg_files(j).name);

    % Open EEG file using fileIO to read BrainVision files
    EEG = pop_fileio(eeg_file);

    for i = 1:numel(file_list)
        % Get the file name
        file_name = file_list(i).name;

        % Create the full file path
        full_file_path = fullfile(folder_path, file_name);

        % Display or process the file as needed
        fprintf('Processing file: %s\n', full_file_path);

        EEG = pop_loadset();
        EEG = eeg_checkset(EEG);

        %Epoch using [-2000 100] window
    
        EEG = pop_epoch(EEG); 
        
   % Save the new data to the subject's output folder
        [~, eeg_filename, eeg_extension] = fileparts(eeg_files(j).name);
        output_filename = fullfile(output_subject_directory, [eeg_filename, '_epoched', eeg_extension]);
        pop_saveset(EEG, output_filename);
        fprintf('Processed and saved: %s\n', output_filename);

    end    
end   

  

end 
