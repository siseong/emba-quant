"""Reproduce Guo (2025), Tables 2, 4 and A3, with Harvard Dataverse v1.0."""
import argparse
import csv
import hashlib
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import statsmodels.api as sm


BASE_URL = "https://dataverse.harvard.edu/api/access/datafile/"
FILES = {
    "market.dta": (
        "10802963?format=original",
        "d2ed98ee2b1b35d44742a3dbd1b35477cb3e430ee4418d637b20666eda6f0a42",
    ),
    "strategy.tab": (
        "10802956", "406dc2382c91fa94441351412f23d30e9963641c9ded41cfafad81961acef6d0"
    ),
    "factors.tab": (
        "10802965", "35e03db78c813e460a33a3026f4869bf2f82ee315d6c39c48298e6571be0f20a"
    ),
    "table2_expected.csv": (
        "10802952", "e0976080e08ece658e5c8785e33e180f4f29f6b1a5e74c00e2cf9dcf56eb936c"
    ),
    "table_a3_expected.csv": (
        "10802959", "58c389dbeb17859659bee9f8df9c5fcc25843a65be44fdaf3aa9edb83fe7542e"
    ),
}
TABLE4_EXPECTED = [0.49, 3.72, 3.60, 3.68, 3.97, 3.77, 3.82, 4.30]


def prepare_inputs(directory):
    directory.mkdir(parents=True, exist_ok=True)
    for filename, (remote_id, checksum) in FILES.items():
        path = directory / filename
        if path.is_file():
            with path.open("rb") as source:
                if hashlib.file_digest(source, "sha256").hexdigest() == checksum:
                    continue
        payload = subprocess.check_output(
            ["curl", "-fLsS", "--retry", "2", "--max-time", "60", BASE_URL + remote_id]
        )
        if hashlib.sha256(payload).hexdigest() != checksum:
            raise ValueError(f"Unexpected Dataverse content for {filename}")
        path.write_bytes(payload)


def monthly(frame, dates):
    frame.index = pd.PeriodIndex(dates, freq="M", name="month")
    frame = frame.sort_index()
    complete = pd.period_range(frame.index[0], frame.index[-1], freq="M")
    if not frame.index.equals(complete):
        raise ValueError("Input months must be unique and consecutive")
    return frame


def newsy_lags(returns):
    # The row is formation month t; the forecast is for month t+1.
    # At quarter-opening month-end, include that month's realized return.
    age = (returns.index.month - 1) % 3
    return pd.DataFrame({
        f"q{quarter + 1}": returns.shift(3 * quarter).where(
            age == 0, returns.shift(3 * quarter + 1).where(
                age == 1, returns.shift(3 * quarter + 2)
            )
        )
        for quarter in range(4)
    })


def is_next_month_newsy(index):
    return pd.Series((index + 1).month % 3 == 1, index=index, name="am")


def robust_ols(y, predictors):
    design = predictors.assign(const=1.0)
    return sm.OLS(y, design, missing="drop").fit(cov_type="HC1")


def table2(path):
    frame = pd.read_stata(path)
    frame = monthly(frame, frame["date"])
    returns = frame["vwretd"]
    target = returns.shift(-1)
    newsy = is_next_month_newsy(frame.index)
    lags = newsy_lags(returns)
    interactions = lags.mul(newsy, axis=0).add_suffix("_x_am")
    return [
        robust_ols(target, lags),
        robust_ols(target[newsy], lags[newsy]),
        robust_ols(target[~newsy], lags[~newsy]),
        robust_ols(target, lags.join(interactions).join(newsy.astype(float))),
    ]


def expanding_ols(signal, target, include):
    # target at row s is realized in s+1, so train only on rows s < t.
    # Mask the pair jointly before computing expanding sample moments.
    valid = include & signal.notna() & target.notna()
    x, y = signal.where(valid), target.where(valid)
    mean_x, mean_y = x.expanding().mean(), y.expanding().mean()
    variance = x.expanding().var(ddof=0)
    covariance = (x * y).expanding().mean() - mean_x * mean_y
    slope = covariance / variance.where(variance > 0)
    return slope.shift(1), (mean_y - slope * mean_x).shift(1)


def forecasts(returns):
    target = returns.shift(-1)
    newsy = is_next_month_newsy(returns.index)
    total = newsy_lags(returns).sum(axis=1, min_count=4)
    direction = 1 - 2 * newsy
    raw_signal = total * direction
    signal = (total - total.expanding().mean().shift(1)) * direction
    # The published script starts its expanding regressions six months after
    # the first formation month with a raw signal and a next-month return.
    first_fit = (raw_signal.notna() & target.notna()).idxmax() + 6
    slope, intercept = expanding_ols(signal, target, pd.Series(True, index=returns.index))
    slope_am, intercept_am = expanding_ols(signal, target, newsy)
    slope_other, intercept_other = expanding_ols(signal, target, ~newsy)
    raw_am, raw_intercept_am = expanding_ols(raw_signal, target, newsy)
    raw_other, raw_intercept_other = expanding_ols(raw_signal, target, ~newsy)

    split_slope = slope_am.where(newsy, slope_other)
    split_intercept = intercept_am.where(newsy, intercept_other)
    split_mean = target.where(newsy).expanding().mean().shift(1).where(
        newsy, target.where(~newsy).expanding().mean().shift(1)
    )
    output = pd.DataFrame({
        "raw_split": raw_signal * raw_am.where(newsy, raw_other)
        + raw_intercept_am.where(newsy, raw_intercept_other),
        "split_ols": signal * split_slope + split_intercept,
        "split_mean": signal * split_slope + split_mean,
        "split_component": signal * split_slope,
        "pooled_ols": signal * slope + intercept,
        "pooled_component": signal * slope,
    })
    output.loc[output.index < first_fit] = np.nan
    output["historical_mean"] = returns.expanding().mean()
    output["pooled_mean"] = output["historical_mean"] + output["pooled_component"]
    output["next_return"] = target
    output["newsy_next_month"] = newsy
    output["signal"] = signal
    return output


def table4(forecast, inputs):
    payout = inputs["de"].expanding().mean()
    roe = inputs["roe"].expanding().mean()
    growth = (1 - payout) * roe
    dp = (inputs["d"] / inputs["p"] + growth) / 12
    ep = (inputs["e"] / inputs["p"] * payout + growth) / 12
    bm = roe * (1 + payout * (inputs["bm"] - 1)) / 12
    valuation = (dp + ep + bm) / 3
    methods = pd.DataFrame({
        0: valuation,
        1: forecast["raw_split"],
        2: forecast["split_ols"],
        3: forecast["split_mean"],
        4: forecast["split_component"] + valuation,
        5: forecast["pooled_ols"],
        6: forecast["pooled_mean"],
        7: forecast["pooled_component"] + valuation,
    })
    actual = forecast["next_return"]
    benchmark = forecast["historical_mean"]
    sample = (methods.index >= "1926-01") & actual.notna() & methods.notna().all(axis=1)
    tss = ((actual[sample] - benchmark[sample]) ** 2).sum()
    r2 = 100 * (1 - methods[sample].sub(actual[sample], axis=0).pow(2).sum() / tss)
    return r2, methods.loc[sample].index


def table_a3(forecast, factor_path):
    factors = pd.read_csv(factor_path, sep="\t")
    factors = monthly(factors, factors.pop("ym")).reindex(forecast.index)
    # Original factor file is in monthly percent. Date factors by holding month.
    factors = factors.join(forecast[["pooled_component", "next_return"]])
    next_factors = factors[["mktrf", "hml", "smb", "mom"]].shift(-1)
    raw_return = factors["pooled_component"] * factors["next_return"]
    scale = factors["mktrf"].std() / raw_return.std()
    portfolio = (raw_return * scale).rename("strategy_return_pct")
    window = slice("1926-10", "2021-05")
    results = [
        robust_ols(portfolio.loc[window], next_factors.iloc[:, :count].loc[window])
        for count in (0, 1, 3, 4)
    ]
    returns = portfolio.to_frame().join(next_factors.add_prefix("next_"))
    returns["holding_month"] = returns.index + 1
    return results, returns, scale


def regression_comparison(table, models, expected_path, names):
    with expected_path.open(newline="") as source:
        rows = csv.reader(source)
        metrics = []
        variable = None
        for row in rows:
            if len(row) != 5:
                continue
            label, *values = [cell.removeprefix('="').removesuffix('"') for cell in row]
            if label in names:
                variable, statistic = label, "coef"
            elif label in {"N", "R-sq"}:
                variable, statistic = label, label
            elif not label and any(value.startswith("[") for value in values):
                statistic = "t"
            else:
                continue
            for column, (value, model) in enumerate(zip(values, models), 1):
                if not value:
                    continue
                if statistic == "N":
                    actual, digits = model.nobs, 0
                elif statistic == "R-sq":
                    actual, digits = model.rsquared, 3
                elif statistic == "coef":
                    actual, digits = model.params[names[variable]], 3
                else:
                    actual, digits = model.tvalues[names[variable]], 2
                expected = float(value.strip("[]*"))
                metrics.append(compare(table, column, variable, statistic, actual, expected, digits))
    return metrics


def compare(table, column, variable, metric, actual, expected, digits):
    return {
        "table": table, "column": column, "variable": variable, "metric": metric,
        "actual": actual, "expected": expected, "difference": actual - expected,
        "match": bool(np.isfinite(actual) and round(actual, digits) == expected),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    input_dir = args.work_dir / "input"
    output_dir = args.work_dir / "output"
    prepare_inputs(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = pd.read_csv(input_dir / "strategy.tab", sep="\t").dropna(how="all")
    inputs.columns = inputs.columns.str.lower()
    dates = pd.to_datetime(inputs.pop("date").astype(int), format="%Y%m")
    inputs = monthly(inputs, dates)
    forecast = forecasts(inputs["vwretd"].fillna(inputs["ret_gfd"]))
    r2, sample = table4(forecast, inputs)
    alpha, returns, scale = table_a3(forecast, input_dir / "factors.tab")
    table2_names = {
        **{f"vwretd_prevq1_l{i}q": f"q{i}" for i in range(1, 5)},
        **{f"vwretd_prevq1_l{i}q_x_am1": f"q{i}_x_am" for i in range(1, 5)},
        "am1_flag": "am", "_cons": "const",
    }
    a3_names = {**{f"{v}_f1m": v for v in ["mktrf", "hml", "smb", "mom"]}, "_cons": "const"}
    checks = regression_comparison(
        "2", table2(input_dir / "market.dta"), input_dir / "table2_expected.csv", table2_names
    )
    checks += [compare("4", i, "forecast", "oos_r2_pct", r2[i], ref, 2)
               for i, ref in enumerate(TABLE4_EXPECTED)]
    checks += regression_comparison("A3", alpha, input_dir / "table_a3_expected.csv", a3_names)
    comparison = pd.DataFrame(checks)
    if comparison.groupby("table").size().to_dict() != {"2": 58, "4": 8, "A3": 32}:
        raise ValueError("Unexpected number of reference cells")
    comparison.to_csv(output_dir / "comparison.csv", index=False)
    forecast.join(returns).to_csv(output_dir / "monthly.csv")
    print(f"Table 4 formation months: {sample[0]} to {sample[-1]} (N={len(sample)})")
    print(f"Table A3 volatility scale: {scale:.8f}")
    print(comparison.groupby("table")["match"].agg(["sum", "size"]).to_string())
    mismatches = comparison.loc[~comparison["match"]]
    if not mismatches.empty:
        print(mismatches.to_string(index=False))
    return int(not mismatches.empty)


if __name__ == "__main__":
    raise SystemExit(main())
