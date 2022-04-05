import matplotlib
from matplotlib import dates as mdates, pyplot as plt, patches as mpatches, colors
import numpy as np
import pandas as pd
from collections import defaultdict


def plot_barcode():

    code_len = 100
    pixel_per_bar = 8
    dpi = 300

    fig, axes = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(code_len * pixel_per_bar / dpi, 0.5), dpi=dpi
    )

    second_color = ["red", "orange", "purple"]

    for i, ax in enumerate(axes):
        code = np.random.choice([0, 1], size=(100,))
        ax.get_yaxis().set_visible(False)
        cmap = colors.ListedColormap(["white", second_color[i]])
        ax.imshow(code.reshape(1, -1), cmap=cmap, aspect="auto", interpolation="nearest")

    plt.show()


def plot_evts():

    matplotlib.rcParams["font.size"] = 8.0

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    # create random data
    data1 = np.random.random([1, 50])
    print(data1)
    print(data1[0])

    # set different colors for each set of positions
    colors1 = ["C{}".format(i) for i in range(data1.shape[0])]

    # set different line properties for each set of positions
    # note that some overlap
    lineoffsets1 = np.array([-15, -3, 1, 1.5, 6, 10])
    linelengths1 = [5, 2, 1, 1, 3, 1.5]

    fig, axs = plt.subplots()

    # create a horizontal plot
    axs.eventplot(data1, colors=colors1)

    plt.show()

def plot_pids_timeline_cpu(start=None, end=None, outname=None):

    #pids = ["2744156","2744477","2744518","2744799","2744839","2745385","2745425","2745824","2745888",
    #"2747135","2747207","2748968","2749075","2751145","2751341","2751866","2751908","2752207","2752291",
    #"2752824","2752949","2753573","2753710","2754153","2754193",
    #"2754558","2754598","2754994","2755047","2755448","2755488","2755764","2755804"]
    pids=["3691113"
    #,"3691246"
    ]
    bar_height = 1
    ymins = [0, 1, 2]
    categories = ["BIO", "VFS", "OPEN"]
    colors_dict = dict(
        OPENAT="purple",
        VFSOPEN="slateblue",
        VFSR="dodgerblue",
        VFSW="red",
        BIOR="blue",
        BIOW="red",
    )

    fig, axs = plt.subplots(
        nrows=len(pids) + 1,
        ncols=1,
        figsize=(30, len(pids) * 3),
        gridspec_kw={"height_ratios": [3] * (len(pids) ) + [1]},  # 1 for timeline
        sharex=True,
    )

    #
    # Plot CPU
    #
    df = pd.read_csv(
        f"data/cpu_data/cpu_all.csv",
        sep=",",
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if start is not None:
        df = df[df["timestamp"] > np.datetime64(start)]
    if end is not None:
        df = df[df["timestamp"] < np.datetime64(end)]

    ax = axs[0]

    #ax.set_title("CPU Usage")
    #ax.set_ylabel("percent utilisation(%)")

    # There are more fields available but weren't very interesting
    variables = [
        "%usr",
        "%sys",
        "%iowait",
        "%idle",
    ]

    n_features = len(variables)

    cm = plt.get_cmap("gist_rainbow")  # Colormap

    for i, var in enumerate(variables):
        line = ax.plot(df["timestamp"], df[var], label=var, linewidth=1)
        line[0].set_color(cm(1 * i / n_features))

    ax.grid(True, which="both", linestyle="--", color="grey", alpha=0.2)
    ax.tick_params(which="both", direction="in")

    ax.set_ylim(ymin=0)
    ax.legend(bbox_to_anchor=(1, 0.5), loc="center left")

    # ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=100))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    #
    # Plot PIDs
    #
    for i, pid in enumerate(pids):
        print(f"Processing pid {pid}")

        df = pd.read_csv(
            f"data/st_end_data/st_end_data_{pid}", names=["start_date", "end_date", "event"]
        )
        df = df[["start_date", "end_date", "event"]]
        df.start_date = pd.to_datetime(df.start_date).astype(np.datetime64)
        df.end_date = pd.to_datetime(df.end_date).astype(np.datetime64)

        if start is not None:
            df = df[df["end_date"] > np.datetime64(start)]
        if end is not None:
            df = df[df["end_date"] < np.datetime64(end)]


        # Can't define this earlier
        masks = {
            "BIO": (df["event"] == "BIOR") | (df["event"] == "BIOW"),
            "OPEN": (df["event"] == "OPENAT") | (df["event"] == "VFSOPEN"),
            "VFS": (df["event"] == "VFSR") | (df["event"] == "VFSW"),
        }
        #print(len(df["event"]))
        ax = axs[i+1]
        ax.set_title(f"{pid}")

        # Plot the events
        #count=0
        for j, category in enumerate(categories):
            mask = masks[category]
            #count=count+1
            start_dates = mdates.date2num(df.loc[mask].start_date)
            end_dates = mdates.date2num(df.loc[mask].end_date)
            # Could increase bar width by rounding up durations to nearest ms or such
            durations = end_dates - start_dates

            xranges = list(zip(start_dates, durations))
            ymin = ymins[j] - 0.5
            yrange = (ymin, bar_height)
            colors = [colors_dict[event] for event in df.loc[mask].event]
            ax.broken_barh(xranges, yrange, facecolors=colors, alpha=1)
            # you can set alpha to 0.6 to check if there are some overlaps
        #print(count)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

        ax.grid(True, axis="x", linestyle="--", linewidth=0.45, alpha=0.2, color="grey")
        ax.tick_params(which="both", direction="in")

        # Format the x-ticks
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=100))
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%H:%M:%S",
            )
        )

        # Format the y-ticks
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories)

        # Add the legend
        if i == 4:
            patches = [
                mpatches.Patch(color=color, label=key) for (key, color) in colors_dict.items()
            ]
            ax.legend(handles=patches, bbox_to_anchor=(1, 0.5), loc="center left")

  

   

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add the legend
    patches = [mpatches.Patch(color=color, label=key) for (key, color) in colors_dict.items()]
    ax.legend(handles=patches, bbox_to_anchor=(1, 0.5), loc="center left")

    # TODO: Calculate the sort of timescale we're plotting and choose appropriate limits
    # Format the x-ticks
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=100))
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter(
            "%b %d %H:%M",
            # "%H:%M:%S.%f",
        )
    )

    # TODO: Calculate the sort of timescale we're plotting and choose appropriate limits
    # Set the x axis limits
    # ax.set_xlim(
    #     df.start_date.min() - np.timedelta64(10, "s"),
    #     df.end_date.max() + np.timedelta64(10, "s"),
    # )

    # Format the y-ticks
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories)

    ax.grid(True, axis="x", linestyle="--", linewidth=0.45, alpha=0.2, color="grey")
    ax.tick_params(axis="x", which="both", direction="out", rotation=30)

    print("Saving figure")

    fig.suptitle("3D_UNet PyTorch Image Segmentation")

    if outname is not None:
        filename = outname
    else:
        filename = "timelines/cpu_timeline"

    plt.savefig(f"./plots/{filename}.png", format="png", dpi=600)
def plot_thread(pid):

    fig, ax = plt.subplots(figsize=(20, 6))

    df = pd.read_csv(
        f"data/st_end_data/st_end_data_{pid.split('_')[0]}",
        names=["start_date", "end_date", "event"],
    )
    df = df[["start_date", "end_date", "event"]]
    df.start_date = pd.to_datetime(df.start_date).astype(np.datetime64)
    df.end_date = pd.to_datetime(df.end_date).astype(np.datetime64)

    print(df.shape)

    bar_height = 1
    colors_dict = dict(
        OPENAT="purple",
        VFSOPEN="slateblue",
        VFSR="dodgerblue",
        VFSW="red",
        BIOR="darkorange",
        BIOW="red",
    )

    ymins = [0, 1, 2]
    categories = ["BIO", "VFS", "OPEN"]
    masks = {
        "BIO": (df["event"] == "BIOR") | (df["event"] == "BIOW"),
        "OPEN": (df["event"] == "OPENAT") | (df["event"] == "VFSOPEN"),
        "VFS": (df["event"] == "VFSR") | (df["event"] == "VFSW"),
    }

    # Plot the events
    for i, category in enumerate(categories):
        mask = masks[category]
        #print(mask)
        start_dates = mdates.date2num(df.loc[mask].start_date)
        print(start_dates)
        end_dates = mdates.date2num(df.loc[mask].end_date)
        durations = end_dates - start_dates
        xranges = list(zip(start_dates, durations))
        ymin = ymins[i] - 0.5
        yrange = (ymin, bar_height)
        colors = [colors_dict[event] for event in df.loc[mask].event]
        ax.broken_barh(xranges, yrange, facecolors=colors, alpha=1)
        # you can set alpha to 0.6 to check if there are some overlaps

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Specific formatting for each pid
    # Default formatting
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter(
            "%b%d",
        )
    )
    ax.xaxis.set_minor_locator(mdates.AutoDateLocator(maxticks=100))
    ax.xaxis.set_minor_formatter(
        mdates.DateFormatter(
            "%H:%M:%S",
        )
    )

    print(df.start_date.min())
    print(df.start_date.max())
        # Set the limits
    ax.set_xlim(
        df.start_date.min() - np.timedelta64(5, "m"),
        df.start_date.max() + np.timedelta64(5, "m"),
    )

    ax.grid(True, axis="x", which="minor", linestyle="--", linewidth=0.45)
    ax.tick_params(
        axis="x", which="both", direction="in", grid_color="grey", grid_alpha=0.2, rotation=30
    )
    ax.tick_params(axis="x", which="major", labelsize=12)
    ax.tick_params(axis="x", which="minor", labelsize=8)


    # Format the y-ticks
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories)

    # Add the legend
    patches = [mpatches.Patch(color=color, label=key) for (key, color) in colors_dict.items()]
    ax.legend(handles=patches, bbox_to_anchor=(1, 0.5), loc="center left")

    ax.set_title(pid)

    plt.savefig(f"./plots/timelines/{pid}.png", format="png", dpi=500)

def generate_all_indiv_thread_plots():
    #pids = ["2744156","2744477","2744518","2744799","2744839","2745385","2745425","2745824","2745888",
    #"2747135","2747207","2748968","2749075","2751145","2751341","2751866","2751908","2752207","2752291",
    #"2752824","2752949","2753573","2753710","2754153","2754193",
    #"2754558","2754598","2754994","2755047","2755448","2755488","2755764","2755804"]
    for pid in pids:
        plot_thread(pid)

if __name__ == "__main__":
    #plot_pids_timeline_cpu(outname="timelines/all_c")
    plot_pids_timeline_cpu(outname="timelines1/all",start="2022-03-31T17:05:00",
        end="2022-03-31T17:17:10",)
    plot_pids_timeline_cpu(outname="timelines1/all_f1",start="2022-03-31T17:05:00",
        end="2022-03-31T17:06:00",)
    plot_pids_timeline_cpu(outname="timelines1/all_f2",start="2022-03-31T17:05:00",
        end="2022-03-31T17:07:00",)
    plot_pids_timeline_cpu(outname="timelines1/all_f5",start="2022-03-31T17:05:00",
        end="2022-03-31T17:10:00",)
    plot_pids_timeline_cpu(outname="timelines1/all_l1",start="2022-03-31T17:16:10",
        end="2022-03-31T17:17:10",)
    plot_pids_timeline_cpu(outname="timelines1/all_l2",start="2022-03-31T17:15:10",
        end="2022-03-31T17:17:10",)
    plot_pids_timeline_cpu(outname="timelines1/all_l5",start="2022-03-31T17:12:10",
        end="2022-03-31T17:17:10",)
    #generate_all_indiv_thread_plots()
