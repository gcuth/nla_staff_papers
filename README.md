# NLA Staff Papers

This python script extracts the [NLA Staff Papers list](https://www.nla.gov.au/our-publications/staff-papers) and outputs it as a json file.

It supports both a sensible default (running `./scrape.py` alone), along with custom optional arguments for `--outpath` and `--url`. It's written in a functional style.

## Setup

To ensure your python environment meets requirements, run:

```sh
pip install -r requirements.txt
```

## Usage

To download, run:

```sh
python ./scrape.py
```

By default, this will save a datestamped `.json` file into the present directory, and will also echo the results to console.

To silence console output:

```sh
python ./scrape.py --silent
```

To set a custom outpath:

```sh
python ./scrape.py --outpath [/your/chosen/path.json]
```
