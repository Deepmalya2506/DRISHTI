from DRISHTI.utils.plot import *

def inspect_raw_dataset(dataset):

    bands = dataset["bands"]

    for name,image in bands.items():

        print(f"\n{name}")

        show_image(
            image,
            title=f"{name} Raw DN"
        )

        show_histogram(
            image,
            title=f"{name} Histogram"
        )

        show_histogram(
            image,
            title=f"{name} Histogram (Log)",
            log=True
        )

        show_image(
            log_scale(image),
            title=f"{name} Log DN"
        )