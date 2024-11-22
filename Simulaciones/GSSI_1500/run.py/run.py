import os
import pandas as pd

# Define constants and simulation parameters
BASE_DIRECTORY = r"C:\Users\nrodriguez\Desktop\RootBot\Simulaciones\GSSI_1500"
os.makedirs(BASE_DIRECTORY, exist_ok=True)

# Base template for gprMax input file
template = """#title: B-scan. 3 different root diameters at depth {depth}, soil {soil_perm} and root {root_perm}. Atenna: GSSI 1.5GHz (Model 5100)

#domain: 0.480 0.148 0.485
#dx_dy_dz: 0.001 0.001 0.001
#time_window: 6e-9

#material: {soil_perm} 0 1 0 soil
#material: {root_perm} 0 1 0 root

#box: 0 0 0 0.480 0.148 0.420 soil
#cylinder: 0.240 0 {z_start} 0.240 0.148 {z_start} {radius} root

#python:
from user_libs.antennas.GSSI import antenna_like_GSSI_1500
antenna_like_GSSI_1500(0.105 + current_model_run * 0.005, 0.074, 0.420, 0.001)
#end_python:

#geometry_view: 0 0 0 0.480 0.148 0.485 0.001 0.001 0.001 {name} n
"""

# Load the filtered simulation data
filtered_simulations_path = os.path.join(BASE_DIRECTORY, "Simulation_Plan.csv")
filtered_simulations = pd.read_csv(filtered_simulations_path)

# Prepare a list for the summary file
summary_data = []

# Iterate through the filtered simulation data
for index, row in filtered_simulations.iterrows():
    # Extract simulation parameters
    radius = row['Radio']
    depth = row['Profundidad (cm)']
    soil_perm = row['Permitividad Suelo']
    root_perm = row['Permitividad Ramas']
    
    # Calculate z_start for the cylinder
    z_start = round(0.485 - 0.065 - depth/100, 3)
    
    # Prepare simulation directory
    folder_name = f"radius_{radius}_depth_{depth}_soil_{soil_perm}_root_{root_perm}_antenna_GSSI1500"
    simulation_dir = os.path.join(BASE_DIRECTORY, folder_name)

    if os.path.exists(simulation_dir):
        print(f"\033[93mFolder {folder_name} already exists. Skipping simulation.\033[0m")
        continue  # Skip the rest of the loop for this simulation
    
    os.makedirs(simulation_dir, exist_ok=True)
    
    # Create the gprMax input file content
    input_file_content = template.format(
        soil_perm=soil_perm,
        root_perm=root_perm,
        z_start=z_start,
        radius=radius,
        name = folder_name, 
        depth=depth
    )
    
    # Save the input file
    input_file_path = os.path.join(simulation_dir, f"{folder_name}.in")
    with open(input_file_path, 'w') as input_file:
        input_file.write(input_file_content)
    
    # Run the simulation
    print(f"\033[95mRunning simulation for {folder_name}\033[0m")
    print(f"\033[95mpython -m gprMax \"{input_file_path}\" -n 54\033[0m")
    os.system(f"python -m gprMax \"{input_file_path}\" -n 54")

    # # Merge output files
    merged_output_path = os.path.join(simulation_dir, f"{folder_name}_merged.out")
    print(f"\033[95mpython -m tools.outputfiles_merge \"{input_file_path[:-3]}\"\033[0m")
    os.system(f"python -m tools.outputfiles_merge \"{input_file_path[:-3]}\"")

    # Generate B-scan plots
    # for component in ['Ex', 'Ey', 'Ez']: #solo Ey
    #     print(f"\033[95mpython -m tools.plot_Bscan \"{merged_output_path}\" {component}\033[0m")
    #     os.system(f"python -m tools.plot_Bscan \"{merged_output_path}\" {component}")

    # Append to summary data
    summary_data.append([index + 1, radius, depth, soil_perm, root_perm, "GSSI 1500", folder_name])

    for file_name in os.listdir(simulation_dir):
        if file_name.endswith(".vti"):
            file_path = os.path.join(simulation_dir, file_name)
            os.remove(file_path)
            print(f"\033[91mDeleted {file_path}\033[0m")

# Create a summary CSV file in the base directory
summary_file_path = os.path.join(BASE_DIRECTORY, "simulation_summary.csv")
summary_columns = ["Simulation No.", "Radius", "Depth (cm)", "Soil Permittivity", "Root Permittivity", "Antenna", "Folder Name"]
summary_df = pd.DataFrame(summary_data, columns=summary_columns)
summary_df.to_csv(summary_file_path, index=False)

print(f"\033[95mSimulation setup complete. Summary saved at: {summary_file_path}\033[0m")
