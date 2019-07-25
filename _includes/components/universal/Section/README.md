---
title: Section
category: Universal Components
assets: examples
state:
  text: ✘ unstable (purple bevel added)
  color: black
  background: yellow
API:
  text: HTML
  color: black
  background: '#CCCCCC'
support:
  text: IE 7
  color: white
  background: grey
---

## Table of Contents
- [Overview](#overview)
- [Examples](#examples)
- [API](#api)
- [Support](#support)

## Overview

- `Section` should form the backbone of how you seperate groups of content inside the `Page` component.
- By default this component takes on the appearance of a traditional UI card component.
- However, it has the capacity to appear beveled with cards nested in it to either distinguish itself visually (with one card) or create a second level of grouping with multiple cards inside it.
- It is recommended to not nest component directly inside the Page component without having a `Section` component as a middle-man.
- The `Section` component aims to encapsulate itself from the it's parent component (usually the `Page` component), this means that in most cases you will need to add bottom or top margins via utility classes.
- Spacing with utility classes is helpful in circumstances where it would be hard to programatically predict how things should collapse on mobile (specifically with columns and sidebars)._

## Examples

### Basic
<iframe width="100%" height="315" src="basic.html" frameborder="0" allowfullscreen></iframe>
[View Example](basic.html)

<iframe width="100%" height="315" src="code-basic.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-basic.html)

### Grouped
<iframe style="resize: horizontal;" width="100%" height="800" src="grouped.html" frameborder="0" allowfullscreen></iframe>
[View Example](grouped.html)

<iframe width="100%" height="315" src="code-grouped.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-grouped.html)

### Green Bevel
<iframe style="resize: horizontal;" width="100%" height="315" src="green.html" frameborder="0" allowfullscreen></iframe>
[View Example](green.html)

<iframe width="100%" height="315" src="code-green.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-green.html)

### Dark Card
<iframe style="resize: horizontal;" width="100%" height="315" src="dark.html" frameborder="0" allowfullscreen></iframe>
[View Example](dark.html)

<iframe width="100%" height="315" src="code-dark.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-dark.html)

### Clickable
<iframe style="resize: horizontal;" width="100%" height="315" src="clickable.html" frameborder="0" allowfullscreen></iframe>
[View Example](clickable.html)

<iframe width="100%" height="315" src="code-clickable.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-clickable.html)

### Invisible Card
<iframe style="resize: horizontal;" width="100%" height="315" src="invisible.html" frameborder="0" allowfullscreen></iframe>
[View Example](invisible.html)

<iframe width="100%" height="315" src="code-invisible.html" frameborder="0" allowfullscreen></iframe>
[View Code](code-invisible.html)

## API

### HTML via CSS classes

#### `.Section`
| Modifier | Description |
|---|---|
| `.is-bevel` | Creates the grey bevel effect that forms the base on which additional cards rest. However can also be used without cards if you want to add supplementary information with little visual weight |
| `.is-green` | Should only be used in conjunction with `.is-bevel`, turns the bevel green. Is used for primary call to action cards   |
| `.is-invisible` | Hides all styling associated with the component, but preserves padding. This is usefull to ensure that content lines up with cards around it, even when you want the content to appear 'outside' the cards structure |
| `.is-link` | Displays pointer cursor and darkens the component by 10% when mouse if hovered over it, this provides the visual feedback that the card is a clickable link. It is usually a good idea to include some underline text inside the component to further indicate this. Automatically darkens all children nested inside section as well.

#### `.Section-card`
| Modifier | Description |
|---|---|
| `.is-dark` | Changes the background to dark grey and the text color to white. This is an alternative way of indicating a call of action. This is usually used as a secondary call to action alongside the main green bordered `Section` call to action. |
| `.is-invisible` | Hides all styling associated with the component, but preserves padding. This is useful when you want the title to be inside the bevel or you want to add supplimentary content inside the bevel after the cards |

#### `.Section-title`
| Modifier | Description |
|---|---|
| `.is-small` | Changes the text size from the default `16px` to `14px`, this is usefully when you want to have nested titles in the content underneath the primary title |

## Support

| Browser | Enhancement |
|---|---|
| IE 5 | Has problems with `is-dark` modifier. (Partial support) |
| IE 7 | Acceptable rendition of component, renders mobile version. (Base Support) |
| IE 9 | Rounded `border-radius`, `box-shadows` and additional spacing triggers due media query support (Optimal Support) |