# LinksList

## Overview

A list of actionable links usually associated with a piece of UI directly above or below it. Requires an icon from the `components/Icon` Jekyll include for each link if implemented via Jekyll.

## Jekyll Implementation

## Props (for React Implementation)

- `listArray`: Pass an array of objects. Each objecft represents an link item. All properties in obhects are requred, and are as follows:
  - `listArray.id`: Used in React to create `key` attribute
  - `listArray.title`: The text that will be used to show the link (that user will click on)
  - `listArray.prefex`: A string that will be prefixed before the link text (however after the icon). Useful when you want to provide more information about the link.
  - `listArray.link`: A string that will be used in the `href` attribute of the link.
  - `listArray.type`: The type will determine what icon will be added to link (currently supports all icons in the `components/Icons` component).

## Examples

### Basic React Example

```jsx
const example = [
  {
    id: 'dataset',
    title: 'View Dataset',
    prefix: 'Source',
    link: '/dataset',
    type: 'dataset',
  },
  {
    id: 'google',
    title: 'Go to Google.com',
    link: '//google.com',
    type: 'guide',
  },
  {
    id: 'pdf',
    title: 'Download PDF',
    link: '/assets/file.pdf',
    type: 'download',
  },
];

<LinksList listArray={example} />
```

### Basic Jekyll Example

```html
<ul class="LinksList">
  {%
    include components/LinksList/item.html
    prefix="Source"
    text="View Dataset"
    url="/dataset"
    type="dataset"
  %}

  {%
    include components/LinksList/item.html
    text="Go to Google.com"
    url="//google.com"
    type="guide"
  %}

  {%
    include components/LinksList/item.html
    text="Download PDF"
    url="/assets/file.pdf"
    type="download"
  %}
</ul>
```