from DRISHTI.core.data_ingestion import build_drishti_dataset
from DRISHTI.core.visualization import total_plot

def main():
    dataset = build_drishti_dataset()
    total_plot(dataset)

if __name__ == "__main__":
    main()
