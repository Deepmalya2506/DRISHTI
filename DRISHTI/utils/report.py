from pprint import pprint


def dataset_report(
    metadata,
    raster_summary,
    band_stats,
    reciprocity
):

    print("\n" + "=" * 70)
    print("DRISHTI DATASET REPORT")
    print("=" * 70)

    print("\nMission Metadata")
    print("-" * 70)

    print(f"Processing Level : {metadata['product_type']}")
    print(f"Frequency Band   : {metadata['frequency_band']}")
    print(f"Projection       : {metadata.get('map_projection','Unknown')}")
    print(f"Pixel Spacing    : {metadata['output_pixel_spacing']} m")
    print(f"Looks            : {metadata['range_looks']} x {metadata['azimuth_looks']}")
    print(f"Calibration K    : {metadata['calibration_constant']}")
    print(f"Incidence Angle  : {metadata['incidence_angle']}°")

    print("\nRaster Summary")
    print("-" * 70)

    pprint(raster_summary)

    print("\nBand Statistics")
    print("-" * 70)

    for band, stats in band_stats.items():

        print(f"\n{band}")

        for k, v in stats.items():

            print(f"{k:10s}: {v}")

    print("\nReciprocity")
    print("-" * 70)

    print(f"RMSE        : {reciprocity['rmse']:.4f}")
    print(f"Bias        : {reciprocity['bias']:.4f}")
    print(f"Correlation : {reciprocity['correlation']:.6f}")

    print("=" * 70)