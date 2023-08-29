# coding: utf-8
# author: Tobias Westholm
# email: tobias_westholm@hotmail.com
import pandas as pd

def mean_intensities_and_circularity(df, image, ROI, cell_type1, cell_type2):
    """
    simple function that calculates and returns the mean intensities 
    for cell type 1, cell type 2, and both for the specified ROI ID. 
    It also calculates the mean circularity for the cells in the ROI.
    """
    only_CD45 = df.drop(df[df.Class == cell_type2].index)
    only_Ignore = df.drop(df[df.Class == cell_type1].index)
    CD45_mean_intensity = only_CD45["CD45_intensity"].mean()
    Ignore_mean_intensity = only_Ignore["CD45_intensity"].mean()
    Combined_mean_intensity = df["CD45_intensity"].mean()
    CD45_circularity = only_CD45["Circularity"].mean()
    Ignore_circularity = only_Ignore["Circularity"].mean()
    Combined_circularity = df["Circularity"].mean()

    # create results list
    results = [image, ROI, CD45_mean_intensity, Ignore_mean_intensity, Combined_mean_intensity, CD45_circularity, Ignore_circularity, Combined_circularity]

    return results
  
if __name__ == "__main__":
    #VARIABLES
    in_path = "C:\\Users\\tobia\\Desktop\\Exjobb\\Python_stuff\\intensities_and_circularity\\cell_intensity_measurements.csv"       #path to input csv file
    out_path = "C:\\Users\\tobia\\Desktop\\Exjobb\\Python_stuff\\intensities_and_circularity"      #path to the results directory, default is current directory'
    pair = "CD45:PathCellObject" #cell type pair
    separator = ','    #csv separator, default tab
    decimal = '.'       #float decimal sign, default: .
    
    # create the output dictionary
    out = {'image':[],
    'ROI':[],
    'CD45_mean_intensity':[],
    'Ignore_mean_intensity':[],
    'Combined_mean_intensity':[],
    'CD45_circularity':[],
    'Ignore_circularity':[],
    'Combined_circularity':[]}

    # read the csv file
    
    df = pd.read_csv(in_path,
                     sep=separator,
                     decimal=decimal,
                     low_memory=False,
                     skiprows=1,
                     usecols=[0, 1, 2, 3, 4],
                     names=['Image',
                            'Class',
                            'ROI',
                            'Circularity',
                            'CD45_intensity'])
    df.isna().sum(axis=0)
    #df = df.dropna(axis=0)
    #define cells
    cell_type2 = pair.split(':')[1]
    cell_type1 = pair.split(':')[0]
    # list all images
    images = df['Image'].unique()
    # check that all images have both classes
    for image in images:
        if cell_type1 not in df.groupby('Image').get_group(
            image)['Class'].unique():
            print(f"{cell_type1} not in {image}")
        if cell_type2 not in df.groupby('Image').get_group(
            image)['Class'].unique():
            print(f"{cell_type2} not in {image}")
    # iterate over images
    for image in images:
        # filter on cell type included in analysis AND clean out any annotations & detections (outside of ROIs) with the parent named "Image"
        filtered = df[(df['Class'] == cell_type1) | (
                  df['Class'] == cell_type2) & (df['ROI'] != 'Image')].reset_index(drop=True)
        # extract the image
        one_pic = filtered.groupby('Image').get_group(image).reset_index(drop=True)
        # iterate through all ROIs in the picture
        for roi_value in sorted(one_pic['ROI'].unique()):
            # pick out all rows with the right ROI number. roi_value MIGHT NEED TO BE CONVERTED TO STRING OR INTEGER IN THE COMPARISON BELOW
            one_roi = one_pic.loc[one_pic['ROI'] == roi_value].reset_index(drop=True)
            #one_roi = one_roi.drop(one_roi[one_roi.Class == cell_type1].index)
            #try:
            # calculate statistics.
            results = mean_intensities_and_circularity(one_roi, image, roi_value, cell_type1, cell_type2)
            #except Exception as e:
                #print(f'Error in {image}: {e}')
                #continue
            # append to output dictionary
            for key, value in zip(out.keys(), results):
                out[key].append(value)
    # create dataframe from out dictionary
    out_df = pd.DataFrame(out)
    print(out_df.head())

    # save the output
    out_df.to_csv(
        f'{out_path}/intensities_and_circularity_of_{cell_type1}_and_{cell_type2}.csv',
        index=False,
        sep='\t')
