# BarChart


## Overview
Displays either a horizontal or vertical bar chart from the ChartJS (https://www.chartjs.org/) library.


## Notes
- Includes button that converts and downloads the chart as a PNG. See the `downloadChart` service for more information.
- Normalises the object passed to `items` into a scheme that ChartJS accepts. Default ChartJS schema is not exposed directly due to the implimentation of headings and labels inside the bar charts, which is not included by default by ChartJS and required some abstractions over ChartJS.
- Returns a node via the React ref attribute to run ChartJS against since ChartJS requires a DOM node as input.


## Props
- `items`: The data that will be presented in the bar chart. Accepts an object. Root level keys will be used as labels for each bar and the associated values will be used as the value of that bar. However, note that, if there is a second level of nesting in the `items` object, then the root level will **instead** be rendered as headings and keys passed to the object of the root level key will rather be the labels (and the nested object's value will be the bar values)
- `color`: Accepts a hex colour that overrides the default `#7bb344` color.
- `rotated`: If true, then chart then bars ascend upwards instead of the default sideways (from left to right)
- `scale`: Bars are 20px wide by default (width, not length), however if a value is passed to `scale` the 20px is multiplied by `scale` to determine a new value. Usefuly when you want to indicate that some charts are more important than others.


## Examples


### Basic Example
```jsx
const items = {
  example1: 10,
  example2: 20,
  example3: 100,
};

<ChartSourceController {...{ items }} />
```


### With Modifiers Example
```jsx
const items = {
  example1: 10,
  example2: 20,
  example3: 100,
};

<ChartSourceController color="#00ff22" scale="3" rotated {...{ items }} />
```


### With Headings
```jsx
const items = {
  noHundred: {
    example1: 10,
    example2: 20,
  },
  hundred: {
    example3: 100,
  }
};


<ChartSourceController {...{ items }} />
```