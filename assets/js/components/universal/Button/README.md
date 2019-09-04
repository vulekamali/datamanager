---
title: Button
category: Universal Components
assets: examples
state:
  text: ✘ unstable (support + is-loading + js hook)
  color: black
  background: yellow
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

- Buttons indicate an action a user can perform.
- Class can be used on either `<a>` or `<button>` tags. Generally a-tags are used for links to pages and button-tags modify the state of the current page.
- The theming of the button, either primary (the default) or secondary, guides the user to what is perceived to be the next logical action.
- Buttons should always incate clearly what will happen once clicked. Either when read in combination with it's header or in the button itself. Prefer phrases like 'Sign up for our newsletter' or 'Show all departments' above phrases like 'Stay informed' or 'Explore more departments'.

## Examples

### Basic
<iframe width="100%" height="100" src="basic.html" frameborder="0" allowfullscreen></iframe>
[View Example](basic.html)

<iframe width="100%" height="100" src="code-basic.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-basic.html)

### Page Transition Animation
<iframe width="100%" height="100" src="loader.html" frameborder="0" allowfullscreen></iframe>
[View Example](loader.html)

<iframe width="100%" height="100" src="code-loader.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-loader.html)

### Small
<iframe width="100%" height="100" src="small.html" frameborder="0" allowfullscreen></iframe>
[View Example](small.html)

<iframe width="100%" height="100" src="code-small.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-small.html)

### Multiple Lines
<iframe width="100%" height="100" src="multiline.html" frameborder="0" allowfullscreen></iframe>
[View Example](multiline.html)

<iframe width="100%" height="100" src="code-multiline.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-multiline.html)

### Inline
<iframe width="100%" height="100" src="inline.html" frameborder="0" allowfullscreen></iframe>
[View Example](inline.html)

<iframe width="100%" height="100" src="code-inline.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-inline.html)

### Icon and text
<iframe width="100%" height="100" src="icon.html" frameborder="0" allowfullscreen></iframe>
[View Example](icon.html)

<iframe width="100%" height="100" src="code-icon.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-icon.html)

### Only an icon
<iframe width="100%" height="100" src="icononly.html" frameborder="0" allowfullscreen></iframe>
[View Example](icononly.html)

<iframe width="100%" height="100" src="code-icononly.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-icononly.html)

### Invisible
<iframe width="100%" height="100" src="invisible.html" frameborder="0" allowfullscreen></iframe>
[View Example](invisible.html)

<iframe width="100%" height="100" src="code-invisible.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-invisible.html)

## API

### HTML via CSS classes

#### `.Button`
| Modifier | Description |
|---|---|
| `.is-secondary` | Applies a white background and dark grey colors to the button. Useful when a call to action needs to sit lower in the visual hierarchy than a primary call/s to action (default button state) |
| `.is-small` | Decreases padding and font-size down to `13px`. Useful when default button size seems too big in proportion to it's surrounding elements. Do not use small to indicate secondary call to actions, rather rely on the `is-secondary` modifier |
| `.is-inline` | By default buttons are rendered as block level elements. This enables a parent HTML element to control the width of the button while keeping buttons encapsulated from their parents |
| `.is-invisible` | Removes visual styling from button, however retains underlying structure and hover effect. This is useful if you want to create a clickable element, but do not want it to call attention as a call to action |
| `.is-circle` | Forces the width and the width and the height padding to be the same, as opposed to the regular 2:3 ratio. This is useful when a button only has an icon or single letter and you prefer the button to be a circle. |
| `.js-padeLoad` | Triggers a loading animation on the button once pressed. This is useful when a button triggers a new pade to load. When there is high-latency on the network (usually on mobile devices) it provides the user explicit feedback that an action is currently in progress |

## Support

| Browser | Enhancement |
|---|---|
| IE 5 | Has problems with `is-small` modifier and icons do not display. (Partial support) |
| IE 7 | Icons do not work, can be used as long as icons always have supplementary text inside the button. (Partial support) |
| IE 9 | Everything renders as it should, however page transition loading animation does not fire (Base Support) |
| Evergreen browsers | Page transition loading animation fires (Optimal Support) |