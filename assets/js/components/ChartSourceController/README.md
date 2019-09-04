# ChartSourceController


## Overview
A wrapper component that accepts all `BarChart` props and also a `toggle` prop. 


## Notes
- All `BarChart` props are passed along to a `BarChart` component.
- If a toggle object is passed the component assumes that a user should be able between different sources for the chart 
- All root level keys present in the `toggle` object should correspond to specific root level keys in the `items` object.
- If that option is selected via the radio buttons the values in the corresponding key inside `items` will be fed to the `BarChart`.


## Props
- `items`: The data that should be passed to th `BarChart` component. See `BarChart` documentation for more info on this prop.
- `toggle`: An object that enables the toggling between sources. The root level keys should correspond to root level keys in `items`.
- `toggle[key].title`: The label that should be shown next to the radio button.
- `toggle[key].description`: A descritpion that should be shown under the radio buttons of the specific `key` is selected.
- `styling`: All styling options that should be applied to the chart.
- `styling.scale`: See `BarChart` component for more details.
- `styling.rotated`: See `BarChart` component for more details.
- `styling.color`: See `BarChart` component for more details.
- `intial`: Sets the initial key in `items` and `toggle` that should be selected.


## Example
```jsx
const items = {
  noHeadings: {
    example1: 10,
    example2: 20,
    example3: 100,
  }
  withHeading: {
    noHundred: {
      example1: 10,
      example2: 20,
    },
    hundred: {
      example3: 100,
    }
  }
}

const toggle = {
  noHeading: {
    title: 'Without Headings',
    description: 'Note there are currently hidden heading, select \'With Headings\' to show them',
  }
  headings: {
    title: 'With Headings'
  }
}

<ChartSourceController {...{ items, toggle, styling }} default="headings" />
```