---
title: Page
category: Universal Components
assets: examples
state:
  text: ✔ stable
  color: white
  background: green
API:
  text: HTML
  color: black
  background: '#CCCCCC'
support:
  text: IE 9
  color: white
  background: grey
---

## Table of Contents
- [Overview](#overview)
- [Examples](#examples)
- [API](#api)
- [Support](#support)

## Overview

- The `Page` component will always be the highest level component on a page.
- It controls the behaviour and positioning of the header, footer, content and sidebar areas.
- In order to impliment what is known as the 'holy-grail layout', i.e. footer always sits at the bottom of the viewport, even when there is not sufficient content to push it down (https://en.wikipedia.org/wiki/Holy_grail_(web_design), `display: table` is used.
- However in order to avoid buggy behaviour (when detecting the width of HTML nodes) and since mobile viewports almost always fill the entire viewport with content, the above only triggers on tablet viewport sizes.
- The sidebar will always collapse under the main content on viewports smaller than widescreen (1050px).

## Examples

### Basic
<iframe style="resize: horizontal;" width="100%" height="315" src="basic.html" frameborder="0" allowfullscreen></iframe>
[View Example](basic.html)

<iframe width="100%" height="315" src="code-basic.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-basic.html)

### Sidebar
<iframe style="resize: horizontal;" width="100%" height="315" src="sidebar.html" frameborder="0" allowfullscreen></iframe>
[View Example](sidebar.html)

<iframe width="100%" height="315" src="code-sidebar.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-sidebar.html)

### Full Page
<iframe style="resize: horizontal;" width="100%" height="315" src="full.html" frameborder="0" allowfullscreen></iframe>
[View Example](full.html)

<iframe width="100%" height="315" src="code-full.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-full.html)


## API

### HTML via CSS classes

#### `.Page-contentInner`

| CSS | Description |
|---|---|
| `.is-full` | Modifies the page container width from the default `1024` to `1800`. This is useful when you want to factor very widescreen viewports into your page layout |

## Support

| Browser | Enhancement |
|---|---|
| IE 5 | Media queries and `max-width` are not supported so sidebar will collapse under content and site will stretch all the way to width of the screen (Partial support) |
| IE 9 | Optimal Support |