# chartAdaptor


## Overview
JavaScript function bound to a DOM node with `data-component="chartAdaptor"` that normalises data supplied (based on what is passed to `data-type` attribute) before it is passed to the `ChartSourceController` component.


## Notes
- See the `index.text.js` Jest test files for each normalisation script in the services folder to see what the expected input and out ouput of each normalisation function is.


## Props
- `type`: String that determines how data passed is normalised.
- `items`: The raw data that should be normalised.
- `scale`: A number indicating the visual importance a chart should have based on the size of important elements in it. Useful for indicating the most important charts on a page.
- `color`: A hex value that overrides the default `#7bb344` colour of chart.
