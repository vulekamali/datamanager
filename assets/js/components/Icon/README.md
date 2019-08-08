---
title: Icon
category: Universal Components
assets: examples
state:
  text: ✔ stable
  color: white
  background: green
API:
  text: HTML / Preact / Jekyll
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

## Overview

A lowel-level component that is used to create Icons.

- Usually used inside other components.
- Icons are always contained in a square (equal height and width) SVG. This makes resizing easier.
- Never set the fill or stroke colour in the component itself, it should inherit fill and stroke colours of it's parent.
- On non-evergreen browsers icon will not be converted to `block` elements, and rather retain the default `inline` box modal. This is done to enable icons to be centered without flexbox inside the `Button` component.

## Examples

### Basic
<iframe width="100%" height="315" src="basic.html" frameborder="0" allowfullscreen></iframe>
[View Example](basic.html)

<iframe width="100%" height="315" src="code-basic.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-basic.html)

### Small

<iframe width="100%" height="315" src="small.html" frameborder="0" allowfullscreen></iframe>
[View Example](basic.html)

<iframe width="100%" height="315" src="code-small.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-basic.html)

### Large

<iframe width="100%" height="315" src="large.html" frameborder="0" allowfullscreen></iframe>
[View Example](large.html)

<iframe width="100%" height="315" src="code-large.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-large.html)

## API

### HTML via CSS classes

#### `.Icon`
| Modifier | Description |
|---|---|
| `.is-small` | Changes the width and height of the icon from the default 18px's to 16px. |
| `.is-large` | Changes the width and height of the icon from the default 18px's to 24px. |

### Preact Component
| Prop | Description |
|---|---|
| `size` | String that changes the width and height of the icon. Only accepts `small` and `large`. |
| `type` | String that determines the icon that will be rendered. Only accepts  `download`, `facebook`, `search`, `twitter`, `close`, `play`, `pin`, `date`, `hamburger` or `home`. |

### Jekyll via an include
Use exact same API as Preact, by passing props as variables inside an include. For example: `{% include component/Icon/index.html type="facebook" %}`.

## Support

| Browser | Enhancement |
|---|---|
| IE 5 | No support |
| IE 9 | Complete support for icons, however due to the absence of flexbox icons might have a couple of pixels of padding below them depending on the size of line-height (Base Support) |
| Evergreen browsers | No extra padding around icon |