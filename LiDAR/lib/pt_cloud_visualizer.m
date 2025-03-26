% AEGIS LiDAR Point Cloud Visualization Test Program


% ALL POINT CLOUD CAPTURES ------------------------------------------------

%%%         MARCH 18, 2025 TEST FILES                                   %%%
%ptCloud = pcread('..\test_clouds\test2.pcd');
%ptCloud = pcread('..\test_clouds\test3.pcd');
%ptCloud = pcread('..\test_clouds\cloud_20250318_183733.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_18_time_19_50_42_DOUBLE.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_18_time_21_26_43.pcd');

%%%         MARCH 20, 2025 TEST FILES                                   %%%
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_12_00_00.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_12_44_25.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_12_48_32.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_12_48_32_WINDOWS.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_14_32_40.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_14_41_43.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_20_50_06.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_20_54_27.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_20_58_01.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_21_01_07.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_21_09_19.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_21_14_06.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_22_15_13.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_22_30_05_FIXED_IT.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_22_55_51.pcd');

%%%         MARCH 21, 2025 TEST FILES                                   %%%
%ptCloud = pcread('..\test_clouds\cloud_2025_03_21_time_21_18_07.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_21_time_21_29_12.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_21_time_21_43_24.pcd');

%%%         MARCH 24, 2025 TEST FILES                                   %%%
%ptCloud = pcread('..\test_clouds\cloud_2025_03_24_time_16_30_38.pcd');


%%%         INTERESTING TEST FILES                                      %%%

% FIRST SCAN WITH IDENTIFIABLE FEATURES
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_20_time_12_48_32_WINDOWS.pcd');

% LOOK AT THIS ONE TO UNDERSTAND COORDINATE TRANSFORMATION VVVVV
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_20_time_20_50_06.pcd');

% SINGLE RINGS
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_20_time_21_01_07.pcd');
%ptCloud = pcread('..\test_clouds\cloud_2025_03_20_time_22_15_13.pcd');

% GOOD BUT DISTORTED
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_20_time_21_09_19.pcd');

% FIRST FIXED SCAN!!! DOUBLED POINTS PER RING (MAX_PACKETS)
% There's still a problem... not sure how to fix.
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_20_time_22_30_05_FIXED_IT.pcd');

% Doubled points again, half degree steps between ring. Unreal.
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_20_time_22_55_51.pcd');

% Great res but back to the problem. Moved using steps instead of degrees.
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_21_time_21_29_12.pcd');

% Same problem. Moved using degrees, and the problem reappeared. Shit.
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_21_time_21_43_24.pcd');

% Good leveling, good example of distortion.
%ptCloud = pcread('D:\AEGIS Code\scan\cloud_2025_03_24_time_16_30_38.pcd');


% FILTERING TESTING -------------------------------------------------------

% disp("Count before outlier removal: ");
% disp(ptCloud.Count);
% 
% ptCloud = pcdenoise(ptCloud);
% 
% disp("Count after outlier removal: ");
% disp(ptCloud.Count);

%ptCloud = removePointsInToroid(ptCloud, [0, 0, -1.6], 0.5, 0.25);
%ptCloud = removePointsInToroid(ptCloud, [], , );
%ptCloud = removePointsInToroid(ptCloud, [], , );
%ptCloud = removePointsInToroid(ptCloud, [], , );
%ptCloud = removePointsInToroid(ptCloud, [], , );


% VISUALIZER --------------------------------------------------------------

pcviewer(ptCloud, 'white', ShowPointCloudAxes='on');


% FUNCTIONS ---------------------------------------------------------------

% THIS IS A GPT-GENERATED FUNCTION
function filteredCloud = removePointsInToroid(ptCloud, center, radius, thickness)
% removePointsInToroid removes points from a 3D point cloud that lie inside a toroid.
%
%   filteredCloud = removePointsInToroid(ptCloud, center, radius, thickness)
%
% Inputs:
%   ptCloud   - Either an Nx3 matrix of 3D points or a MATLAB pointCloud object.
%   center    - 1x3 vector representing the center of the toroid.
%   radius    - Scalar representing the major radius (distance from the center 
%               of the toroid to the center of the tube).
%   thickness - Scalar representing the full diameter of the tube (minor axis).
%
% Output:
%   filteredCloud - The filtered point cloud, returned as a pointCloud object if 
%                   the input was a pointCloud object, or as an Nx3 matrix otherwise.
%
% Assumptions:
%   The toroid is assumed to be aligned with the z-axis. For a differently
%   oriented toroid, you would need to apply a coordinate transformation.

    pts = ptCloud.Location;

    % Compute the minor radius (half of the thickness).
    minorRadius = thickness / 2;
    
    % Compute the distance in the XY plane from each point to the toroid's center.
    d_xy = sqrt((pts(:,1) - center(1)).^2 + (pts(:,2) - center(2)).^2);
    
    % Use the toroid's implicit equation:
    % ((d_xy - radius)^2 + (z - center_z)^2) < minorRadius^2.
    inside = ((d_xy - radius).^2 + (pts(:,3) - center(3)).^2) < minorRadius^2;
    
    % Filter out the points that lie inside the toroid.
    ptsFiltered = pts(~inside, :);
    
    % Return the filtered points in the same format as the input.
    filteredCloud = pointCloud(ptsFiltered);
end