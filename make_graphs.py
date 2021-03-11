import plotly.io as io
from pathlib import Path

folder_path = Path('/Users/mattgilbert/Documents/UBIcenter/ubicenter.org/assets/markdown_assets/2021-01-18_racial_poverty_disparities_mlk_day_2021')

import pandas as pd
import numpy as np
import microdf as mdf
import plotly.express as px

SPM_COLS = [
    "spm_" + i for i in ["id", "weight", "povthreshold", "resources", "numper"]
]
raw = pd.read_csv(
    "https://github.com/MaxGhenis/datarepo/raw/master/pppub20.csv.gz",
    usecols=["PRDTRACE", "MARSUPWT", "AGI"] + [i.upper() for i in SPM_COLS],
)
person = raw.copy(deep=True)
person.columns = person.columns.str.lower()
person["weight"] = person.marsupwt / 100
person.spm_weight /= 100
person = person.rename(columns={"prdtrace": "race"})
# Add indicators for white only and black only (not considering other races).
person["white"] = person.race == 1
person["black"] = person.race == 2
# Limit to positive AGI.
person["agi_pos"] = np.maximum(person.agi, 0)
# Need total population to calculate UBI and total AGI for required tax rate.
total_population = person.weight.sum()
total_agi = mdf.weighted_sum(person, "agi_pos", "weight")
# Sum up AGI for each SPM unit and merge that back to person level.
spm = person.groupby(SPM_COLS)[["agi_pos", "white", "black"]].sum()
spm.columns = ["spm_" + i for i in spm.columns]
# Merge these back to person to calculate population in White and Black spmus.
person = person.merge(spm, on="spm_id")
pop_in_race_spmu = pd.Series(
    {
        "Black": person[person.spm_black > 0].weight.sum(),
        "White": person[person.spm_white > 0].weight.sum(),
    }
)
spm.reset_index(inplace=True)


def pov_gap(df, resources, threshold, weight):
    # df: Should be SPM-unit level.
    gaps = np.maximum(df[threshold] - df[resources], 0)
    return (gaps * df[weight]).sum()


def pov(race, monthly_ubi):
    # Total cost and associated tax rate.
    cost = monthly_ubi * total_population * 12
    tax_rate = cost / total_agi
    # Calculate new tax, UBI and resources per SPM unit.
    spm["new_spm_resources"] = (
        spm.spm_resources - 
        (tax_rate * spm.spm_agi_pos) +  # New tax
        (12 * monthly_ubi * spm.spm_numper))  # UBI
    # Merge back to person.
    person2 = person.merge(spm[["spm_id", "new_spm_resources"]], on="spm_id")
    # Based on new resources, calculate
    person2["new_poor"] = person2.new_spm_resources < person2.spm_povthreshold
    # Calculate poverty rate for specified race.
    poverty_rate = mdf.weighted_mean(
        person2[person2[race.lower()]], "new_poor", "weight"
    )
    # Calculate poverty gap for specified race.
    poverty_gap = pov_gap(
        spm[spm["spm_" + race.lower()] > 0], "new_spm_resources",
        "spm_povthreshold", "spm_weight"
    )
    poverty_gap_per_capita = (poverty_gap / pop_in_race_spmu[race])

    return pd.Series({
        "poverty_rate": poverty_rate,
        "poverty_gap_per_capita": poverty_gap_per_capita
    })


def pov_row(row):
    return pov(row.race, row.monthly_ubi)


summary = mdf.cartesian_product(
    {"race": ["White", "Black"], "monthly_ubi": np.arange(0, 1001, 50)}
)
summary = pd.concat([summary, summary.apply(pov_row, axis=1)], axis=1)
# Format results.
summary.poverty_rate = 100 * summary.poverty_rate.round(3)
summary.poverty_gap_per_capita = summary.poverty_gap_per_capita.round(0)
wide = summary.pivot_table(
    ["poverty_rate", "poverty_gap_per_capita"], "monthly_ubi", "race"
)
wide.columns = ["pg_black", "pg_white", "pr_black", "pr_white"]
wide["pg_ratio"] = (wide.pg_black / wide.pg_white).round(2)
wide["pr_ratio"] = (wide.pr_black / wide.pr_white).round(2)
wide.reset_index(inplace=True)
ratios = wide.melt(id_vars="monthly_ubi", value_vars=["pr_ratio", "pg_ratio"])
# Change for chart.
ratios.variable.replace({"pr_ratio": "Poverty rate",
                         "pg_ratio": "Poverty gap per capita"},
                        inplace=True)


def add_ubi_center_logo(fig, x=0.98, y=-0.14):
    fig.add_layout_image(
        dict(
            source="https://raw.githubusercontent.com/UBICenter/blog/master/jb/_static/ubi_center_logo_wide_blue.png",
            # See https://github.com/plotly/plotly.py/issues/2975.
            # source="../_static/ubi_center_logo_wide_blue.png",
            xref="paper", yref="paper",
            x=x, y=y,
            sizex=0.12, sizey=0.12,
            xanchor="right", yanchor="bottom"
        )
    )


def line_graph(
    df,
    x,
    y,
    color,
    title,
    xaxis_title,
    yaxis_title,
    color_discrete_map,
    yaxis_ticksuffix,
    yaxis_tickprefix,
):
    """Style for line graphs.
    
    Arguments
    df: DataFrame with data to be plotted.
    x: The string representing the column in df that holds the new spending in billions.
    y: The string representing the column in df that holds the poverty rate.
    color: The string representing the UBI type.
    xaxis_title: The string represnting the xaxis-title.
    yaxis_title: The string representing the yaxis-title.
    
    Returns
    Nothing. Shows the plot.
    """
    fig = px.line(
        df, x=x, y=y, color=color, color_discrete_map=color_discrete_map
    )
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        yaxis_ticksuffix=yaxis_ticksuffix,
        yaxis_tickprefix=yaxis_tickprefix,
        font=dict(family="Roboto"),
        hovermode="x",
        xaxis_tickprefix="$",
        plot_bgcolor="white",
        legend_title_text="",
        height=600,
        width=1000,
    )

    fig.update_layout(
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.9)
    )

    fig.update_traces(mode="markers+lines", hovertemplate=None)
    
    add_ubi_center_logo(fig)

    return fig
    

DARK_BLUE = "#1565C0"
GRAY = "#9E9E9E"
DARK_GREEN = "#388E3C"
LIGHT_GREEN = "#66BB6A"
CONFIG = {"displayModeBar": False}

fig = line_graph(
    df=summary,
    x="monthly_ubi",
    y="poverty_rate",
    color="race",
    title="Black and White poverty rate by UBI amount",
    xaxis_title="Monthly universal basic income funded by flat income tax",
    yaxis_title="SPM poverty rate (2019)",
    color_discrete_map={"White": GRAY, "Black": DARK_BLUE},
    yaxis_ticksuffix="%",
    yaxis_tickprefix="",
)
io.write_html(fig, str(folder_path.joinpath('2021-01-18-racial-poverty-disparities-mlk-day-2021-graph-1.html')), full_html = False, include_plotlyjs = False, config = {'displayModeBar': False})

fig = line_graph(
    df=summary,
    x="monthly_ubi",
    y="poverty_gap_per_capita",
    color="race",
    title="Black and White poverty gap per capita by UBI amount",
    xaxis_title="Monthly universal basic income funded by flat income tax",
    yaxis_title="Poverty gap per capita (2019)",
    color_discrete_map={"White": GRAY, "Black": DARK_BLUE},
    yaxis_ticksuffix="",
    yaxis_tickprefix="$",
)
io.write_html(fig, str(folder_path.joinpath('2021-01-18-racial-poverty-disparities-mlk-day-2021-graph-2.html')), full_html = False, include_plotlyjs = False, config = {'displayModeBar': False})

fig = line_graph(
    df=ratios,
    x="monthly_ubi",
    y="value",
    color="variable",
    title="Black poverty relative to White poverty by UBI amount",
    xaxis_title="Monthly universal basic income funded by flat income tax",
    yaxis_title="Ratio of Black to White poverty measure (2019)",
    color_discrete_map={"Poverty rate": LIGHT_GREEN,
                        "Poverty gap per capita": DARK_GREEN},
    yaxis_ticksuffix="",
    yaxis_tickprefix="",
)
fig.add_hline(1, line_dash="dot")
io.write_html(fig, str(folder_path.joinpath('2021-01-18-racial-poverty-disparities-mlk-day-2021-graph-3.html')), full_html = False, include_plotlyjs = False, config = {'displayModeBar': False})

